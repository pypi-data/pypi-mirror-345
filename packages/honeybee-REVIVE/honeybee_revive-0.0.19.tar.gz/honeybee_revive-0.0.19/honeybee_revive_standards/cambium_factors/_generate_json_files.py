# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Utility functions used to generate the Cambium Factors by Region JSON-Files."""

import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

region_data_dicts: list[dict] = [
    {"code": "AZNMc", "name": "WECC Southwest", "description": "Southwest US"},
    {"code": "CAMXc", "name": "WECC California", "description": "Southwest Coast/Most of California"},
    {"code": "ERCTc", "name": "ERCOT All", "description": "Most of Texas"},
    {"code": "FRCCc", "name": "FRCC All", "description": "Most of Florida"},
    {"code": "MROEc", "name": "MRO East", "description": "Eastern Wisconsin"},
    {"code": "MROWc", "name": "MRO West", "description": "Upper Midwest"},
    {"code": "NEWEc", "name": "NPCC New England", "description": "New England"},
    {"code": "NWPPc", "name": "WECC Northwest", "description": "Northwest US"},
    {"code": "NYSTc", "name": "New York State", "description": "New York State"},
    {"code": "RFCEc", "name": "RFC East", "description": "Mid Atlantic"},
    {"code": "RFCMc", "name": "RFC Michigan", "description": "Most of Michigan"},
    {"code": "RFCWc", "name": "RFC West", "description": "Ohio Valley"},
    {"code": "RMPAc", "name": "WECC Rockies", "description": "Colorado-Eastern Wyoming"},
    {"code": "SPNOc", "name": "SPP North", "description": "Kansas-Western Missouri"},
    {"code": "SPSOc", "name": "SPP South", "description": "Texas Panhandle-Oklahoma"},
    {"code": "SRMVc", "name": "SERC Mississippi Valley", "description": "Lower Mississippi Valley"},
    {"code": "SRMWc", "name": "SERC Midwest", "description": "Middle Mississippi Valley"},
    {"code": "SRSOc", "name": "SERC South", "description": "Southeast US, Gulf Coast"},
    {"code": "SRTVc", "name": "SERC Tennessee Valley", "description": "Tennessee Valley"},
    {"code": "SRVCc", "name": "SERC Virginia/Carolina", "description": "Virginia/Carolinas"},
]


class GridRegion(BaseModel):
    region_code: str
    region_name: str
    description: str
    hourly_CO2_factors: defaultdict[int, list[float]] = Field(default_factory=lambda: defaultdict(list))


# -- Setup the region objects....
regions: dict[str, GridRegion] = dict()
for region_data_dict in region_data_dicts:
    regions[region_data_dict["code"]] = GridRegion(
        region_code=region_data_dict["code"],
        region_name=region_data_dict["name"],
        description=region_data_dict["description"],
    )

# -- The original Cambium files (by year)...
_src_cambium_file_path = Path("/Users/em/Desktop/REVIVE/REVIVE_repo/REVIVE2024/Databases/CambiumFactors")
for filename in sorted(os.listdir(_src_cambium_file_path)):
    filename = Path(filename)

    if filename.suffix != ".csv":
        continue

    year = filename.stem  # Thanks Al...

    hourlyBAEmissions = pd.read_csv(os.path.join(_src_cambium_file_path, filename))
    hourlyBAEmissions = hourlyBAEmissions.drop(hourlyBAEmissions.columns[0], axis=1)

    for region_name in hourlyBAEmissions.columns:  # grid-regions....
        region_hourly_data = list(hourlyBAEmissions[region_name])
        regions[region_name].hourly_CO2_factors[int(year)] = region_hourly_data


# -- Create the new (by region) JSON files
for _ in list(regions.values()):
    # Write the factor to file
    target_dir = Path(
        "/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_REVIVE/honeybee_revive_standards/cambium_factors"
    )
    target_file = target_dir / f"{_.region_code}.json"
    with open(target_file, "w") as f:
        f.write(_.json())
