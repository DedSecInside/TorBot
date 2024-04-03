"""
Module containing class with colors
"""
COLORS = {
    "white": "\033[1;37m",
    "yellow": "\033[1;33m",
    "green": "\033[1;32m",
    "blue": "\033[1;34m",
    "cyan": "\033[1;36m",
    "red": "\033[1;31m",
    "magenta": "\033[1;35m",
    "black": "\033[1;30m",
    "darkwhite": "\033[0;37m",
    "darkyellow": "\033[0;33m",
    "darkgreen": "\033[0;32m",
    "darkblue": "\033[0;34m",
    "darkcyan": "\033[0;36m",
    "darkred": "\033[0;31m",
    "darkmagenta": "\033[0;35m",
    "darkblack": "\033[0;30m",
    "end": "\033[0;0m",
}


class color:
    """
    Class that contains colors used for TorBot in terminal and a method
    that adds color to a string.

    Attributes:
        message (string): Message to be wrapped in color.
        selected (string): Color to be displayed.
    """

    def __init__(self, message, selected):
        """Initialise color object with specified text and selected color."""
        self._msg = message
        self._color = COLORS[selected]

    def __str__(self):
        return self._color + self._msg + COLORS["end"]

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)
