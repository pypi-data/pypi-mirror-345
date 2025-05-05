"""
Various bond-type specific settings.
"""

from collections import namedtuple
from enum import Enum

BondSettings = namedtuple(
    "BondSettings", ["detection_threshold", "radius_scale", "color"]
)


class BondType(Enum):
    SINGLE = BondSettings(1.0, 1.0, "#d3d3d3")
    COORDINATION = BondSettings(1.3, 0.6, "#c20cbe")
