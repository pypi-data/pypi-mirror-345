# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE Properties Extension for Lighting Load objects."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.load.lighting import Lighting
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy_ph: {}".format(e))


class LightingReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(LightingReviveProperties_FromDictError, self).__init__(self.msg)


class LightingReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (Lighting | None) -> None
        self._host = _host
        self.id_num = 0
        self.cost = 0.0
        self.labor_fraction = 0.4
        self.lifetime_years = 25

    @property
    def host(self):
        # type: () -> Lighting | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Lighting | None) -> LightingReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (Lighting | None): The new host for the duplicated object.

        Returns:
        --------
            * (LightingReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (Lighting | None) -> LightingReviveProperties
        host = new_host or self.host
        new_obj = self.__class__(host)
        new_obj.id_num = self.id_num
        new_obj.cost = self.cost
        new_obj.labor_fraction = self.labor_fraction
        new_obj.lifetime_years = self.lifetime_years
        return new_obj

    def to_dict(self, abridged=False):
        # type: (bool) -> dict
        """Return a dictionary representation of the object.

        Arguments:
        ----------
            * abridged (bool): Default=False. Set to True to return an abridged version of the object.

        Returns:
        --------
            * (dict): A dictionary representation of the object.
        """

        d = {}
        if abridged:
            d["type"] = "LightingRevivePropertiesAbridged"
        else:
            d["type"] = "LightingReviveProperties"
        d["id_num"] = self.id_num
        d["cost"] = self.cost
        d["labor_fraction"] = self.labor_fraction
        d["lifetime_years"] = self.lifetime_years
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, Lighting | None) -> LightingReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (Lighting | None): The host for the new object.

        Returns:
        --------
            * (LightingReviveProperties): The new object.
        """

        valid_types = (
            "LightingReviveProperties",
            "LightingRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise LightingReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(host)
        new_obj.id_num = _input_dict["id_num"]
        new_obj.cost = _input_dict["cost"]
        new_obj.labor_fraction = _input_dict["labor_fraction"]
        new_obj.lifetime_years = _input_dict["lifetime_years"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-Lighting Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
