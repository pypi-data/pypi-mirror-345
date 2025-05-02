# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""This is called during __init__ and extends the base honeybee class Properties with a new '._revive' slot"""

from honeybee.properties import ApertureProperties, FaceProperties, ModelProperties, RoomProperties, ShadeProperties

from .properties.aperture import ApertureReviveProperties
from .properties.face import FaceReviveProperties
from .properties.model import ModelReviveProperties
from .properties.room import RoomReviveProperties
from .properties.shade import ShadeReviveProperties

# Step 1)
# set a private '._revive' attribute on each relevant HB-Core Property class to None

setattr(ModelProperties, "_revive", None)
setattr(RoomProperties, "_revive", None)
setattr(FaceProperties, "_revive", None)
setattr(ApertureProperties, "_revive", None)
setattr(ShadeProperties, "_revive", None)

# Step 2)
# create methods to define the public '.revive' property instances on each obj.properties container


def model_revive_properties(self):
    if self._revive is None:
        self._revive = ModelReviveProperties(self.host)
    return self._revive


def room_revive_properties(self):
    if self._revive is None:
        self._revive = RoomReviveProperties(self.host)
    return self._revive


def face_revive_properties(self):
    if self._revive is None:
        self._revive = FaceReviveProperties(self.host)
    return self._revive


def aperture_revive_properties(self):
    if self._revive is None:
        self._revive = ApertureReviveProperties(self.host)
    return self._revive


def shade_revive_properties(self):
    if self._revive is None:
        self._revive = ShadeReviveProperties(self.host)
    return self._revive


# Step 3)
# add public '.revive' property methods to all the Properties classes
setattr(ModelProperties, "revive", property(model_revive_properties))
setattr(RoomProperties, "revive", property(room_revive_properties))
setattr(FaceProperties, "revive", property(face_revive_properties))
setattr(ApertureProperties, "revive", property(aperture_revive_properties))
setattr(ShadeProperties, "revive", property(shade_revive_properties))
