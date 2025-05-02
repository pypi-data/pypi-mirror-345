# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE Properties Extension for Electric Equipment Load objects."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.load.equipment import ElectricEquipment
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy_ph: {}".format(e))


class ElectricEquipmentReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(ElectricEquipmentReviveProperties_FromDictError, self).__init__(self.msg)


class ElectricEquipmentReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (ElectricEquipment | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> ElectricEquipment | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (ElectricEquipment | None) -> ElectricEquipmentReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (ElectricEquipment | None): The new host for the duplicated object.

        Returns:
        --------
            * (ElectricEquipmentReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (ElectricEquipment | None) -> ElectricEquipmentReviveProperties
        host = new_host or self.host
        new_obj = self.__class__(host)
        new_obj.id_num = self.id_num
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
            d["type"] = "ElectricEquipmentRevivePropertiesAbridged"
        else:
            d["type"] = "ElectricEquipmentReviveProperties"
        d["id_num"] = self.id_num
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, ElectricEquipment | None) -> ElectricEquipmentReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (ElectricEquipment | None): The host for the new object.

        Returns:
        --------
            * (ElectricEquipmentReviveProperties): The new object.
        """

        valid_types = (
            "ElectricEquipmentReviveProperties",
            "ElectricEquipmentRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise ElectricEquipmentReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(host)
        new_obj.id_num = _input_dict["id_num"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-ElectricEquipment Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
