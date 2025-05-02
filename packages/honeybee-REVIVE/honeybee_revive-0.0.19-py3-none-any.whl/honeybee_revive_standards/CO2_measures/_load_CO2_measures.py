# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility function to load CO2ReductionMeasure data from a JSON file."""

import json
import os

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasure
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))


def is_CO2_measure(_json_object):
    # type: (dict) -> bool
    """Check if a JSON object is a valid 'CO2ReductionMeasure' dict."""
    if "type" not in _json_object:
        return False
    if not _json_object["type"] == "CO2ReductionMeasure":
        return False
    return True


def load_CO2_measures_from_json_file(_filepath):
    # type: (str) -> dict[str, CO2ReductionMeasure]
    """Load a NationalEmissionsFactors object from a JSON file."""
    if not os.path.exists(_filepath):
        raise ValueError("File not found: {}".format(_filepath))

    with open(_filepath, "r") as json_file:
        all_measures = (CO2ReductionMeasure.from_dict(d) for d in json.load(json_file) if is_CO2_measure(d))
        return {_.name: _ for _ in all_measures}
