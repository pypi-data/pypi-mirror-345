# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Model Phius REVIVE Fuel types and Fuel-Collection Classes."""

try:
    from typing import Iterator
except ImportError:
    pass  # Python 2.7


class Fuel(object):

    def __init__(
        self,
        _fuel_type="ELECTRICITY",
        _purchase_price_per_kwh=0.0,
        _sale_price_per_kwh=0.0,
        _annual_base_price=0.0,
    ):
        # type: (str, float, float, float) -> None
        self._fuel_type = _fuel_type
        self.purchase_price_per_kwh = _purchase_price_per_kwh
        self.sale_price_per_kwh = _sale_price_per_kwh
        self.annual_base_price = _annual_base_price

    @property
    def unique_id(self):
        # type: () -> str
        return "{}-{}-{}-{}".format(
            self.fuel_type, self.purchase_price_per_kwh, self.sale_price_per_kwh, self.annual_base_price
        )

    @property
    def fuel_type(self):
        # type: () -> str
        return self._fuel_type

    @fuel_type.setter
    def fuel_type(self, _input):
        # type: (str) -> None
        _input = str(_input).upper().strip()
        allowed_types = ["ELECTRICITY", "NATURAL_GAS"]
        if _input not in allowed_types:
            raise ValueError("Fuel type must be: {}.".format(allowed_types))
        self._fuel_type = _input

    def to_dict(self):
        # type: () -> dict
        d = {}
        d["type"] = "Fuel"
        d["fuel_type"] = self.fuel_type
        d["purchase_price_per_kwh"] = self.purchase_price_per_kwh
        d["sale_price_per_kwh"] = self.sale_price_per_kwh
        d["annual_base_price"] = self.annual_base_price
        return d

    @classmethod
    def from_dict(cls, _dict):
        # type: (dict) -> Fuel
        if not _dict["type"] == "Fuel":
            raise ValueError("The supplied dict is not a Fuel? Got: {}".format(_dict["type"]))

        fuel = cls()
        fuel.fuel_type = _dict["fuel_type"]
        fuel.purchase_price_per_kwh = _dict["purchase_price_per_kwh"]
        fuel.sale_price_per_kwh = _dict["sale_price_per_kwh"]
        fuel.annual_base_price = _dict["annual_base_price"]
        return fuel

    def duplicate(self):
        # type: () -> Fuel
        return Fuel.from_dict(self.to_dict())

    def __copy__(self):
        # type: () -> Fuel
        return self.duplicate()

    def __str__(self):
        # type: () -> str
        return "{}(type={})".format(self.__class__.__name__, self.fuel_type)

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


class FuelCollection(object):

    def __init__(self):
        # type: () -> None
        self._storage = {}  # type: dict[str, Fuel]

    def add_fuel(self, fuel):
        # type: (Fuel) -> None
        self._storage[fuel.fuel_type] = fuel

    def get_fuel(self, fuel_type):
        # type: (str) -> Fuel
        return self._storage[fuel_type]

    def fuels(self):
        # type: () -> list[Fuel]
        return list(self._storage.values())

    def keys(self):
        # type: () -> list[str]
        return sorted(self._storage.keys())

    def values(self):
        # type: () -> list[Fuel]
        return list(sorted(self._storage.values(), key=lambda f: f.fuel_type))

    def duplicate(self):
        # type: () -> FuelCollection
        new_collection = FuelCollection()
        for fuel in self.fuels():
            new_collection.add_fuel(fuel.duplicate())
        return new_collection

    def __copy__(self):
        # type: () -> FuelCollection
        return self.duplicate()

    def to_dict(self):
        # type: () -> dict[str, dict]
        return {k: v.to_dict() for k, v in self._storage.items()}

    @classmethod
    def from_dict(cls, _dict):
        # type: (dict) -> FuelCollection
        collection = cls()
        for v in _dict.values():
            collection.add_fuel(Fuel.from_dict(v))
        return collection

    @classmethod
    def with_default_fuels(cls):
        # type: () -> FuelCollection
        collection = cls()

        electricity = Fuel(
            _fuel_type="ELECTRICITY",
            _purchase_price_per_kwh=0.17984,
            _sale_price_per_kwh=0.132,
            _annual_base_price=200.0,
        )
        collection.add_fuel(electricity)

        natural_gas = Fuel(
            _fuel_type="NATURAL_GAS",
            _purchase_price_per_kwh=0.0471,
            _sale_price_per_kwh=0.0,
            _annual_base_price=200.0,
        )
        collection.add_fuel(natural_gas)

        return collection

    def __iter__(self):
        # type: () -> Iterator[Fuel]
        return iter(sorted(self._storage.values(), key=lambda x: x.unique_id))

    def __contains__(self, key):
        # type: (str | Fuel) -> bool
        if isinstance(key, Fuel):
            return key in self._storage.values()
        return key in self._storage

    def __len__(self):
        # type: () -> int
        return len(self._storage)

    def __str__(self):
        # type: () -> str
        return "{}({}-fuels)".format(self.__class__.__name__, len(self._storage))

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)
