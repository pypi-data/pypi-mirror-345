# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE Properties Extension for Honeybee-Energy Window Shade classes."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.material.shade import EnergyWindowMaterialBlind, EnergyWindowMaterialShade
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy_ph: {}".format(e))

try:
    from ph_units.unit_type import Unit
except ImportError as e:
    raise ImportError("Failed to import ph_units: {}".format(e))


class EnergyWindowMaterialShadeReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(EnergyWindowMaterialShadeReviveProperties_FromDictError, self).__init__(self.msg)


class EnergyWindowMaterialShadeReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (EnergyWindowMaterialShade | None) -> None
        self._host = _host
        self.id_num = 0
        self.kg_CO2_per_m2 = Unit(0.0, "KG/M2")
        self.cost_per_m2 = Unit(0.0, "COST/M2")
        self.labor_fraction = 0.4
        self.lifetime_years = 25

    @property
    def host(self):
        # type: () -> EnergyWindowMaterialShade | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (EnergyWindowMaterialShade | None) -> EnergyWindowMaterialShadeReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (EnergyWindowMaterialShade | None): The new host for the duplicated object.

        Returns:
        --------
            * (EnergyWindowMaterialShadeReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, _host=None):
        # type: (EnergyWindowMaterialShade | None) -> EnergyWindowMaterialShadeReviveProperties
        host = _host or self.host
        new_obj = self.__class__(host)
        new_obj.id_num = self.id_num
        new_obj.kg_CO2_per_m2 = Unit(self.kg_CO2_per_m2.value, self.kg_CO2_per_m2.unit)
        new_obj.cost_per_m2 = Unit(self.cost_per_m2.value, self.cost_per_m2.unit)
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
            d["type"] = "EnergyWindowMaterialShadeRevivePropertiesAbridged"
        else:
            d["type"] = "EnergyWindowMaterialShadeReviveProperties"

        d["id_num"] = self.id_num
        d["kg_CO2_per_m2"] = self.kg_CO2_per_m2.to_dict()
        d["cost_per_m2"] = self.cost_per_m2.to_dict()
        d["labor_fraction"] = self.labor_fraction
        d["lifetime_years"] = self.lifetime_years
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, _host):
        # type: (dict, EnergyWindowMaterialShade | None) -> EnergyWindowMaterialShadeReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (EnergyWindowMaterialShade | None): The host for the new object.

        Returns:
        --------
            * (EnergyWindowMaterialShadeReviveProperties): The new object.
        """

        valid_types = (
            "EnergyWindowMaterialShadeReviveProperties",
            "EnergyWindowMaterialShadeRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise EnergyWindowMaterialShadeReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(_host)
        new_obj.id_num = _input_dict["id_num"]
        new_obj.kg_CO2_per_m2 = Unit.from_dict(_input_dict["kg_CO2_per_m2"])
        new_obj.cost_per_m2 = Unit.from_dict(_input_dict["cost_per_m2"])
        new_obj.labor_fraction = _input_dict["labor_fraction"]
        new_obj.lifetime_years = _input_dict["lifetime_years"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-EnergyWindowMaterialShade Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)


class EnergyWindowMaterialBlindReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (EnergyWindowMaterialBlind | None) -> None
        self._host = _host
        self.id_num = 0
        self.kg_CO2_per_m2 = Unit(0.0, "KG/M2")
        self.cost_per_m2 = Unit(0.0, "COST/M2")
        self.labor_fraction = 0.4
        self.lifetime_years = 25

    @property
    def host(self):
        # type: () -> EnergyWindowMaterialBlind | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (EnergyWindowMaterialBlind | None) -> EnergyWindowMaterialBlindReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (EnergyWindowMaterialBlind | None): The new host for the duplicated object.

        Returns:
        --------
            * (EnergyWindowMaterialBlindReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, _host=None):
        # type: (EnergyWindowMaterialBlind | None) -> EnergyWindowMaterialBlindReviveProperties
        host = _host or self.host
        new_obj = self.__class__(host)
        new_obj.id_num = self.id_num
        new_obj.kg_CO2_per_m2 = Unit(self.kg_CO2_per_m2.value, self.kg_CO2_per_m2.unit)
        new_obj.cost_per_m2 = Unit(self.cost_per_m2.value, self.cost_per_m2.unit)
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
            d["type"] = "EnergyWindowMaterialBlindRevivePropertiesAbridged"
        else:
            d["type"] = "EnergyWindowMaterialBlindReviveProperties"

        d["id_num"] = self.id_num
        d["kg_CO2_per_m2"] = self.kg_CO2_per_m2.to_dict()
        d["cost_per_m2"] = self.cost_per_m2.to_dict()
        d["labor_fraction"] = self.labor_fraction
        d["lifetime_years"] = self.lifetime_years
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, _host):
        # type: (dict, EnergyWindowMaterialBlind | None) -> EnergyWindowMaterialBlindReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (EnergyWindowMaterialBlind | None): The host for the new object.

        Returns:
        --------
            * (EnergyWindowMaterialBlindReviveProperties): The new object.
        """

        valid_types = (
            "EnergyWindowMaterialBlindReviveProperties",
            "EnergyWindowMaterialBlindRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise EnergyWindowMaterialShadeReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(_host)
        new_obj.id_num = _input_dict["id_num"]
        new_obj.kg_CO2_per_m2 = Unit.from_dict(_input_dict["kg_CO2_per_m2"])
        new_obj.cost_per_m2 = Unit.from_dict(_input_dict["cost_per_m2"])
        new_obj.labor_fraction = _input_dict["labor_fraction"]
        new_obj.lifetime_years = _input_dict["lifetime_years"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-EnergyWindowMaterialBlind Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
