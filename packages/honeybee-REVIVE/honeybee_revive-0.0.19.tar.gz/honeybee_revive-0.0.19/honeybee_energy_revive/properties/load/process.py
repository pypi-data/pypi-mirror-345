# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE Properties Extension for Electric Equipment Load objects."""

try:
    from honeybee_energy.load.process import Process
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy_ph: {}".format(e))


class ProcessReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(ProcessReviveProperties_FromDictError, self).__init__(self.msg)


class ProcessReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (Process | None) -> None
        self._host = _host
        self.id_num = 0
        self.cost = 0.0
        self.labor_fraction = 0.4
        self.lifetime_years = 25

    @property
    def host(self):
        # type: () -> Process | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Process | None) -> ProcessReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (Process | None): The new host for the duplicated object.

        Returns:
        --------
            * (ProcessReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (Process | None) -> ProcessReviveProperties
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
            d["type"] = "ProcessRevivePropertiesAbridged"
        else:
            d["type"] = "ProcessReviveProperties"
        d["id_num"] = self.id_num
        d["cost"] = self.cost
        d["labor_fraction"] = self.labor_fraction
        d["lifetime_years"] = self.lifetime_years
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, Process | None) -> ProcessReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (Process | None): The host for the new object.

        Returns:
        --------
            * (ProcessReviveProperties): The new object.
        """

        valid_types = (
            "ProcessReviveProperties",
            "ProcessRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise ProcessReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(host)
        new_obj.id_num = _input_dict["id_num"]
        new_obj.cost = _input_dict["cost"]
        new_obj.labor_fraction = _input_dict["labor_fraction"]
        new_obj.lifetime_years = _input_dict["lifetime_years"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-Process Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
