
"""
Module containing class with colors
"""

class Colors:
    """
    Class that contains colors used for TorBot in terminal and a method
    that adds colr to a string

    Attributes:
        _colors (dict): A map containing all of the color codes needed
    """
    def __init__(self):
        self._colors = {
            'white':    "\033[1;37m",
            'yellow':   "\033[1;33m",
            'green':    "\033[1;32m",
            'blue':     "\033[1;34m",
            'cyan':     "\033[1;36m",
            'red':      "\033[1;31m",
            'magenta':  "\033[1;35m",
            'black':      "\033[1;30m",
            'darkwhite':  "\033[0;37m",
            'darkyellow': "\033[0;33m",
            'darkgreen':  "\033[0;32m",
            'darkblue':   "\033[0;34m",
            'darkcyan':   "\033[0;36m",
            'darkred':    "\033[0;31m",
            'darkmagenta':"\033[0;35m",
            'darkblack':  "\033[0;30m",
            'end':        "\033[0;0m"
        }

    def add(self, string, color):
        """
        Method that adds color to a given string

        Args:
            string (str): string to add color to
            color (str): string of color to add
        """
        return self.get(color) + string + self.get('end')

    def get(self, color):
        """
        Method that returns the color code of the given color string

        Args:
            color (str): color code to be returned
        """
        return self._colors[color]
