# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Face Phius REVIVE Properties."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee.face import Face
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


class FaceReviveProperties(object):
    def __init__(self, _host):
        # type: (Face | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> Face | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Face | None) -> FaceReviveProperties
        """
        Duplicate the FaceReviveProperties object.

        Arguments:
        ----------
            * new_host (Face | None): The new host for the properties.

        Returns:
        ----------
            * FaceReviveProperties: The duplicated FaceReviveProperties object.
        """

        _host = new_host or self._host
        new_properties_obj = FaceReviveProperties(_host)
        new_properties_obj.id_num = self.id_num

        return new_properties_obj

    def __copy__(self):
        # type: () -> FaceReviveProperties
        return self.duplicate()

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "HB-Face Phius REVIVE Property: [host: {}]".format(self.host_name)

    def __str__(self):
        return self.__repr__()

    def to_dict(self, abridged=False):
        # type: (bool) -> dict[str, dict]
        """
        Convert the FaceReviveProperties object to a dictionary.

        Arguments:
        ----------
            * abridged (bool): Set to True to return an abridged version of the dictionary.

        Returns:
        ----------
            * dict[str, dict]: The FaceReviveProperties dictionary.
        """

        d = {}
        t = "FaceReviveProperties" if not abridged else "FaceRevivePropertiesAbridged"
        d.update({"type": t})
        d.update({"id_num": self.id_num})

        return {"revive": d}

    @classmethod
    def from_dict(cls, data, host):
        # type: (dict, Face | None) -> FaceReviveProperties
        """
        Create a FaceReviveProperties object from a dictionary.

        Arguments:
        ----------
            * data (dict): A dictionary with the FaceRevivePropertiesAbridged properties.
            * host (Face | None): The host object for the properties.

        Returns:
        ----------
            * FaceReviveProperties: The FaceReviveProperties object.
        """

        assert data["type"] == "FaceReviveProperties", "Expected FaceReviveProperties. Got {}.".format(data["type"])

        new_prop = cls(host)
        new_prop.id_num = data.get("id_num", 0)

        return new_prop

    def apply_properties_from_dict(self, _face_prop_dict):
        # type: (dict) -> None
        """Apply properties from an FaceRevivePropertiesAbridged dictionary.

        Arguments:
        ----------
            * _face_prop_dict (dict): A FaceRevivePropertiesAbridged dictionary loaded from
                the Face object itself. Unabridged.

        Returns:
        --------
            * None
        """
        return None
