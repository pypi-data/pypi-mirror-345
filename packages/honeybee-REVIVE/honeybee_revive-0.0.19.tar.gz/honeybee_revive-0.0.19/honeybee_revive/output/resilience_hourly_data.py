# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to get the Resilience-sim hourly values from an EnergyPlus SQL file and write to JSON & CSV.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The path to the EnergyPlus SQL file to read in.
    * [2] (str): The path to the output JSON file to write the data to.
    * [3] (str): The output variable name to read from the SQL file.
"""

import os
import sqlite3
import sys
from collections import namedtuple
from pathlib import Path

import pandas as pd


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot locate the specified file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple("Filepaths", ["sql", "json_filepath"])
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

    assert len(_args) == 4, "Error: Incorrect number of arguments."

    # -----------------------------------------------------------------------------------
    # -- The EnergyPlus SQL input file.
    results_sql_file = Path(_args[1])
    if not results_sql_file.exists():
        raise InputFileError(results_sql_file)

    # -----------------------------------------------------------------------------------
    # -- JSON File paths:
    json_filepath = Path(_args[2])
    if json_filepath.exists():
        print(f"\t>> Removing the file: {json_filepath}")
        os.remove(json_filepath)

    return Filepaths(results_sql_file, json_filepath)


def get_time_series_data(source_file_path: Path, output_variable_name: str) -> list[Record]:
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
            (output_variable_name,),
        )
        for row in c.fetchall():
            date = pd.to_datetime(f"2016-{row[1]}-{row[2]} {row[3]-1}:00:00", utc=True)
            data_.append(Record(date, row[4], row[0]))
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


def pivot_df_by_zone_name(_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot the DataFrame so the columns are the Zone names."""
    pivot_df = _df.pivot(index="Date", columns="Zone", values="Value")
    pivot_df.reset_index(inplace=True)
    return pivot_df


if __name__ == "__main__":
    print("- " * 100)
    print(f"\t>> Using Python: {sys.version}")
    print(f"\t>> Running the script: '{__file__.split('/')[-1]}'")
    print(f"\t>> With the arguments:")
    print("\n".join([f"\t\t{i} | {a}" for i, a in enumerate(sys.argv)]))

    # -------------------------------------------------------------------------
    # --- Input / Output file Path
    print("\t>> Resolving file paths...")
    file_paths = resolve_paths(sys.argv)
    print(f"\t>> Source SQL File: '{file_paths.sql}'")
    print(f"\t>> JSON Data File: '{file_paths.json_filepath}'")
    output_variable_name = sys.argv[3]

    # -------------------------------------------------------------------------
    # -- Get the Hourly Data from the SQL File, output it to a JSON file.
    set_temps = get_time_series_data(file_paths.sql, output_variable_name)
    set_df = pd.DataFrame(set_temps)
    set_df.to_json(file_paths.json_filepath, orient="records")
    set_df = pivot_df_by_zone_name(set_df)
    set_df.to_csv(file_paths.json_filepath.with_suffix(".csv"), index=False)
