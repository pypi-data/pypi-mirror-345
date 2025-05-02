# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE properties for Honeybee-Energy-HeatCoolSystem HVAC Objects."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.hvac.heatcool._base import _HeatCoolBase
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_revive.hvac.equipment import PhiusReviveHVACEquipment, PhiusReviveHVACEquipmentCollection
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))


class HeatCoolSystemReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(HeatCoolSystemReviveProperties_FromDictError, self).__init__(self.msg)


class HeatCoolSystemReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (_HeatCoolBase | None) -> None
        self._host = _host
        self.equipment_collection = PhiusReviveHVACEquipmentCollection()

    @property
    def host(self):
        # type: () -> _HeatCoolBase | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def add_equipment(self, equipment):
        # type: (PhiusReviveHVACEquipment) -> None
        """Add equipment to the equipment collection.

        Arguments:
        ----------
            * equipment (PhiusReviveHVACEquipment): The equipment to add.
        """
        self.equipment_collection.add_equipment(equipment)

    def duplicate(self, new_host=None):
        # type: (_HeatCoolBase | None) -> HeatCoolSystemReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (_HeatCoolBase| None): The new host for the duplicated object.

        Returns:
        --------
            * (HeatCoolBaseReviveProperties): The duplicated object.
        """
        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (_HeatCoolBase | None) -> HeatCoolSystemReviveProperties
        host = new_host or self.host
        new_obj = self.__class__(host)
        new_obj.equipment_collection = self.equipment_collection.duplicate()
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
            d["type"] = "HeatCoolSystemRevivePropertiesAbridged"
        else:
            d["type"] = "HeatCoolSystemReviveProperties"
        d["equipment_collection"] = self.equipment_collection.to_dict(abridged)
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, _host):
        # type: (dict, _HeatCoolBase | None) -> HeatCoolSystemReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (_HeatCoolBase | None): The host for the new object.

        Returns:
        --------
            * (HeatCoolBaseReviveProperties): The new object.
        """
        valid_types = (
            "HeatCoolSystemReviveProperties",
            "HeatCoolSystemRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise HeatCoolSystemReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(_host)
        new_obj.equipment_collection = PhiusReviveHVACEquipmentCollection.from_dict(_input_dict["equipment_collection"])
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-HeatCoolSystem Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
