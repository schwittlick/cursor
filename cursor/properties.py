from __future__ import annotations

from enum import Enum, auto


class Property(Enum):
    LAYER = auto()
    LINETYPE = auto()
    VELOCITY = auto()
    PEN_FORCE = auto()
    PEN_SELECT = auto()
    IS_POLY = auto()
    LASER_PWM = auto()
    LASER_ONOFF = "laser"
    LASER_VOLT = "volt"
    LASER_AMP = "amp"
    LASER_DELAY = "delay"
    LASER_Z = "z"
    # below used for jpeg renderer
    COLOR = "color"
    WIDTH = "width"
    RADIUS = "radius"
