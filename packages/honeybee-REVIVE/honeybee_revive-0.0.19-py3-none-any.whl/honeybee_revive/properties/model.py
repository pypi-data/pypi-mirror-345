# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Model Phius REVIVE Properties."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    from itertools import izip as zip  # type: ignore
except ImportError:
    pass  # Python3

try:
    from honeybee import extensionutil

    if TYPE_CHECKING:
        from honeybee.aperture import Aperture
        from honeybee.face import Face
        from honeybee.model import Model
        from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasureCollection
    from honeybee_revive.fuels import FuelCollection
    from honeybee_revive.grid_region import GridRegion
    from honeybee_revive.national_emissions import NationalEmissionsFactors

    if TYPE_CHECKING:
        from honeybee_revive.properties.aperture import ApertureReviveProperties
        from honeybee_revive.properties.face import FaceReviveProperties
        from honeybee_revive.properties.room import RoomReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import RoomReviveProperties:\n\t{}".format(e))


class ModelReviveProperties(object):

    def __init__(self, _host):
        # type: (Model | None) -> None
        self._host = _host
        self.id_num = 0
        self.grid_region = GridRegion()
        self.national_emissions_factors = NationalEmissionsFactors()
        self.analysis_duration = 50
        self.envelope_labor_cost_fraction = 0.4
        self.co2_measures = CO2ReductionMeasureCollection()
        self.fuels = FuelCollection.with_default_fuels()

    @property
    def host(self):
        # type: () -> Model | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    @property
    def host_rooms(self):
        # type: () -> tuple[Room]
        if self.host:
            return self.host.rooms
        return tuple()

    def duplicate(self, new_host=None):
        # type: (Model | None) -> ModelReviveProperties
        """
        Create a duplicate of the ModelReviveProperties object.

        Arguments:
        ----------
            * new_host (Model | None): The new host for the properties.

        Returns:
        ----------
            * ModelReviveProperties: The duplicated ModelReviveProperties object
        """
        _host = new_host or self._host
        new_properties_obj = ModelReviveProperties(_host)
        new_properties_obj.id_num = self.id_num
        new_properties_obj.grid_region = self.grid_region.duplicate()
        new_properties_obj.national_emissions_factors = self.national_emissions_factors.duplicate()
        new_properties_obj.analysis_duration = self.analysis_duration
        new_properties_obj.envelope_labor_cost_fraction = self.envelope_labor_cost_fraction
        new_properties_obj.co2_measures = self.co2_measures.duplicate()
        new_properties_obj.fuels = self.fuels.duplicate()

        return new_properties_obj

    def __copy___(self):
        # type: () -> ModelReviveProperties
        return self.duplicate()

    def __str__(self):
        return "HB-Model Phius REVIVE Property: [host: {}]".format(self.host_name)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return self.__repr__()

    def to_dict(self, abridged=False):
        # type: (bool) -> dict[str, dict]
        """
        Convert the ModelReviveProperties object to a dictionary.

        Arguments:
        ----------
            * abridged (bool): Set to True to return an abridged version of the dictionary.

        Returns:
        ----------
            * dict: The ModelReviveProperties dictionary.
        """

        d = {}

        if abridged == False:
            d["type"] = "ModelRevivePropertiesAbridged"
        else:
            d["type"] = "ModelReviveProperties"

        d["id_num"] = self.id_num
        d["grid_region"] = self.grid_region.to_dict()
        d["national_emissions_factors"] = self.national_emissions_factors.to_dict()
        d["analysis_duration"] = self.analysis_duration
        d["envelope_labor_cost_fraction"] = self.envelope_labor_cost_fraction
        d["co2_measures"] = self.co2_measures.to_dict()
        d["fuels"] = self.fuels.to_dict()

        return {"revive": d}

    @classmethod
    def from_dict(cls, _dict, host):
        # type: (dict, Model | None) -> ModelReviveProperties
        """
        Create a ModelReviveProperties object from a dictionary.

        Arguments:
        ----------
            * _dict (dict): A dictionary with the ModelReviveProperties properties.
            * host (Any): The host object for the properties.

        Returns:
        ----------
            * ModelReviveProperties: The ModelReviveProperties object.
        """

        assert _dict["type"] == "ModelReviveProperties", "Expected ModelReviveProperties. Got {}.".format(_dict["type"])

        new_prop = cls(host)
        new_prop.id_num = _dict["id_num"]
        new_prop.grid_region = GridRegion.from_dict(_dict["grid_region"])
        new_prop.national_emissions_factors = NationalEmissionsFactors.from_dict(_dict["national_emissions_factors"])
        new_prop.analysis_duration = _dict["analysis_duration"]
        new_prop.envelope_labor_cost_fraction = _dict["envelope_labor_cost_fraction"]
        new_prop.co2_measures = CO2ReductionMeasureCollection.from_dict(_dict["co2_measures"])
        new_prop.fuels = FuelCollection.from_dict(_dict["fuels"])

        return new_prop

    @staticmethod
    def load_properties_from_dict(data):
        # type: (dict[str, dict]) -> tuple[GridRegion, NationalEmissionsFactors, int, float, CO2ReductionMeasureCollection, FuelCollection]
        """Load the HB-Model .revive properties from an HB-Model dictionary as Python objects.

        The function is called when re-serializing an HB-Model object from a
        dictionary. It will load honeybee_revive entities as Python objects and returns
        a tuple of dictionaries with all the de-serialized Honeybee-REVIVE objects.

        Arguments:
        ----------
            data (dict[str, dict]): A dictionary representation of an entire honeybee-core Model.

        Returns:
        --------
            * None
        """
        assert "revive" in data["properties"], "HB-Model Dictionary possesses no ModelReviveProperties?"

        grid_region = GridRegion.from_dict(data["properties"]["revive"]["grid_region"])
        national_emissions_factors = NationalEmissionsFactors.from_dict(
            data["properties"]["revive"]["national_emissions_factors"]
        )
        analysis_duration = data["properties"]["revive"]["analysis_duration"]
        envelope_labor_cost_fraction = data["properties"]["revive"]["envelope_labor_cost_fraction"]
        measures_collection = CO2ReductionMeasureCollection.from_dict(data["properties"]["revive"]["co2_measures"])
        fuels_collection = FuelCollection.from_dict(data["properties"]["revive"]["fuels"])

        return (
            grid_region,
            national_emissions_factors,
            analysis_duration,
            envelope_labor_cost_fraction,
            measures_collection,
            fuels_collection,
        )

    def apply_properties_from_dict(self, data):
        # type: (dict) -> None
        """Apply the .revive properties of a dictionary to the host Model of this object.

        This method is called when the HB-Model is de-serialized from a dict back into
        a Python object. In an 'Abridged' HBJSON file, all the property information
        is stored at the model level, not at the sub-model object level. In that case,
        this method is used to apply the right property data back onto all the sub-model
        objects (faces, rooms, apertures, etc).

        Arguments:
        ----------
            * data (dict): A dictionary representation of an entire honeybee-core
                Model. Note that this dictionary must have ModelReviveProperties
                in order for this method to successfully apply the .revive properties.

        Returns:
        --------
            * None
        """
        assert "revive" in data["properties"], "Dictionary possesses no ModelReviveProperties?"

        # collect lists of .revive property dictionaries at the sub-model level (room, face, etc)
        (
            room_revive_dicts,
            face_revive_dicts,
            shd_revive_dicts,
            ap_revive_dicts,
            dr_revive_dicts,
        ) = extensionutil.model_extension_dicts(data, "revive", [], [], [], [], [])

        # re-build all of the .revive property objects from the HB-Model dict as python objects
        (
            self.grid_region,
            self.national_emissions_factors,
            self.analysis_duration,
            self.envelope_labor_cost_fraction,
            self.co2_measures,
            self.fuels,
        ) = self.load_properties_from_dict(data)

        # apply the .revive properties to all the sub-model objects in the HB-Model
        for room, room_dict in zip(self.host_rooms, room_revive_dicts):
            if not room_dict:
                continue
            hb_room_prop_revive = getattr(room.properties, "revive")  # type: RoomReviveProperties
            hb_room_prop_revive.apply_properties_from_dict(room_dict)

        apertures = []  # type: list[Aperture]
        faces = []  # type: list[Face]
        for hb_room in self.host_rooms:
            for face in hb_room.faces:
                faces.append(face)
                for aperture in face.apertures:
                    apertures.append(aperture)

        for face, face_dict in zip(faces, face_revive_dicts):
            face_prop_revive = getattr(face.properties, "revive")  # type: FaceReviveProperties
            face_prop_revive.apply_properties_from_dict(face_dict)

        for aperture, ap_dict in zip(apertures, ap_revive_dicts):
            ap_prop_revive = getattr(aperture.properties, "revive")  # type: ApertureReviveProperties
            ap_prop_revive.apply_properties_from_dict(ap_dict)
