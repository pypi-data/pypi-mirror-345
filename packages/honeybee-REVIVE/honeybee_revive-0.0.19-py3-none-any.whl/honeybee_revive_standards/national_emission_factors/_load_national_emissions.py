# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility function to load NationalEmissionsFactor data from a JSON file."""

import json
import os

try:
    from honeybee_revive.national_emissions import NationalEmissionsFactors
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))


def is_national_emissions(_json_object):
    # type: (dict) -> bool
    """Check if a JSON object is a valid 'NationalEmissionsFactors' dict."""
    if "type" not in _json_object:
        return False
    if not _json_object["type"] == "NationalEmissionsFactors":
        return False
    return True


def load_national_emissions_from_json_file(_filepath):
    # type: (str) -> dict[str, NationalEmissionsFactors]
    """Load a NationalEmissionsFactors object from a JSON file."""
    if not os.path.isfile(_filepath):
        raise ValueError("File does not exist: {}".format(_filepath))

    with open(_filepath, "r") as json_file:
        all_emissions = (
            NationalEmissionsFactors.from_dict(d) for d in json.load(json_file) if is_national_emissions(d)
        )
        return {_.country_name: _ for _ in all_emissions}
