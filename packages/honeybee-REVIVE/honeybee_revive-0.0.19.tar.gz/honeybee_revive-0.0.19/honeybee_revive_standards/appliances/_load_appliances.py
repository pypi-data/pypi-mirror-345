# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility function to load Appliance (HB-E Process) Objects from a JSON file."""

import json
import os

try:
    from honeybee_energy.load.process import Process
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_revive_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_standards:\n\t{}".format(e))


def is_abridged_process(_json_object):
    # type: (dict) -> bool
    """Check if a JSON object is a valid 'ProcessAbridged' dict."""
    if "type" not in _json_object:
        return False
    if not _json_object["type"] == "ProcessAbridged":
        return False
    return True


def load_abridged_appliances_from_json_file(_appliance_filepath, _schedules_filepath="", _schedules_dict=None):
    # type: (str, str, dict[str, ScheduleRuleset] | None) -> dict[str, Process]
    """Load a HBE-Process object from a JSON file.

    Args:
        _appliance_filepath: Full path to the JSON file containing the appliances.
        _schedules_filepath: An optional full path to the JSON file containing the schedules.
        _schedules_dict: An optional dictionary of ScheduleRuleset objects to use for the appliances.
    Returns:
        A dictionary of Process objects (Appliances) keyed by their display name.
    """

    # -- Load the Schedules from a JSON file, if a dict of schedules is not provided.
    if not _schedules_dict:
        _schedules_dict = load_schedules_from_json_file(_schedules_filepath)

    # -- Check if the file exists
    if not os.path.exists(_appliance_filepath):
        raise ValueError("File not found: {}".format(_appliance_filepath))

    with open(_appliance_filepath, "r") as json_file:
        all_measures = (
            Process.from_dict_abridged(d, _schedules_dict) for d in json.load(json_file) if is_abridged_process(d)
        )
        return {_.display_name: _ for _ in all_measures}
