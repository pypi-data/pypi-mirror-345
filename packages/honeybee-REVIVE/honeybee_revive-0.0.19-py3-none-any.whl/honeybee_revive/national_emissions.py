# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Model Phius REVIVE National Emissions Factors."""


class NationalEmissionsFactors(object):

    def __init__(self, country_name="", us_trading_rank=0, GDP_million_USD=0.0, CO2_MT=0.0, kg_CO2_per_USD=0.0):
        # type: (str, int, float, float, float) -> None
        self.country_name = country_name
        self.us_trading_rank = us_trading_rank
        self.GDP_million_USD = GDP_million_USD
        self.CO2_MT = CO2_MT
        self.kg_CO2_per_USD = kg_CO2_per_USD

    def to_dict(self):
        # type: () -> dict
        d = {}
        d["type"] = "NationalEmissionsFactors"
        d["country_name"] = self.country_name
        d["us_trading_rank"] = self.us_trading_rank
        d["GDP_million_USD"] = self.GDP_million_USD
        d["CO2_MT"] = self.CO2_MT
        d["kg_CO2_per_USD"] = self.kg_CO2_per_USD
        return d

    @classmethod
    def from_dict(cls, _input_dict):
        # type: (dict) -> NationalEmissionsFactors
        if not _input_dict["type"] == "NationalEmissionsFactors":
            raise ValueError("This is not a 'NationalEmissionsFactors' dict. Got: {}".format(_input_dict["type"]))

        new_obj = cls(
            _input_dict["country_name"],
            _input_dict["us_trading_rank"],
            _input_dict["GDP_million_USD"],
            _input_dict["CO2_MT"],
            _input_dict["kg_CO2_per_USD"],
        )
        return new_obj

    def duplicate(self):
        # type: () -> NationalEmissionsFactors
        new_obj = NationalEmissionsFactors(
            country_name=self.country_name,
            us_trading_rank=self.us_trading_rank,
            GDP_million_USD=self.GDP_million_USD,
            CO2_MT=self.CO2_MT,
            kg_CO2_per_USD=self.kg_CO2_per_USD,
        )
        return new_obj

    def __copy__(self):
        # type: () -> NationalEmissionsFactors
        return self.duplicate()

    def __str__(self):
        return "NationalEmissionsFactors [{}]: {} | {} | {} | {}".format(
            self.country_name, self.us_trading_rank, self.GDP_million_USD, self.CO2_MT, self.kg_CO2_per_USD
        )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return self.__repr__()
