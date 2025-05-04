"""
Anchor points
"""
from enum import Enum

class Anchor(Enum):
    TOP_LEFT = (0, 0)
    TOP_CENTER = (0.5, 0)
    TOP_RIGHT = (1, 0)
    MIDDLE_LEFT = (0, 0.5)
    CENTER = (0.5, 0.5)
    MIDDLE_RIGHT = (1, 0.5)
    BOTTOM_LEFT = (0, 1)
    BOTTOM_CENTER = (0.5, 1)
    BOTTOM_RIGHT = (1, 1)