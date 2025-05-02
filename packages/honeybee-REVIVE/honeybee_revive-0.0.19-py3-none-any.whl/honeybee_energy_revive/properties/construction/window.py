# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE properties for Honeybee-Energy WindowConstruction Objects"""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_revive.properties.materials.glazing import EnergyWindowMaterialGlazingReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_revive:\n\t{}".format(e))

try:
    from ph_units.unit_type import Unit
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class WindowConstructionReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(WindowConstructionReviveProperties_FromDictError, self).__init__(self.msg)


class WindowConstructionReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host=None):
        # type: (WindowConstruction | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> WindowConstruction | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    @property
    def total_thickness_m(self):
        # type: () -> Unit
        if not self.host:
            return Unit(0.0, "M")
        return Unit(self.host.thickness, "M")

    @property
    def kg_CO2_per_m2(self):
        # type: () -> Unit
        """Return the total kg-of-CO2-per-m2 of all the materials in the construction."""

        if not self.host:
            return Unit(0.0, "KG/M2")

        total = 0.0
        for mat in self.host.materials:
            mat_prop = getattr(mat.properties, "revive")  # type: EnergyWindowMaterialGlazingReviveProperties
            total += mat_prop.kg_CO2_per_m2.value
        return Unit(total, "KG/M2")

    @property
    def cost_per_m2(self):
        # type: () -> Unit
        """Return the total cost-per-m2 of all the materials in the construction."""

        if not self.host:
            return Unit(0.0, "COST/M2")

        total = 0.0
        for mat in self.host.materials:
            mat_prop = getattr(mat.properties, "revive")  # type: EnergyWindowMaterialGlazingReviveProperties
            total += mat_prop.cost_per_m2.value
        return Unit(total, "COST/M2")

    @property
    def labor_fraction(self):
        # type: () -> float
        """Return the weighted-average labor fraction of all the materials in the construction."""

        if not self.host:
            return 0.0

        total = 0.0
        for mat in self.host.materials:
            mat_prop = getattr(mat.properties, "revive")  # type: EnergyWindowMaterialGlazingReviveProperties
            total += mat_prop.labor_fraction * mat.thickness
        try:
            return total / self.total_thickness_m.value
        except ZeroDivisionError:
            return 0.0

    @property
    def lifetime_years(self):
        # type: () -> int
        """Return the weighted-average lifetime of all the materials in the construction."""

        if not self.host:
            return 0

        total = 0.0
        for mat in self.host.materials:
            mat_prop = getattr(mat.properties, "revive")  # type: EnergyWindowMaterialGlazingReviveProperties
            total += mat_prop.lifetime_years * mat.thickness
        try:
            return round(total / self.total_thickness_m.value)
        except ZeroDivisionError:
            return 0

    def duplicate(self, new_host=None):
        # type: (WindowConstruction | None) -> WindowConstructionReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (WindowConstruction | None): The new host for the duplicated object.

        Returns:
        --------
            * (WindowConstructionReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (WindowConstruction | None) -> WindowConstructionReviveProperties
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
            d["type"] = "WindowConstructionRevivePropertiesAbridged"
        else:
            d["type"] = "WindowConstructionReviveProperties"
        d["id_num"] = self.id_num
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, WindowConstruction | None) -> WindowConstructionReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (WindowConstruction | None): The host for the new object.

        Returns:
        --------
            * (WindowConstructionReviveProperties): The new object.
        """

        valid_types = (
            "WindowConstructionReviveProperties",
            "WindowConstructionRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise WindowConstructionReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(host)
        new_obj.id_num = _input_dict["id_num"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-WindowConstruction Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
