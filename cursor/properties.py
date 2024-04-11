from __future__ import annotations

from enum import Enum


class Property(str, Enum):
    LAYER = "layer"
    LINE_TYPE = "linetype"
    VELOCITY = "velocity"
    PEN_FORCE = "penforce"
    PEN_SELECT = "penselect"
    IS_POLY = "ispoly"
    LASER_PWM = "pwm"
    LASER_ONOFF = "laser"
    LASER_VOLT = "volt"
    LASER_AMP = "amp"
    LASER_DELAY = "delay"
    LASER_Z = "z"
    # below used for jpeg renderer
    COLOR = "color"
    WIDTH = "width"
    RADIUS = 'radius'
    TAGS = 'tags'
