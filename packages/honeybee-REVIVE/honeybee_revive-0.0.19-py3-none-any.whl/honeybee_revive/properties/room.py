# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""HB-Room Phius REVIVE Properties."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass  # Python 2.7

try:
    if TYPE_CHECKING:
        from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

# -----------------------------------------------------------------------------


class RoomReviveProperties(object):
    def __init__(self, _host):
        # type: (Room | None) -> None
        self._host = _host
        self.id_num = 0

    @property
    def host(self):
        # type: () -> Room | None
        return self._host

    @property
    def host_name(self):
        # type: () -> str
        return self.host.display_name if self.host else "No Host"

    def duplicate(self, new_host=None):
        # type: (Room | None) -> RoomReviveProperties
        """Create a duplicate of the RoomReviveProperties object.

        Arguments:
        ----------
            * new_host (Any): The new host for the properties.

        Returns:
        ----------
            * RoomReviveProperties: The duplicated RoomReviveProperties object.
        """

        _host = new_host or self._host
        new_obj = RoomReviveProperties(_host)
        new_obj.id_num = self.id_num
        return new_obj

    def __copy__(self):
        # type: () -> RoomReviveProperties
        return self.duplicate()

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return "HB-Room Phius REVIVE Property: [host: {}]".format(self.host_name)

    def __str__(self):
        return self.__repr__()

    def to_dict(self, abridged=False):
        # type: (bool) -> dict
        """Convert the RoomReviveProperties object to a dictionary.

        Arguments:
        ----------
            * abridged (bool): Set to True to return an abridged version of the dictionary.

        Returns:
        ----------
            * dict: The RoomReviveProperties dictionary.
        """

        d = {}

        if abridged == False:
            d["type"] = "RoomReviveProperties"
            d["id_num"] = self.id_num
        else:
            d["type"] = "RoomRevivePropertiesAbridged"

        return {"revive": d}

    @classmethod
    def from_dict(cls, _input_dict, host):
        # type: (dict, Room | None) -> RoomReviveProperties
        """Create a RoomReviveProperties object from a dictionary.

        Arguments:
        ----------
            * _input_dict (dict): A dictionary with the RoomRevivePropertiesAbridged properties.

        Returns:
        ----------
            * RoomReviveProperties: The RoomReviveProperties object.
        """

        assert _input_dict["type"] == "RoomReviveProperties", "Expected RoomReviveProperties. Got {}.".format(
            _input_dict["type"]
        )
        new_prop = cls(host)
        new_prop.id_num = _input_dict.get("id_num", 0)
        return new_prop

    def apply_properties_from_dict(self, room_prop_dict):
        # type: (dict) -> None
        """Apply properties from a RoomRevivePropertiesAbridged dictionary.

        Arguments:
        ----------
            * room_prop_dict (dict): A RoomRevivePropertiesAbridged dictionary loaded from
                the room object itself. Unabridged. In Abridged form, this
                dict will just include the 'revive_bldg_segment_id' reference instead of the
                the entire properties data dict.

        Returns:
        --------
            * None
        """
        return None


def get_revive_prop_from_space(_room):
    # type: (Room) -> RoomReviveProperties
    """Get the HB-Room's Phius REVIVE-Properties."""
    return getattr(_room.properties, "revive")
