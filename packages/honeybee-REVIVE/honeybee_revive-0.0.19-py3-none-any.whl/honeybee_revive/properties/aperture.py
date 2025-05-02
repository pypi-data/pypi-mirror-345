# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Aperture Phius REVIVE Properties."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


class ApertureReviveProperties(object):
    def __init__(self, _host):
        # type: (Aperture | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> Aperture | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Aperture | None) -> ApertureReviveProperties
        """
        Duplicate the ApertureReviveProperties object.

        Arguments:
        ----------
            * new_host (Aperture | None): The new host for the properties.

        Returns:
        ----------
            * ApertureReviveProperties: The duplicated ApertureReviveProperties object.
        """

        _host = new_host or self._host
        new_properties_obj = ApertureReviveProperties(_host)
        new_properties_obj.id_num = self.id_num
        return new_properties_obj

    def __copy__(self):
        # type: () -> ApertureReviveProperties
        return self.duplicate()

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "HB-Aperture Phius REVIVE Property: [host: {}]".format(self.host_name)

    def to_dict(self, abridged=False):
        # type: (bool) -> dict[str, dict]
        """
        Convert the ApertureReviveProperties object to a dictionary.

        Arguments:
        ----------
            * abridged (bool): Set to True to return an abridged version of the dictionary.

        Returns:
        ----------
            * dict[ster, dict]: The ApertureReviveProperties dictionary.
        """

        d = {}
        d["type"] = "ApertureReviveProperties" if not abridged else "ApertureRevivePropertiesAbridged"
        d["id_num"] = self.id_num
        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, Aperture | None) -> ApertureReviveProperties
        """
        Create an ApertureReviveProperties object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): A dictionary with the ApertureRevivePropertiesAbridged properties.
            * host (Aperture | None): The host object for the properties.

        Returns:
        ----------
            * ApertureReviveProperties: The ApertureReviveProperties object.
        """

        assert _input_dict["type"] == "ApertureReviveProperties", "Expected ApertureReviveProperties. Got {}.".format(
            _input_dict["type"]
        )
        new_prop = cls(host)
        new_prop.id_num = _input_dict["id_num"]
        return new_prop

    def apply_properties_from_dict(self, _aperture_prop_dict):
        # type: (dict) -> None
        """Apply properties from an ApertureRevivePropertiesAbridged dictionary.

        Arguments:
        ----------
            * _aperture_prop_dict (dict): An ApertureRevivePropertiesAbridged dictionary loaded from
                the Aperture object itself. Unabridged.

        Returns:
        ----------
            * None
        """
        return None
