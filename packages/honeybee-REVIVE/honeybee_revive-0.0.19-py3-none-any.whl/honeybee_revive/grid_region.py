# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Model Phius REVIVE Cambium Region Factors.

Note that this object does not store the action factors - just the lookup code and name.
"""


class GridRegion(object):

    def __init__(self, _region_name="", _region_code="", _description="", _filepath=""):
        self.region_name = _region_name
        self.region_code = _region_code
        self.description = _description
        self.filepath = _filepath

    @property
    def display_name(self):
        # type: () -> str
        return self.region_name

    def to_dict(self):
        # type: () -> dict
        d = {}
        d["region_name"] = self.region_name
        d["region_code"] = self.region_code
        d["description"] = self.description
        d["filepath"] = self.filepath
        return d

    @classmethod
    def from_dict(cls, _input_dict):
        # type: (dict) -> GridRegion
        new_obj = cls(
            _input_dict["region_name"], _input_dict["region_code"], _input_dict["description"], _input_dict["filepath"]
        )
        return new_obj

    def duplicate(self):
        # type: () -> GridRegion
        new_obj = GridRegion(
            _region_name=self.region_name,
            _region_code=self.region_code,
            _description=self.description,
            _filepath=self.filepath,
        )
        return new_obj

    def __copy__(self):
        # type: () -> GridRegion
        return self.duplicate()

    def __str__(self):
        return "GridRegion [{}]: {} | {} | {}".format(
            self.region_code, self.region_name, self.description, self.filepath
        )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return self.__repr__()
