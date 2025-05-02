# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility function to load HB-E-Program Objects from a JSON file."""

import json
import os

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_revive_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive_standards:\n\t{}".format(e))


def is_program(_json_object):
    # type: (dict) -> bool
    """Check if a JSON object is a valid 'ProgramTypeAbridged' dict."""
    if "type" not in _json_object:
        return False
    if not _json_object["type"] == "ProgramTypeAbridged":
        return False
    return True


def load_programs_from_json_file(_programs_filepath, _schedules_filepath="", _schedules_dict=None):
    # type: (str, str, dict[str, ScheduleRuleset] | None) -> dict[str, ProgramType]
    """Load a set of HBE-ScheduleRuleset object from a JSON file."""
    if not os.path.exists(_programs_filepath):
        raise ValueError("File not found: {}".format(_programs_filepath))

    if not _schedules_dict:
        _schedules_dict = load_schedules_from_json_file(_schedules_filepath)

    with open(_programs_filepath, "r") as json_file:
        all_programs = (
            ProgramType.from_dict_abridged(d, _schedules_dict) for d in json.load(json_file) if is_program(d)
        )
        return {_.identifier: _ for _ in all_programs}
