# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to generate the Summer Resiliency Graphs.

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

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot locate the specified file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple("Filepaths", ["sql", "graphs"])
Record = namedtuple("Record", ["Date", "Value", "Zone"])


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
        os.mkdir(target_graphs_dir)

    return Filepaths(results_sql_file, target_graphs_dir)


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


def create_line_plot_figure(
    _df: pd.DataFrame,
    _title: str,
    _horizontal_lines: list[float] | None = None,
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
        fig.add_trace(
            go.Scatter(x=zone_data["Date"], y=zone_data["Value"], mode="lines", name=zone_name)
        )

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


def df_in_kWh(_data: list[Record]) -> pd.DataFrame:
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


if __name__ == "__main__":
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    print("- " * 50)
    print(f"\t>> Using Python: {sys.version}")
    print(f"\t>> Running the script: '{__file__.split('/')[-1]}'")
    print(f"\t>> With the arguments:")
    print("\n".join([f"\t\t{i} | {a}" for i, a in enumerate(sys.argv)]))
    print("\t>> Resolving file paths...")
    file_paths = resolve_paths(sys.argv)
    print(f"\t>> Source SQL File: '{file_paths.sql}'")
    print(f"\t>> Target Output Folder: '{file_paths.graphs}'")

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Get all the data from the SQL File
    env_drybulb_C = get_time_series_data(file_paths.sql, "Site Outdoor Air Drybulb Temperature")
    env_RH = get_time_series_data(file_paths.sql, "Site Outdoor Air Relative Humidity")
    env_wind_speed_m3s = get_time_series_data(file_paths.sql, "Site Wind Speed")
    env_air_pressure_Pa = get_time_series_data(file_paths.sql, "Site Outdoor Air Barometric Pressure")
    drybulb_C = get_time_series_data(file_paths.sql, "Zone Mean Air Temperature")
    zone_RH = get_time_series_data(file_paths.sql, "Zone Air Relative Humidity")
    heat_index = get_time_series_data(file_paths.sql, "Zone Heat Index")
    vent_infiltration_m3s = get_time_series_data(file_paths.sql, "Zone Infiltration Current Density Volume Flow Rate")
    vent_mech_m3s = get_time_series_data(file_paths.sql, "Zone Mechanical Ventilation Current Density Volume Flow Rate")
    vent_zone_m3s = get_time_series_data(file_paths.sql, "Zone Ventilation Current Density Volume Flow Rate")
    vent_infiltration_ach = get_time_series_data(file_paths.sql, "Zone Infiltration Air Change Rate")
    vent_mech_ach = get_time_series_data(file_paths.sql, "Zone Mechanical Ventilation Air Changes per Hour")
    vent_zone_ach = get_time_series_data(file_paths.sql, "Zone Ventilation Air Change Rate")
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
    total_J_vent_gain = get_time_series_data(file_paths.sql, "Zone Ventilation Total Heat Loss Energy")
    total_J_vent_loss = get_time_series_data(file_paths.sql, "Zone Ventilation Total Heat Gain Energy")

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Outdoor Environment Plots
    env_fig1 = create_line_plot_figure(pd.DataFrame(env_drybulb_C), "Outdoor Air Dry-Bulb Temp. [C]")
    env_fig2 = create_line_plot_figure(pd.DataFrame(env_RH), "Outdoor Air Relative Humidity [%]")
    env_fig3 = create_line_plot_figure(pd.DataFrame(env_wind_speed_m3s), "Outdoor Wind Speed [m/s]")
    env_fig4 = create_line_plot_figure(pd.DataFrame(env_air_pressure_Pa), "Outdoor Air Pressure [Pa]")

    with open(html_file(file_paths.graphs / "summer_outdoor_environment.html"), "w") as f:
        f.write(pio.to_html(env_fig1, full_html=False, include_plotlyjs="cdn", div_id="env_fig1"))
        f.write(pio.to_html(env_fig2, full_html=False, include_plotlyjs=False, div_id="env_fig2"))
        f.write(pio.to_html(env_fig3, full_html=False, include_plotlyjs=False, div_id="env_fig3"))
        f.write(pio.to_html(env_fig4, full_html=False, include_plotlyjs=False, div_id="env_fig4"))

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Heat Index Plots
    hi_df = pd.DataFrame(heat_index)
    hi_fig1 = create_line_plot_figure(hi_df, "Zone Heat Index [C]", [26.7, 32.2, 39.4, 51.7])
    hi_fig1.add_annotation(
        x=hi_df["Date"].min(),
        y=26.7 + 2,
        showarrow=False,
        text="Caution",
        xanchor="left",
    )
    hi_fig1.add_annotation(
        x=hi_df["Date"].min(),
        y=32.2 + 2,
        showarrow=False,
        text="Warning",
        xanchor="left",
    )
    hi_fig1.add_annotation(
        x=hi_df["Date"].min(),
        y=39.4 + 2,
        showarrow=False,
        text="Danger",
        xanchor="left",
    )
    hi_fig1.add_annotation(
        x=hi_df["Date"].min(),
        y=51.7 + 2,
        showarrow=False,
        text="Extreme Danger",
        xanchor="left",
    )

    hi_fig2 = create_line_plot_figure(pd.DataFrame(drybulb_C + env_drybulb_C), "Zone Dry-Bulb Air Temp. [C]")
    hi_fig3 = create_line_plot_figure(pd.DataFrame(zone_RH + env_RH), "Zone Air Relative Humidity [%]")

    with open(html_file(file_paths.graphs / "summer_heat_index.html"), "w") as f:
        f.write(pio.to_html(hi_fig1, full_html=False, include_plotlyjs="cdn", div_id="hi_fig1"))
        f.write(pio.to_html(hi_fig2, full_html=False, include_plotlyjs=False, div_id="hi_fig2"))
        f.write(pio.to_html(hi_fig3, full_html=False, include_plotlyjs=False, div_id="hi_fig3"))

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Ventilation Plots
    # vent_fig1 = create_line_plot_figure(df_in_m3hr(vent_infiltration_m3s), "Zone Envelope Infiltration [m3/hr]")
    # vent_fig2 = create_line_plot_figure(df_in_m3hr(vent_zone_m3s), "Zone Ventilation [m3/hr]")
    # vent_fig3 = create_line_plot_figure(df_in_m3hr(vent_mech_m3s), "Zone Mechanical Ventilation [m3/hr]")

    vent_fig1 = create_line_plot_figure(pd.DataFrame(vent_infiltration_ach), "Zone Infiltration [ACH]")
    vent_fig2 = create_line_plot_figure(pd.DataFrame(vent_zone_ach), "Zone Ventilation [ACH]")
    vent_fig3 = create_line_plot_figure(pd.DataFrame(vent_mech_ach), "Zone Mechanical Ventilation [ACH]")

    with open(html_file(file_paths.graphs / "summer_ventilation.html"), "w") as f:
        f.write(pio.to_html(vent_fig1, full_html=False, include_plotlyjs="cdn", div_id="vent_fig1"), )
        f.write(pio.to_html(vent_fig2, full_html=False, include_plotlyjs=False, div_id="vent_fig2"), )
        f.write(pio.to_html(vent_fig3, full_html=False, include_plotlyjs=False, div_id="vent_fig3"), )

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -- Energy Flow Plots
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

    with open(html_file(file_paths.graphs / "summer_energy_flow.html"), "w") as f:
        f.write(pio.to_html(energy_fig1, full_html=False, include_plotlyjs="cdn", div_id="energy_fig1"))
        f.write(pio.to_html(energy_fig2, full_html=False, include_plotlyjs=False, div_id="energy_fig2"))
        f.write(pio.to_html(energy_fig3, full_html=False, include_plotlyjs=False, div_id="energy_fig3"))
        f.write(pio.to_html(energy_fig4, full_html=False, include_plotlyjs=False, div_id="energy_fig4"))
        f.write(pio.to_html(energy_fig5, full_html=False, include_plotlyjs=False, div_id="energy_fig5"))
        f.write(pio.to_html(energy_fig6, full_html=False, include_plotlyjs=False, div_id="energy_fig6"))
        f.write(pio.to_html(energy_fig7, full_html=False, include_plotlyjs=False, div_id="energy_fig7"))
