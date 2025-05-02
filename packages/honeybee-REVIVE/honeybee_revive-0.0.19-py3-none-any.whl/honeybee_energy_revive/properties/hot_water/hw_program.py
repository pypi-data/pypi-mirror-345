# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Honeybee-Energy-REVIVE Properties Extension for ServiceHotWater Program objects."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee_energy.properties.extension import ServiceHotWaterProperties
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy.", e)


class ServiceHotWaterReviveProperties_FromDictError(Exception):
    def __init__(self, _expected_types, _input_type):
        self.msg = 'Error: Expected type of "{}". Got: {}'.format(_expected_types, _input_type)
        super(ServiceHotWaterReviveProperties_FromDictError, self).__init__(self.msg)


class ServiceHotWaterReviveProperties(object):
    """Honeybee-REVIVE Properties for storing REVIVE data."""

    def __init__(self, _host):
        # type: (ServiceHotWaterProperties | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> ServiceHotWaterProperties | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.__class__.__name__ if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (ServiceHotWaterProperties | None) -> ServiceHotWaterReviveProperties
        """Duplicate this object with a new host.

        Arguments:
        ----------
            * new_host (ServiceHotWaterProperties | None): The new host for the duplicated object.

        Returns:
        --------
            * (ServiceHotWaterPropertiesReviveProperties): The duplicated object.
        """

        return self.__copy__(new_host)

    def __copy__(self, new_host=None):
        # type: (ServiceHotWaterProperties | None) -> ServiceHotWaterReviveProperties
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
            d["type"] = "ServiceHotWaterRevivePropertiesAbridged"
        else:
            d["type"] = "ServiceHotWaterReviveProperties"
        d["id_num"] = self.id_num
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, ServiceHotWaterProperties | None) -> ServiceHotWaterReviveProperties
        """Create an object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): The dictionary to create the object from.
            * host (ServiceHotWaterProperties | None): The host for the new object.

        Returns:
        --------
            * (ServiceHotWaterPropertiesReviveProperties): The new object.
        """

        valid_types = (
            "ServiceHotWaterReviveProperties",
            "ServiceHotWaterRevivePropertiesAbridged",
        )
        if _input_dict["type"] not in valid_types:
            raise ServiceHotWaterReviveProperties_FromDictError(valid_types, _input_dict["type"])
        new_obj = cls(host)
        new_obj.id_num = _input_dict["id_num"]
        return new_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "HBE-ServiceHotWaterProperties Phius REVIVE Property: [host: {}]".format(self.host_name)

    def ToString(self):
        return str(self)
