# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility function to load Cambium GridRegion Data from a JSON file."""

import json
import os

try:
    from honeybee_revive.grid_region import GridRegion
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))


def load_grid_region_from_json_file(_filepath):
    # type: (str) -> GridRegion
    """Load a GridRegion object from a JSON file."""
    if not os.path.isfile(_filepath):
        raise ValueError("File does not exist: {}".format(_filepath))

    with open(_filepath, "r") as f:
        data = json.load(f)

    return GridRegion(
        data["region_name"],
        data["region_code"],
        data["description"],
        _filepath,
    )
