# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Shade Phius REVIVE Properties."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee.shade import Shade
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


class ShadeReviveProperties(object):
    # type: (Shade | None) -> None
    def __init__(self, _host):
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> Shade | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Shade | None) -> ShadeReviveProperties
        """
        Create a duplicate of the ShadeReviveProperties object.

        Arguments:
        ----------
            * new_host (Any): The new host for the properties.

        Returns:
        ----------
            * ShadeReviveProperties: The duplicated ShadeReviveProperties object
        """

        _host = new_host or self._host
        new_properties_obj = ShadeReviveProperties(_host)
        new_properties_obj.id_num = self.id_num

        return new_properties_obj

    def __copy__(self):
        # type: () -> ShadeReviveProperties
        return self.duplicate()

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "HB-Shade Phius REVIVE Properties: [host: {}]".format(self.host_name)

    def __str__(self):
        return self.__repr__()

    def to_dict(self, abridged=False):
        # type: (bool) -> dict[str, dict]
        """
        Convert the ShadeReviveProperties object to a dictionary.

        Arguments:
        ----------
            * abridged (bool): Set to True to return an abridged version of the dictionary.

        Returns:
        ----------
            * dict: The ShadeReviveProperties dictionary.
        """

        d = {}
        t = "ShadeReviveProperties" if not abridged else "ShadeRevivePropertiesAbridged"
        d.update({"type": t})
        d.update({"id_num": self.id_num})

        return {"revive": d}

    @classmethod
    def from_dict(cls, data, host):
        # type: (dict, Shade | None) -> ShadeReviveProperties
        """Create a ShadeReviveProperties object from a dictionary.

        Arguments:
        ----------
            * data (dict): A dictionary with the ShadeReviveProperties properties.
            * host (Any): The host object for the properties.

        Returns:
        ----------
            * ShadeReviveProperties: The ShadeReviveProperties object.
        """

        assert data["type"] == "ShadeReviveProperties", "Expected ShadeReviveProperties. Got {}.".format(data["type"])

        new_prop = cls(host)
        new_prop.id_num = data.get("id_num", 0)

        return new_prop


def get_revive_prop_from_space(_shade):
    # type: (Shade) -> ShadeReviveProperties
    """Get the HB-Shade's Phius REVIVE-Properties."""
    return getattr(_shade.properties, "revive")
