# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-REVIVE HVAC Equipment and Equipment-Collection."""

from uuid import uuid4

try:
    from typing import Iterable
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee._lockable import lockable
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


@lockable
class PhiusReviveHVACEquipment(object):

    def __init__(self, display_name="unnamed_equipment", cost=0.0, labor_fraction=0.0, lifetime_years=0):
        self.identifier = str(uuid4())
        self.display_name = display_name
        self.cost = cost
        self.labor_fraction = labor_fraction
        self.lifetime_years = lifetime_years

    def to_dict(self, abridged=False):
        # type: (bool) -> dict
        d = {}
        if abridged:
            d["type"] = "PhiusReviveHVACEquipmentAbridged"
        else:
            d["type"] = "PhiusReviveHVACEquipment"

        d["identifier"] = self.identifier
        d["display_name"] = self.display_name
        d["cost"] = self.cost
        d["labor_fraction"] = self.labor_fraction
        d["lifetime_years"] = self.lifetime_years
        return d

    @classmethod
    def from_dict(cls, _input_dict):
        # type: (dict) -> PhiusReviveHVACEquipment
        new_obj = cls()
        new_obj.identifier = _input_dict["identifier"]
        new_obj.display_name = _input_dict["display_name"]
        new_obj.cost = _input_dict["cost"]
        new_obj.labor_fraction = _input_dict["labor_fraction"]
        new_obj.lifetime_years = _input_dict["lifetime_years"]
        return new_obj

    def __copy__(self):
        # type: () -> PhiusReviveHVACEquipment
        new_obj = self.__class__()
        new_obj.display_name = self.display_name
        new_obj.identifier = self.identifier
        new_obj.cost = self.cost
        new_obj.labor_fraction = self.labor_fraction
        new_obj.lifetime_years = self.lifetime_years
        return new_obj

    def duplicate(self):
        # type: () -> PhiusReviveHVACEquipment
        return self.__copy__()

    def __str__(self):
        # type: () -> str
        return self.__repr__()

    def __repr__(self):
        # type: () -> str
        return "Phius Revive HVAC Equipment: [{}]".format(self.display_name)

    def ToString(self):
        # type: () -> str
        return str(self)


class PhiusReviveHVACEquipmentCollection(object):
    """A collection of PhiusReviveHVACEquipment objects."""

    def __init__(self):
        self._equipment = {}  # type: dict[str, PhiusReviveHVACEquipment]
        self._iter = iter(self.equipment)

    @property
    def equipment(self):
        # type: () -> list[PhiusReviveHVACEquipment]
        return list(self._equipment.values())

    def add_equipment(self, _equipment):
        # type: (PhiusReviveHVACEquipment) -> None
        self._equipment[_equipment.identifier] = _equipment

    def get_equipment_by_identifier(self, _identifier):
        # type: (str) -> PhiusReviveHVACEquipment | None
        return self._equipment.get(_identifier, None)

    def __contains__(self, _equipment):
        # type: (PhiusReviveHVACEquipment) -> bool
        return _equipment.identifier in self._equipment

    def to_dict(self, abridged=False):
        # type: (bool) -> dict
        d = {}
        if abridged:
            d["type"] = "PhiusReviveHVACEquipmentCollectionAbridged"
        else:
            d["type"] = "PhiusReviveHVACEquipmentCollection"
        d["equipment"] = [equip.to_dict(abridged) for equip in self.equipment]
        return d

    @classmethod
    def from_dict(cls, _input_dict):
        # type: (dict) -> PhiusReviveHVACEquipmentCollection
        new_obj = cls()
        for equip_dict in _input_dict["equipment"]:
            new_obj.add_equipment(PhiusReviveHVACEquipment.from_dict(equip_dict))
        return new_obj

    def __copy__(self):
        # type: () -> PhiusReviveHVACEquipmentCollection
        new_obj = self.__class__()
        for equip in self.equipment:
            new_obj.add_equipment(equip.duplicate())
        return new_obj

    def duplicate(self):
        # type: () -> PhiusReviveHVACEquipmentCollection
        return self.__copy__()

    def __len__(self):
        return len(self._equipment)

    def __iter__(self):
        # type: () -> PhiusReviveHVACEquipmentCollection
        self._iter = iter(self.equipment)
        return self

    def __next__(self):
        # type: () -> PhiusReviveHVACEquipment
        return next(self._iter)

    def __str__(self):
        # type: () -> str
        return "{}({} items)".format(self.__class__.__name__, len(self._equipment))

    def __repr__(self):
        # type: () -> str
        return self.__str__()

    def ToString(self):
        # type: () -> str
        return self.__str__()
