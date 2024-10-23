"""
Drawers for labels on plots.
"""

from enum import Enum

__all__ = ("TextAlignment",)

#####################################################################


class TextAlignment(Enum):
    """Text alignment constants."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
