# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Model Phius REVIVE CO2-Reduction-Measure and Measure-Collection Classes."""

try:
    from typing import Iterator
except ImportError:
    pass  # Python 2.7


class CO2ReductionMeasure(object):
    def __init__(
        self,
        name="unnamed_CO2_measure",
        measure_type="PERFORMANCE",
        year=60,
        cost=8500.0,
        kg_CO2=0.0,
        country_name="USA",
        labor_fraction=0.4,
    ):
        self.name = name
        self._measure_type = measure_type
        self.year = year
        self.cost = cost
        self.kg_CO2 = kg_CO2
        self.country_name = country_name
        self.labor_fraction = labor_fraction

    @property
    def unique_id(self):
        # type: () -> str
        return "{}-{}-{}-{}-{}".format(self.name, self.measure_type, self.year, int(self.cost), self.labor_fraction)

    @property
    def measure_type(self):
        # type: () -> str
        return self._measure_type

    @measure_type.setter
    def measure_type(self, _input):
        # type: (str) -> None
        _input = str(_input).upper().strip()
        if _input not in ["PERFORMANCE", "NON_PERFORMANCE"]:
            raise ValueError("Measure type must be either 'PERFORMANCE' or 'COST'.")
        self._measure_type = _input

    def to_dict(self):
        # type: () -> dict
        d = {}
        d["type"] = "CO2ReductionMeasure"
        d["measure_type"] = self.measure_type
        d["name"] = self.name
        d["year"] = self.year
        d["cost"] = self.cost
        d["kg_CO2"] = self.kg_CO2
        d["country_name"] = self.country_name
        d["labor_fraction"] = self.labor_fraction
        return d

    @classmethod
    def from_dict(cls, _dict):
        # type: (dict) -> CO2ReductionMeasure
        if not _dict["type"] == "CO2ReductionMeasure":
            raise ValueError("The supplied dict is not a CO2ReductionMeasure? Got: {}".format(_dict["type"]))

        measure = cls()
        measure.measure_type = _dict["measure_type"]
        measure.name = _dict["name"]
        measure.year = _dict["year"]
        measure.cost = _dict["cost"]
        measure.kg_CO2 = _dict["kg_CO2"]
        measure.country_name = _dict["country_name"]
        measure.labor_fraction = _dict["labor_fraction"]
        return measure

    def duplicate(self):
        # type: () -> CO2ReductionMeasure
        return CO2ReductionMeasure.from_dict(self.to_dict())

    def __copy__(self):
        # type: () -> CO2ReductionMeasure
        return self.duplicate()

    def __str__(self):
        # type: () -> str
        return "{}(name={})".format(self.__class__.__name__, self.name)

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


class CO2ReductionMeasureCollection(object):
    def __init__(self):
        self._storage = {}  # type: dict[str, CO2ReductionMeasure]

    def add_measure(self, measure):
        # type: (CO2ReductionMeasure) -> None
        self._storage[measure.unique_id] = measure

    def measures(self):
        # type: () -> list[CO2ReductionMeasure]
        return list(self._storage.values())

    def keys(self):
        # type: () -> list[str]
        return [k for k, v in sorted(self._storage.items(), key=lambda x: x[1].unique_id)]

    def values(self):
        # type: () -> list[CO2ReductionMeasure]
        return list(sorted(self._storage.values(), key=lambda x: x.unique_id))

    def duplicate(self):
        # type: () -> CO2ReductionMeasureCollection
        new_collection = CO2ReductionMeasureCollection()
        for measure in self.measures():
            new_collection.add_measure(measure.duplicate())
        return new_collection

    def __copy__(self):
        # type: () -> CO2ReductionMeasureCollection
        return self.duplicate()

    def to_dict(self):
        # type: () -> dict[str, dict]
        return {k: v.to_dict() for k, v in self._storage.items()}

    @classmethod
    def from_dict(cls, _dict):
        # type: (dict) -> CO2ReductionMeasureCollection
        collection = cls()
        for k, v in _dict.items():
            collection.add_measure(CO2ReductionMeasure.from_dict(v))
        return collection

    def __iter__(self):
        # type: () -> Iterator[CO2ReductionMeasure]
        return iter(sorted(self._storage.values(), key=lambda x: x.unique_id))

    def __contains__(self, key):
        # type: (str | CO2ReductionMeasure) -> bool
        if isinstance(key, CO2ReductionMeasure):
            return key in self._storage.values()
        return key in self._storage

    def __len__(self):
        # type: () -> int
        return len(self._storage)

    def __str__(self):
        # type: () -> str
        return "{}({}-measures)".format(self.__class__.__name__, len(self._storage))

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)
