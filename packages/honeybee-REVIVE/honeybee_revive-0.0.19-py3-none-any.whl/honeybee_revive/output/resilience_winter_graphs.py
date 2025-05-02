# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to generate the Winter Resiliency Graphs.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The path to the EnergyPlus SQL file to read in.
    * [2] (str): The path to the output folder for the graphs.
"""

import os
import sqlite3
import sys
from collections import namedtuple
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot locate the specified file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple("Filepaths", ["sql", "graphs"])
Record = namedtuple("Record", ["Date", "Value", "Zone"])
Surface = namedtuple(
    "Surface",
    ["Name", "Class", "Area", "GrossArea", "Tilt", "ZoneIndex", "SurfaceIndex", "ExtBoundCond", "ConstructionIndex"],
)
Construction = namedtuple("Construction", ["ConstructionIndex", "Name", "UValue"])


def resolve_paths(_args: list[str]) -> Filepaths:
    """Sort out the file input and output paths. Make the output directory if needed.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Filepaths
    """

    assert len(_args) == 3, "Error: Incorrect number of arguments."

    # -----------------------------------------------------------------------------------
    # -- The EnergyPlus SQL input file.
    results_sql_file = Path(_args[1])
    if not results_sql_file.exists():
        raise InputFileError(results_sql_file)

    # -----------------------------------------------------------------------------------
    # -- Preview-Tables output folder:
    target_graphs_dir = Path(_args[2])
    if not target_graphs_dir.exists():
        print(f"\t>> Creating the directory: {target_graphs_dir}")
    os.makedirs(target_graphs_dir, exist_ok=True)

    return Filepaths(results_sql_file, target_graphs_dir)


def get_constructions(source_file_path: Path) -> dict[int, Construction]:
    conn = sqlite3.connect(source_file_path)
    data_ = {}
    try:
        c = conn.cursor()
        c.execute("SELECT ConstructionIndex, Name, UValue FROM 'Constructions'")
        for row in c.fetchall():
            c = Construction(*row)
            data_[c.ConstructionIndex] = c
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


def get_time_series_data(source_file_path: Path, output_variable: str) -> list[Record]:
    """Get Time-Series data from the SQL File."""
    conn = sqlite3.connect(source_file_path)
    data_ = []  # defaultdict(list)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT KeyValue, Month, Day, Hour, Value FROM 'ReportVariableWithTime' "
            "WHERE Name=? "
            "AND DayType NOT IN ('WinterDesignDay', 'SummerDesignDay') "
            "ORDER BY Month, Day, Hour",
            (output_variable,),
        )
        for row in c.fetchall():
            date = pd.to_datetime(f"2021-{row[1]}-{row[2]} {row[3]-1}:00:00")
            data_.append(Record(date, row[4], row[0]))
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


def get_surface_data(source_file_path: Path) -> list[Surface]:
    conn = sqlite3.connect(source_file_path)
    data_ = []  # defaultdict(list)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT SurfaceName, ClassName, Area, GrossArea, Tilt, ZoneIndex, SurfaceIndex, ExtBoundCond, ConstructionIndex FROM 'Surfaces' "
        )
        for row in c.fetchall():
            data_.append(Surface(*row))
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


def create_line_plot_figure(
    _df: pd.DataFrame,
    _title: str,
    _horizontal_lines: list[float] | None = None,
    _stack: bool = False,
) -> go.Figure:
    """Create a line plot figure from the DataFrame."""

    fig = go.Figure()
    fig.update_layout(
        title=_title,
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the entire figure
        #plot_bgcolor='rgba(0,0,0,0)'   # Transparent background for the plotting area
    )


    if _df.empty:
        return fig

    for zone_name in _df["Zone"].unique():
        zone_data = _df[_df["Zone"] == zone_name]
        if _stack:
            fig.add_trace(
                go.Scatter(x=zone_data["Date"], y=zone_data["Value"], mode="lines", stackgroup="one", name=zone_name)
            )
        else:
            fig.add_trace(go.Scatter(x=zone_data["Date"], y=zone_data["Value"], mode="lines", name=zone_name))

    if _horizontal_lines:
        for line in _horizontal_lines:
            fig.add_shape(
                type="line",
                x0=_df["Date"].min(),  # Start of the line (minimum date)
                x1=_df["Date"].max(),  # End of the line (maximum date)
                y0=line,  # Y-coordinate of the line
                y1=line,  # Y-coordinate of the line
                line=dict(color="Red", width=2, dash="dash"),  # Line style
            )

    return fig


def df_in_m3hr(_data: list[Record]) -> pd.DataFrame:
    """Convert the data from m3/s to m3/hr."""

    df = pd.DataFrame(_data)
    if not df.empty:
        df["Value"] = df["Value"].apply(lambda _: _ * 3600)
    return df


def df_in_kWh(_data: Iterable[Record]) -> pd.DataFrame:
    """Convert the data from J to kWh."""

    df = pd.DataFrame(_data)
    if not df.empty:
        df["Value"] = df["Value"].apply(lambda _: _ * 0.000000277778)
    return df


def html_file(_filename: Path) -> Path:
    """Create an HTML file, but remove it if it already exists."""

    if os.path.exists(_filename):
        os.remove(_filename)
    return _filename


def surface_df_by_construction(
    _records: list[Record],
    _constructions: dict[int, Construction],
    _surfaces_df: pd.DataFrame,
    _exterior_surface_names: set[str],
) -> pd.DataFrame:
    """Get the surface data as a DataFrame, merged by the construction type."""

    ext_surfaces = (r for r in _records if r.Zone in _exterior_surface_names)
    surface_conductance_df = df_in_kWh(ext_surfaces)
    """
    print(f"{surface_conductance_df=}")
    Date                   Value        Zone
    0 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE1
    1 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE2
    2 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE3
    ....
    """

    """
    print(_surface_df)
    Name    Class   Area    GrossArea   Tilt    ZoneIndex   SurfaceIndex    ExtBoundCond    ConstructionIndex
    0_LOWER_C99DFGH..FACE1 Wall    0.000000    0.000000    90.000000   0   0   0   0
    0_LOWER_C99DFGH..FACE2 Wall    0.000000    0.000000    90.000000   0   1   0   0
    0_LOWER_C99DFGH..FACE3 Wall    0.000000    0.000000    90.000000   0   2   0   0
    ....
    """
    
    # Add the ConstructionIndex to each record in the surface_conductance_df
    # surface_conductance_df["ConstructionIndex"] = surface_conductance_df["Zone"].apply(
    #     lambda x: _surfaces_df.loc[_surfaces_df["Name"] == x, "ConstructionIndex"].values[0]
    # )
    # """
    # Date                   Value        Zone                    ConstructionIndex
    # 0 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE1  0
    # 1 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE2  0
    # 2 2021-01-01 00:00:00  0.000000     0_LOWER_C99DFGH..FACE3  0
    # ....
    # """

    # # Merge the 'Value's for each Record, by 'Date' and by the 'ConstructionIndex'
    # surface_conductance_df = surface_conductance_df.groupby(["Date", "ConstructionIndex"])["Value"].sum().reset_index()

    # # re-set the ConstructionIndex (int) to the Construction Name
    # surface_conductance_df["ConstructionIndex"] = surface_conductance_df["ConstructionIndex"].apply(
    #     lambda x: _constructions[x].Name
    # )

    # # re-name 'ConstructionIndex' to 'Zone' for plotting
    # surface_conductance_df.rename(columns={"ConstructionIndex": "Zone"}, inplace=True)
    return surface_conductance_df


def rename_set_temps(_data: list[Record]) -> list[Record]:
    """Rename the SET temperature Zones.

    For some reason, when pulling SET temps from the SQL file, the Zone names come in as the 
    identifier of the Honeybee-Room's Honeybee-Energy-People object. ie: 'FLOOR-0_SPACE RV2024_RESILIENCE_PEOPLE' 
    Shrug. So try and break off the first part of the string and use that as the Zone Name for plotting.
    """
    for i, r in enumerate(_data):
        name_parts = str(r.Zone).split('_SPACE RV2024_')
        _data[i] = Record(r.Date, r.Value, name_parts[0])
    return _data


def write_outdoor_environment_plots(_file_paths: Filepaths) -> None:
    env_drybulb_C = get_time_series_data(_file_paths.sql, "Site Outdoor Air Drybulb Temperature")
    env_RH = get_time_series_data(_file_paths.sql, "Site Outdoor Air Relative Humidity")
    env_wind_speed_m3s = get_time_series_data(_file_paths.sql, "Site Wind Speed")
    env_air_pressure_Pa = get_time_series_data(_file_paths.sql, "Site Outdoor Air Barometric Pressure")

    env_fig1 = create_line_plot_figure(pd.DataFrame(env_drybulb_C), "Outdoor Air Dry-Bulb Temp. [C]")
    env_fig2 = create_line_plot_figure(pd.DataFrame(env_RH), "Outdoor Air Relative Humidity [%]")
    env_fig3 = create_line_plot_figure(pd.DataFrame(env_wind_speed_m3s), "Outdoor Wind Speed [m/s]")
    env_fig4 = create_line_plot_figure(pd.DataFrame(env_air_pressure_Pa), "Outdoor Air Pressure [Pa]")
    env_fig4 = create_line_plot_figure(pd.DataFrame(env_air_pressure_Pa), "Outdoor Air Pressure [Pa]")

    with open(html_file(_file_paths.graphs / "winter_outdoor_environment.html"), "w+") as f:
        f.write(pio.to_html(env_fig1, full_html=False, include_plotlyjs="cdn", div_id="env_fig1"))
        f.write(pio.to_html(env_fig2, full_html=False, include_plotlyjs=False, div_id="env_fig2"))
        f.write(pio.to_html(env_fig3, full_html=False, include_plotlyjs=False, div_id="env_fig3"))
        f.write(pio.to_html(env_fig4, full_html=False, include_plotlyjs=False, div_id="env_fig4"))


def write_ventilation_plots(_file_paths: Filepaths) -> None:
    vent_infiltration_ach = get_time_series_data(_file_paths.sql, "Zone Infiltration Air Change Rate")
    vent_mech_ach = get_time_series_data(_file_paths.sql, "Zone Mechanical Ventilation Air Changes per Hour")
    vent_zone_ach = get_time_series_data(_file_paths.sql, "Zone Ventilation Air Change Rate")
    vent_infiltration_m3s = get_time_series_data(file_paths.sql, "Zone Infiltration Current Density Volume Flow Rate")
    vent_mech_m3s = get_time_series_data(file_paths.sql, "Zone Mechanical Ventilation Current Density Volume Flow Rate")
    vent_zone_m3s = get_time_series_data(file_paths.sql, "Zone Ventilation Current Density Volume Flow Rate")

    vent_fig1 = create_line_plot_figure(pd.DataFrame(vent_infiltration_ach), "Zone Envelope Infiltration [ACH]")
    vent_fig2 = create_line_plot_figure(pd.DataFrame(vent_zone_ach), "Zone Ventilation [ACH]")
    vent_fig3 = create_line_plot_figure(pd.DataFrame(vent_mech_ach), "Zone Mechanical Ventilation [ACH]")

    with open(html_file(_file_paths.graphs / "winter_ventilation.html"), "w") as f:
        f.write(pio.to_html(vent_fig1, full_html=False, include_plotlyjs="cdn", div_id="vent_fig1"))
        f.write(pio.to_html(vent_fig2, full_html=False, include_plotlyjs=False, div_id="vent_fig2"))
        f.write(pio.to_html(vent_fig3, full_html=False, include_plotlyjs=False, div_id="vent_fig3"))


def write_SET_temp_plots(_file_paths: Filepaths) -> None:
    drybulb_C = get_time_series_data(file_paths.sql, "Zone Mean Air Temperature")
    zone_RH = get_time_series_data(file_paths.sql, "Zone Air Relative Humidity")
    set_temps = rename_set_temps(get_time_series_data(file_paths.sql, "Zone Thermal Comfort Pierce Model Standard Effective Temperature"))
    env_drybulb_C = get_time_series_data(_file_paths.sql, "Site Outdoor Air Drybulb Temperature")
    env_RH = get_time_series_data(_file_paths.sql, "Site Outdoor Air Relative Humidity")
    
    set_fig1 = create_line_plot_figure(pd.DataFrame(set_temps), "Zone SET Temperature [C]", [12.22])
    set_fig2 = create_line_plot_figure(pd.DataFrame(drybulb_C + env_drybulb_C), "Dry-Bulb Air Temperature [C]")
    set_fig3 = create_line_plot_figure(pd.DataFrame(zone_RH + env_RH), "Air Relative Humidity [%]")

    with open(html_file(_file_paths.graphs / "winter_SET_temperature.html"), "w") as f:
        f.write(pio.to_html(set_fig1, full_html=False, include_plotlyjs="cdn", div_id="set_fig1"))
        f.write(pio.to_html(set_fig2, full_html=False, include_plotlyjs=False, div_id="set_fig2"))
        f.write(pio.to_html(set_fig3, full_html=False, include_plotlyjs=False, div_id="set_fig3"))


def write_energy_flow_plots(file_paths: Filepaths) -> None:
    total_J_people = get_time_series_data(file_paths.sql, "Zone People Total Heating Energy")
    total_J_lights = get_time_series_data(file_paths.sql, "Zone Lights Total Heating Energy")
    total_J_elec_equip = get_time_series_data(file_paths.sql, "Zone Electric Equipment Total Heating Energy")
    total_J_win_gain = get_time_series_data(file_paths.sql, "Zone Windows Total Heat Gain Energy")
    total_J_solar_gain = get_time_series_data(file_paths.sql, "Zone Windows Total Transmitted Solar Radiation Energy")
    total_J_solar_direct_gain = get_time_series_data(
        file_paths.sql, "Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy"
    )
    total_J_solar_diffuse_gain = get_time_series_data(
        file_paths.sql, "Zone Exterior Windows Total Transmitted Diffuse Solar Radiation Energy"
    )
    total_J_win_loss = get_time_series_data(file_paths.sql, "Zone Windows Total Heat Loss Energy")
    total_J_infiltration_gain = get_time_series_data(file_paths.sql, "Zone Infiltration Total Heat Gain Energy")
    total_J_infiltration_loss = get_time_series_data(file_paths.sql, "Zone Infiltration Total Heat Loss Energy")
    total_J_vent_gain = get_time_series_data(file_paths.sql, "Zone Ventilation Total Heat Gain Energy")
    total_J_vent_loss = get_time_series_data(file_paths.sql, "Zone Ventilation Total Heat Loss Energy")

    # -- 
    energy_fig1 = create_line_plot_figure(df_in_kWh(total_J_people), "Total People Energy [kWh]")
    energy_fig2 = create_line_plot_figure(df_in_kWh(total_J_lights), "Total Lighting Energy [kWh]")
    energy_fig3 = create_line_plot_figure(df_in_kWh(total_J_elec_equip), "Total Elec. Equipment Energy [kWh]")

    win_gain_df = df_in_kWh(total_J_win_gain)
    win_loss_df = df_in_kWh(total_J_win_loss)
    win_gain_df["Value"] = win_gain_df["Value"] - win_loss_df["Value"]
    energy_fig4 = create_line_plot_figure(win_gain_df, "Total Window Heat Gain [kWh]")

    solar_beam_df = df_in_kWh(total_J_solar_direct_gain)
    solar_diffuse_df = df_in_kWh(total_J_solar_diffuse_gain)
    solar_beam_df["Value"] = solar_beam_df["Value"] + solar_diffuse_df["Value"]
    energy_fig5 = create_line_plot_figure(solar_beam_df, "Total (Beam + Diffuse) Window Solar Heat Gain [kWh]")

    infiltration_gain_df = df_in_kWh(total_J_infiltration_gain)
    infiltration_loss_df = df_in_kWh(total_J_infiltration_loss)
    infiltration_gain_df["Value"] = infiltration_gain_df["Value"] - infiltration_loss_df["Value"]
    energy_fig6 = create_line_plot_figure(infiltration_gain_df, "Total Infiltration Heat Gain [kWh]")

    vent_gain_df = df_in_kWh(total_J_vent_gain)
    vent_loss_df = df_in_kWh(total_J_vent_loss)
    if not vent_gain_df.empty and not vent_loss_df.empty:
        vent_gain_df["Value"] = vent_gain_df["Value"] - vent_loss_df["Value"]
    energy_fig7 = create_line_plot_figure(vent_gain_df, "Total Ventilation Heat Gain [kWh]")

    with open(html_file(file_paths.graphs / "winter_energy_flow.html"), "w") as f:
        f.write(pio.to_html(energy_fig1, full_html=False, include_plotlyjs="cdn", div_id="energy_fig1"))
        f.write(pio.to_html(energy_fig2, full_html=False, include_plotlyjs=False, div_id="energy_fig2"))
        f.write(pio.to_html(energy_fig3, full_html=False, include_plotlyjs=False, div_id="energy_fig3"))
        f.write(pio.to_html(energy_fig4, full_html=False, include_plotlyjs=False, div_id="energy_fig4"))
        f.write(pio.to_html(energy_fig5, full_html=False, include_plotlyjs=False, div_id="energy_fig5"))
        f.write(pio.to_html(energy_fig6, full_html=False, include_plotlyjs=False, div_id="energy_fig6"))
        f.write(pio.to_html(energy_fig7, full_html=False, include_plotlyjs=False, div_id="energy_fig7"))


def write_envelope_details_plots(file_paths: Filepaths):
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Get Surface energy data from the SQL file
    srfc_avg_face_conductance = get_time_series_data(
        file_paths.sql, "Surface Average Face Conduction Heat Transfer Energy"
    )
    srfc_win_heat_transfer = get_time_series_data(file_paths.sql, "Surface Window Net Heat Transfer Energy")
    srfc_win_heat_gain = get_time_series_data(file_paths.sql, "Surface Window Heat Gain Energy")
    srfc_win_heat_loss = get_time_series_data(file_paths.sql, "Surface Window Heat Loss Energy")
    srfc_heat_storage = get_time_series_data(file_paths.sql, "Surface Heat Storage Energy")
    srfc_shading_device_on = get_time_series_data(file_paths.sql, "Surface Shading Device Is On Time Fraction")
    srfc_inside_face_temp = get_time_series_data(file_paths.sql, "Surface Inside Face Temperature")
    
    
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Get the Surface level data from the SQL file
    constructions = get_constructions(file_paths.sql)
    surfaces = get_surface_data(file_paths.sql)
    surfaces_df = pd.DataFrame(surfaces)
    exterior_surface_names = {s.Name for s in surfaces if s.ExtBoundCond == 0}

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Create the envelope details plots
    envelope_fig1 = create_line_plot_figure(
        surface_df_by_construction(srfc_avg_face_conductance, constructions, surfaces_df, exterior_surface_names),
        "Surface Average Face Conduction Heat Transfer Energy [kWh]",
        _stack=True,
    )
    envelope_fig2 = create_line_plot_figure(
        surface_df_by_construction(srfc_win_heat_transfer, constructions, surfaces_df, exterior_surface_names),
        "Window Net Heat Transfer Energy [kWh]",
        _stack=True,
    )
    envelope_fig3 = create_line_plot_figure(
        surface_df_by_construction(srfc_win_heat_gain, constructions, surfaces_df, exterior_surface_names),
        "Window Heat Gain Energy [kWh]",
        _stack=True,
    )
    envelope_fig4 = create_line_plot_figure(
        surface_df_by_construction(srfc_win_heat_loss, constructions, surfaces_df, exterior_surface_names),
        "Window Heat Loss Energy [kWh]",
        _stack=True,
    )
    envelope_fig5 = create_line_plot_figure(
        surface_df_by_construction(srfc_heat_storage, constructions, surfaces_df, exterior_surface_names),
        "Heat Storage Energy [kWh]",
        _stack=True,
    )
    envelope_fig6 = create_line_plot_figure(pd.DataFrame(srfc_shading_device_on), "Surface Shading Device On")
    envelope_fig7 = create_line_plot_figure(pd.DataFrame(srfc_inside_face_temp), "Surface Inside Face Temp. [C]")

    with open(html_file(file_paths.graphs / "winter_envelope_details.html"), "w") as f:
        f.write(pio.to_html(envelope_fig1, full_html=False, include_plotlyjs="cdn", div_id="envelope_fig1"))
        f.write(pio.to_html(envelope_fig2, full_html=False, include_plotlyjs=False, div_id="envelope_fig2"))
        f.write(pio.to_html(envelope_fig3, full_html=False, include_plotlyjs=False, div_id="envelope_fig3"))
        f.write(pio.to_html(envelope_fig4, full_html=False, include_plotlyjs=False, div_id="envelope_fig4"))
        f.write(pio.to_html(envelope_fig5, full_html=False, include_plotlyjs=False, div_id="envelope_fig5"))
        f.write(pio.to_html(envelope_fig6, full_html=False, include_plotlyjs=False, div_id="envelope_fig6"))
        f.write(pio.to_html(envelope_fig7, full_html=False, include_plotlyjs=False, div_id="envelope_fig7"))


if __name__ == "__main__":
    # ------------------------------------------------------------------------------------------------------------------
    print("- " * 50)
    print(f"\t>> Using Python: {sys.version}")
    print(f"\t>> Running the script: '{__file__.split('/')[-1]}'")
    print(f"\t>> With the arguments:")
    print("\n".join([f"\t\t{i} | {a}" for i, a in enumerate(sys.argv)]))

    # ------------------------------------------------------------------------------------------------------------------
    # --- Input / Output file Path
    print("\t>> Resolving file paths...")
    file_paths = resolve_paths(sys.argv)
    print(f"\t>> Source SQL File: '{file_paths.sql}'")
    print(f"\t>> Target Output Folder: '{file_paths.graphs}'")

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Generate the Winter Resiliency Graphs
    write_outdoor_environment_plots(file_paths)
    write_SET_temp_plots(file_paths)
    write_ventilation_plots(file_paths)
    write_energy_flow_plots(file_paths)
    # write_envelope_details_plots(file_paths)
