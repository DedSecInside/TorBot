# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Color handling functions.
"""

from abc import ABCMeta, abstractmethod
from math import ceil

__all__ = (
    "Palette",
    "GradientPalette",
    "AdvancedGradientPalette",
    "RainbowPalette",
    "PrecalculatedPalette",
    "ClusterColoringPalette",
    "color_name_to_rgb",
    "color_name_to_rgba",
    "hsv_to_rgb",
    "hsva_to_rgba",
    "hsl_to_rgb",
    "hsla_to_rgba",
    "rgb_to_hsv",
    "rgba_to_hsva",
    "rgb_to_hsl",
    "rgba_to_hsla",
    "palettes",
    "default_edge_colors",
    "known_colors",
)


class Palette(metaclass=ABCMeta):
    """Base class of color palettes.

    Color palettes are mappings that assign integers from the range
    0..M{n-1} to colors (4-tuples). M{n} is called the size or length
    of the palette. C{igraph} comes with a number of predefined palettes,
    so this class is useful for you only if you want to define your
    own palette. This can be done by subclassing this class and implementing
    the L{Palette._get} method as necessary.

    Palettes can also be used as lists or dicts, for the C{__getitem__}
    method is overridden properly to call L{Palette.get}.
    """

    def __init__(self, n):
        self._length = n
        self._cache = {}

    def clear_cache(self):
        """Clears the result cache.

        The return values of L{Palette.get} are cached. Use this method
        to clear the cache.
        """
        self._cache = {}

    def get(self, v):
        """Returns the given color from the palette.

        Values are cached: if the specific value given has already been
        looked up, its value will be returned from the cache instead of
        calculating it again. Use L{Palette.clear_cache} to clear the cache
        if necessary.

        @note: you shouldn't override this method in subclasses, override
          L{_get} instead. If you override this method, lookups in the
          L{known_colors} dict won't work, so you won't be able to refer to
          colors by names or RGBA quadruplets, only by integer indices. The
          caching functionality will disappear as well. However,
          feel free to override this method if this is exactly the behaviour
          you want.

        @param v: the color to be retrieved. If it is an integer, it is
          passed to L{Palette._get} to be translated to an RGBA quadruplet.
          Otherwise it is passed to L{color_name_to_rgb()} to determine the
          RGBA values.

        @return: the color as an RGBA quadruplet"""
        if isinstance(v, list):
            v = tuple(v)
        try:
            return self._cache[v]
        except KeyError:
            pass
        if isinstance(v, str):
            result = color_name_to_rgba(v)
        elif hasattr(v, "__iter__"):    # lists, tuples etc
            return v   # no need to cache
        else:
            if v < 0:
                raise IndexError("color index must be non-negative")
            if v >= self._length:
                raise IndexError("color index too large")
            result = self._get(v)
        self._cache[v] = result
        return result

    def get_many(self, colors):
        """Returns multiple colors from the palette.

        Values are cached: if the specific value given has already been
        looked upon, its value will be returned from the cache instead of
        calculating it again. Use L{Palette.clear_cache} to clear the cache
        if necessary.

        @param colors: the list of colors to be retrieved. The palette class
          tries to make an educated guess here: if it is not possible to
          interpret the value you passed here as a list of colors, the
          class will simply try to interpret it as a single color by
          forwarding the value to L{Palette.get}.
        @return: the colors as a list of RGBA quadruplets. The result will
          be a list even if you passed a single color index or color name.
        """
        if isinstance(colors, (str, int)):
            # Single color name or index
            return [self.get(colors)]
        # Multiple colors
        return [self.get(color) for color in colors]

    @abstractmethod
    def _get(self, v):
        """Override this method in a subclass to create a custom palette.

        You can safely assume that v is an integer in the range 0..M{n-1}
        where M{n} is the size of the palette.

        @param v: numerical index of the color to be retrieved
        @return: a 4-tuple containing the RGBA values"""
        raise NotImplementedError

    __getitem__ = get

    @property
    def length(self):
        """Returns the number of colors in this palette"""
        return self._length

    def __len__(self):
        """Returns the number of colors in this palette"""
        return self._length

    def __plot__(self, backend, context, *args, **kwds):
        """Plots the colors of the palette on the given Cairo context/mpl Axes

        Supported keywork arguments in both Cairo and matplotlib are:

          - C{orientation}: the orientation of the palette. Must be one of
            the following values: C{left-right}, C{bottom-top}, C{right-left}
            or C{top-bottom}. Possible aliases: C{horizontal} = C{left-right},
            C{vertical} = C{bottom-top}, C{lr} = C{left-right},
            C{rl} = C{right-left}, C{tb} = C{top-bottom}, C{bt} = C{bottom-top}.
            The default is C{left-right}.

        Additional supported keyword arguments in Cairo are:

          - C{border_width}: line width of the border shown around the palette.
            If zero or negative, the border is turned off. Default is C{1}.

          - C{grid_width}: line width of the grid that separates palette cells.
            If zero or negative, the grid is turned off. The grid is also
            turned off if the size of a cell is less than three times the given
            line width. Default is C{0}.  Fractional widths are also allowed.

        Keyword arguments in matplotlib are passes to Axes.imshow.
        """
        from igraph.drawing import DrawerDirectory

        drawer = DrawerDirectory.resolve(self, backend)(context)
        drawer.draw(self, **kwds)

    def __repr__(self):
        return "<%s with %d colors>" % (self.__class__.__name__, self._length)


class GradientPalette(Palette):
    """Base class for gradient palettes

    Gradient palettes contain a gradient between two given colors.

    Example:

      >>> pal = GradientPalette("red", "blue", 5)
      >>> pal.get(0)
      (1.0, 0.0, 0.0, 1.0)
      >>> pal.get(2)
      (0.5, 0.0, 0.5, 1.0)
      >>> pal.get(4)
      (0.0, 0.0, 1.0, 1.0)
    """

    def __init__(self, color1, color2, n=256):
        """Creates a gradient palette.

        @param color1: the color where the gradient starts.
        @param color2: the color where the gradient ends.
        @param n: the number of colors in the palette.
        """
        super().__init__(n)
        self._color1 = color_name_to_rgba(color1)
        self._color2 = color_name_to_rgba(color2)

    def _get(self, v):
        """Returns the color corresponding to the given color index.

        @param v: numerical index of the color to be retrieved
        @return: a 4-tuple containing the RGBA values"""
        ratio = float(v) / (len(self) - 1)
        return tuple(
            self._color1[x] * (1 - ratio) + self._color2[x] * ratio for x in range(4)
        )


class AdvancedGradientPalette(Palette):
    """Advanced gradient that consists of more than two base colors.

    Example:

      >>> pal = AdvancedGradientPalette(["red", "black", "blue"], n=9)
      >>> pal.get(2)
      (0.5, 0.0, 0.0, 1.0)
      >>> pal.get(7)
      (0.0, 0.0, 0.75, 1.0)
    """

    def __init__(self, colors, indices=None, n=256):
        """Creates an advanced gradient palette

        @param colors: the colors in the gradient.
        @param indices: the color indices belonging to the given colors. If
          C{None}, the colors are distributed equidistantly
        @param n: the total number of colors in the palette
        """
        super().__init__(n)

        if indices is None:
            diff = float(n - 1) / (len(colors) - 1)
            indices = [i * diff for i in range(len(colors))]
        elif not hasattr(indices, "__iter__"):
            indices = [float(x) for x in indices]
        self._indices, self._colors = list(zip(*sorted(zip(indices, colors))))
        self._colors = [color_name_to_rgba(color) for color in self._colors]
        self._dists = [
            curr - prev for curr, prev in zip(self._indices[1:], self._indices)
        ]

    def _get(self, v):
        """Returns the color corresponding to the given color index.

        @param v: numerical index of the color to be retrieved
        @return: a 4-tuple containing the RGBA values"""
        colors = self._colors
        for i in range(len(self._indices) - 1):
            if self._indices[i] <= v and self._indices[i + 1] >= v:
                dist = self._dists[i]
                ratio = float(v - self._indices[i]) / dist
                return tuple(
                    [
                        colors[i][x] * (1 - ratio) + colors[i + 1][x] * ratio
                        for x in range(4)
                    ]
                )
        return (0.0, 0.0, 0.0, 1.0)


class RainbowPalette(Palette):
    """A palette that varies the hue of the colors along a scale.

    Colors in a rainbow palette all have the same saturation, value and
    alpha components, while the hue is varied between two given extremes
    linearly. This palette has the advantage that it wraps around nicely
    if the hue is varied between zero and one (which is the default).

    Example:

        >>> pal = RainbowPalette(n=120)
        >>> pal.get(0)
        (1.0, 0.0, 0.0, 1.0)
        >>> pal.get(20)
        (1.0, 1.0, 0.0, 1.0)
        >>> pal.get(40)
        (0.0, 1.0, 0.0, 1.0)
        >>> pal = RainbowPalette(n=120, s=1, v=0.5, alpha=0.75)
        >>> pal.get(60)
        (0.0, 0.5, 0.5, 0.75)
        >>> pal.get(80)
        (0.0, 0.0, 0.5, 0.75)
        >>> pal.get(100)
        (0.5, 0.0, 0.5, 0.75)
        >>> pal = RainbowPalette(n=120)
        >>> pal2 = RainbowPalette(n=120, start=0.5, end=0.5)
        >>> pal.get(60) == pal2.get(0)
        True
        >>> pal.get(90) == pal2.get(30)
        True

    This palette was modeled after the C{rainbow} command of R.
    """

    def __init__(self, n=256, s=1, v=1, start=0, end=1, alpha=1):
        """Creates a rainbow palette.

        @param n: the number of colors in the palette.
        @param s: the saturation of the colors in the palette.
        @param v: the value component of the colors in the palette.
        @param start: the hue at which the rainbow begins (between 0 and 1).
        @param end: the hue at which the rainbow ends (between 0 and 1).
        @param alpha: the alpha component of the colors in the palette.
        """
        super().__init__(n)
        self._s = float(clamp(s, 0, 1))
        self._v = float(clamp(v, 0, 1))
        self._alpha = float(clamp(alpha, 0, 1))
        self._start = float(start)
        if end == self._start:
            end += 1
        self._dh = (end - self._start) / n

    def _get(self, v):
        """Returns the color corresponding to the given color index.

        @param v: numerical index of the color to be retrieved
        @return: a 4-tuple containing the RGBA values"""
        return hsva_to_rgba(self._start + v * self._dh, self._s, self._v, self._alpha)


class PrecalculatedPalette(Palette):
    """A palette that returns colors from a pre-calculated list of colors"""

    def __init__(self, items):
        """Creates the palette backed by the given list. The list must contain
        RGBA quadruplets or color names, which will be resolved first by
        L{color_name_to_rgba()}. Anything that is understood by
        L{color_name_to_rgba()} is OK here."""
        super().__init__(len(items))
        for idx, color in enumerate(items):
            if isinstance(color, str):
                color = color_name_to_rgba(color)
            self._cache[idx] = color

    def _get(self, v):
        """This method will only be called if the requested color index is
        outside the size of the palette. In that case, we throw an exception"""
        raise ValueError("palette index outside bounds: %s" % v)


class ClusterColoringPalette(PrecalculatedPalette):
    """A palette suitable for coloring vertices when plotting a clustering.

    This palette tries to make sure that the colors are easily distinguishable.
    This is achieved by using a set of base colors and their lighter and darker
    variants, depending on the number of elements in the palette.

    When the desired size of the palette is less than or equal to the number of
    base colors (denoted by M{n}), only the bsae colors will be used. When the
    size of the palette is larger than M{n} but less than M{2*n}, the base colors
    and their lighter variants will be used. Between M{2*n} and M{3*n}, the
    base colors and their lighter and darker variants will be used. Above M{3*n},
    more darker and lighter variants will be generated, but this makes the individual
    colors less and less distinguishable.
    """

    def __init__(self, n):
        base_colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "#808080"]
        base_colors = [color_name_to_rgba(name) for name in base_colors]

        num_base_colors = len(base_colors)
        colors = base_colors[:]

        blocks_to_add = ceil(float(n - num_base_colors) / num_base_colors)
        ratio_increment = 1.0 / (ceil(blocks_to_add / 2.0) + 1)

        adding_darker = True
        ratio = ratio_increment
        while len(colors) < n:
            if adding_darker:
                new_block = [darken(color, ratio) for color in base_colors]
            else:
                new_block = [lighten(color, ratio) for color in base_colors]
                ratio += ratio_increment
            colors.extend(new_block)
            adding_darker = not adding_darker

        colors = colors[0:n]
        super().__init__(colors)


def clamp(value, min_value, max_value):
    """Clamps the given value between min and max"""
    if value > max_value:
        return max_value
    if value < min_value:
        return min_value
    return value


def color_name_to_rgb(color, palette=None):
    """Converts a color given in one of the supported color formats to
    R-G-B values.

    This is done by calling L{color_name_to_rgba} and then throwing away
    the alpha value.

    @see: color_name_to_rgba for more details about what formats are
      understood by this function.
    """
    return color_name_to_rgba(color, palette)[:3]


def color_name_to_rgba(color, palette=None):
    """Converts a color given in one of the supported color formats to
    R-G-B-A values.

    Examples:

      >>> color_name_to_rgba("red")
      (1.0, 0.0, 0.0, 1.0)
      >>> color_name_to_rgba("#ff8000") == (1.0, 128/255.0, 0.0, 1.0)
      True
      >>> color_name_to_rgba("#ff800080") == (1.0, 128/255.0, 0.0, 128/255.0)
      True
      >>> color_name_to_rgba("#08f") == (0.0, 136/255.0, 1.0, 1.0)
      True
      >>> color_name_to_rgba("rgb(100%, 50%, 0%)")
      (1.0, 0.5, 0.0, 1.0)
      >>> color_name_to_rgba("rgba(100%, 50%, 0%, 25%)")
      (1.0, 0.5, 0.0, 0.25)
      >>> color_name_to_rgba("hsla(120, 100%, 50%, 0.5)")
      (0.0, 1.0, 0.0, 0.5)
      >>> color_name_to_rgba("hsl(60, 100%, 50%)")
      (1.0, 1.0, 0.0, 1.0)
      >>> color_name_to_rgba("hsv(60, 100%, 100%)")
      (1.0, 1.0, 0.0, 1.0)

    @param color: the color to be converted in one of the following formats:
      - B{CSS3 color specification}: C{#rrggbb}, C{#rgb}, C{#rrggbbaa}, C{#rgba},
        C{rgb(red, green, blue)}, C{rgba(red, green, blue, alpha)},
        C{hsl(hue, saturation, lightness)}, C{hsla(hue, saturation, lightness, alpha)},
        C{hsv(hue, saturation, value)} and C{hsva(hue, saturation, value, alpha)}
        where the components are given as hexadecimal numbers in the first four
        cases and as decimals or percentages (0%-100%) in the remaining cases.
        Red, green and blue components are between 0 and 255; hue is between 0
        and 360; saturation, lightness and value is between 0 and 100; alpha is
        between 0 and 1.
      - B{Valid HTML color names}, i.e. those that are present in the HTML 4.0
        specification
      - B{Valid X11 color names}, see U{http://en.wikipedia.org/wiki/X11_color_names}
      - B{Red-green-blue components} given separately in either a comma-, slash- or
        whitespace-separated string or a list or a tuple, in the range of 0-255.
        An alpha value of 255 (maximal opacity) will be assumed.
      - B{Red-green-blue-alpha components} given separately in either a comma-, slash-
        or whitespace-separated string or a list or a tuple, in the range of 0-255
      - B{A single palette index} given either as a string or a number. Uses
        the palette given in the C{palette} parameter of the method call.
    @param palette: the palette to be used if a single number is passed to
      the method. Must be an instance of L{colors.Palette}.

    @return: the RGBA values corresponding to the given color in a 4-tuple.
      Since these colors are primarily used by Cairo routines, the tuples
      contain floats in the range 0.0-1.0
    """
    if not isinstance(color, str):
        if hasattr(color, "__iter__"):
            components = list(color)
        else:
            # A single index is given as a number
            try:
                components = palette.get(color)
            except AttributeError:
                raise ValueError("palette index used when no palette was given") from None
        if len(components) < 4:
            components += [1.0] * (4 - len(components))
    else:
        if color[0] == "#":
            color = color[1:]
            if len(color) == 3:
                components = [int(i, 16) * 17.0 / 255.0 for i in color]
                components.append(1.0)
            elif len(color) == 4:
                components = [int(i, 16) * 17.0 / 255.0 for i in color]
            elif len(color) == 6:
                components = [int(color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
                components.append(1.0)
            elif len(color) == 8:
                components = [int(color[i : i + 2], 16) / 255.0 for i in (0, 2, 4, 6)]
        elif color.lower() in known_colors:
            components = known_colors[color.lower()]
        else:
            color_mode = "rgba"
            maximums = (255.0, 255.0, 255.0, 1.0)
            for mode in ["rgb(", "rgba(", "hsv(", "hsva(", "hsl(", "hsla("]:
                if color.startswith(mode) and color[-1] == ")":
                    color = color[len(mode) : -1]
                    color_mode = mode[:-1]
                    if mode[0] == "h":
                        maximums = (360.0, 100.0, 100.0, 1.0)
                    break

            if " " in color or "/" in color or "," in color:
                color = color.replace(",", " ").replace("/", " ")
                components = color.split()
                for idx, comp in enumerate(components):
                    if comp[-1] == "%":
                        components[idx] = float(comp[:-1]) / 100.0
                    else:
                        components[idx] = float(comp) / maximums[idx]
                if len(components) < 4:
                    components += [1.0] * (4 - len(components))
                if color_mode[:3] == "hsv":
                    components = hsva_to_rgba(*components)
                elif color_mode[:3] == "hsl":
                    components = hsla_to_rgba(*components)
            else:
                components = palette.get(int(color))

    # At this point, the components are floats
    return tuple(clamp(val, 0.0, 1.0) for val in components)


def color_to_html_format(color):
    """Formats a color given as a 3-tuple or 4-tuple in HTML format.

    The HTML format is simply given by C{#rrggbbaa}, where C{rr} gives
    the red component in hexadecimal format, C{gg} gives the green
    component C{bb} gives the blue component and C{gg} gives the
    alpha level. The alpha level is optional.
    """
    color = [int(clamp(component * 256, 0, 255)) for component in color]
    if len(color) == 4:
        return "#{0:02X}{1:02X}{2:02X}{3:02X}".format(*color)
    return "#{0:02X}{1:02X}{2:02X}".format(*color)


def darken(color, ratio=0.5):
    """Creates a darker version of a color given by an RGB triplet.

    This is done by mixing the original color with black using the given
    ratio. A ratio of 1.0 will yield a completely black color, a ratio
    of 0.0 will yield the original color. The alpha values are left intact.
    """
    ratio = 1.0 - ratio
    red, green, blue, alpha = color
    return (red * ratio, green * ratio, blue * ratio, alpha)


def hsla_to_rgba(h, s, l, alpha=1.0):  # noqa: E741
    """Converts a color given by its HSLA coordinates (hue, saturation,
    lightness, alpha) to RGBA coordinates.

    Each of the HSLA coordinates must be in the range [0, 1].
    """
    # This is based on the formulae found at:
    # http://en.wikipedia.org/wiki/HSL_and_HSV
    c = s * (1 - 2 * abs(l - 0.5))
    h1 = (h * 6) % 6
    x = c * (1 - abs(h1 % 2 - 1))
    m = l - c / 2.0
    h1 = int(h1)
    if h1 < 3:
        if h1 < 1:
            return (c + m, x + m, m, alpha)
        elif h1 < 2:
            return (x + m, c + m, m, alpha)
        else:
            return (m, c + m, x + m, alpha)
    else:
        if h1 < 4:
            return (m, x + m, c + m, alpha)
        elif h1 < 5:
            return (x + m, m, c + m, alpha)
        else:
            return (c + m, m, x + m, alpha)


def hsl_to_rgb(h, s, l):  # noqa: E741
    """Converts a color given by its HSL coordinates (hue, saturation,
    lightness) to RGB coordinates.

    Each of the HSL coordinates must be in the range [0, 1].
    """
    return hsla_to_rgba(h, s, l)[:3]


def hsva_to_rgba(h, s, v, alpha=1.0):
    """Converts a color given by its HSVA coordinates (hue, saturation,
    value, alpha) to RGB coordinates.

    Each of the HSVA coordinates must be in the range [0, 1].
    """
    # This is based on the formulae found at:
    # http://en.wikipedia.org/wiki/HSL_and_HSV
    c = v * s
    h1 = (h * 6) % 6
    x = c * (1 - abs(h1 % 2 - 1))
    m = v - c
    h1 = int(h1)
    if h1 < 3:
        if h1 < 1:
            return (c + m, x + m, m, alpha)
        elif h1 < 2:
            return (x + m, c + m, m, alpha)
        else:
            return (m, c + m, x + m, alpha)
    else:
        if h1 < 4:
            return (m, x + m, c + m, alpha)
        elif h1 < 5:
            return (x + m, m, c + m, alpha)
        else:
            return (c + m, m, x + m, alpha)


def hsv_to_rgb(h, s, v):
    """Converts a color given by its HSV coordinates (hue, saturation,
    value) to RGB coordinates.

    Each of the HSV coordinates must be in the range [0, 1].
    """
    return hsva_to_rgba(h, s, v)[:3]


def rgba_to_hsla(r, g, b, alpha=1.0):
    """Converts a color given by its RGBA coordinates to HSLA coordinates
    (hue, saturation, lightness, alpha).

    Each of the RGBA coordinates must be in the range [0, 1].
    """
    alpha = float(alpha)
    rgb_min, rgb_max = float(min(r, g, b)), float(max(r, g, b))

    if rgb_min == rgb_max:
        return 0.0, 0.0, rgb_min, alpha

    lightness = (rgb_min + rgb_max) / 2.0
    d = rgb_max - rgb_min
    if lightness > 0.5:
        sat = d / (2 - rgb_max - rgb_min)
    else:
        sat = d / (rgb_max + rgb_min)

    d *= 6.0
    if rgb_max == r:
        hue = (g - b) / d
        if g < b:
            hue += 1
    elif rgb_max == g:
        hue = 1 / 3.0 + (b - r) / d
    else:
        hue = 2 / 3.0 + (r - g) / d
    return hue, sat, lightness, alpha


def rgba_to_hsva(r, g, b, alpha=1.0):
    """Converts a color given by its RGBA coordinates to HSVA coordinates
    (hue, saturation, value, alpha).

    Each of the RGBA coordinates must be in the range [0, 1].
    """
    # This is based on the formulae found at:
    # http://en.literateprograms.org/RGB_to_HSV_color_space_conversion_(C)
    rgb_min, rgb_max = float(min(r, g, b)), float(max(r, g, b))
    alpha = float(alpha)
    value = float(rgb_max)
    if value <= 0:
        return 0.0, 0.0, 0.0, alpha
    sat = 1.0 - rgb_min / value
    if sat <= 0:
        return 0.0, 0.0, value, alpha
    d = rgb_max - rgb_min
    r = (r - rgb_min) / d
    g = (g - rgb_min) / d
    b = (b - rgb_min) / d
    rgb_max = max(r, g, b)
    if rgb_max == r:
        hue = 0.0 + (g - b) / 6.0
        if hue < 0:
            hue += 1
    elif rgb_max == g:
        hue = 1 / 3.0 + (b - r) / 6.0
    else:
        hue = 2 / 3.0 + (r - g) / 6.0
    return hue, sat, value, alpha


def rgb_to_hsl(r, g, b):
    """Converts a color given by its RGB coordinates to HSL coordinates
    (hue, saturation, lightness).

    Each of the RGB coordinates must be in the range [0, 1].
    """
    return rgba_to_hsla(r, g, b)[:3]


def rgb_to_hsv(r, g, b):
    """Converts a color given by its RGB coordinates to HSV coordinates
    (hue, saturation, value).

    Each of the RGB coordinates must be in the range [0, 1].
    """
    return rgba_to_hsva(r, g, b)[:3]


def lighten(color, ratio=0.5):
    """Creates a lighter version of a color given by an RGB triplet.

    This is done by mixing the original color with white using the given
    ratio. A ratio of 1.0 will yield a completely white color, a ratio
    of 0.0 will yield the original color.
    """
    red, green, blue, alpha = color
    return (
        red + (1.0 - red) * ratio,
        green + (1.0 - green) * ratio,
        blue + (1.0 - blue) * ratio,
        alpha,
    )


default_edge_colors = {
    "cairo": ["grey20", "grey80"],
    "matplotlib": ["dimgrey", "silver"],
    "plotly": ["rgb(51,51,51)", "rgb(204,204,204)"],
}


known_colors = {
    "alice blue": (0.94117647058823528, 0.97254901960784312, 1.0, 1.0),
    "aliceblue": (0.94117647058823528, 0.97254901960784312, 1.0, 1.0),
    "antique white": (
        0.98039215686274506,
        0.92156862745098034,
        0.84313725490196079,
        1.0,
    ),
    "antiquewhite": (
        0.98039215686274506,
        0.92156862745098034,
        0.84313725490196079,
        1.0,
    ),
    "antiquewhite1": (1.0, 0.93725490196078431, 0.85882352941176465, 1.0),
    "antiquewhite2": (
        0.93333333333333335,
        0.87450980392156863,
        0.80000000000000004,
        1.0,
    ),
    "antiquewhite3": (
        0.80392156862745101,
        0.75294117647058822,
        0.69019607843137254,
        1.0,
    ),
    "antiquewhite4": (
        0.54509803921568623,
        0.51372549019607838,
        0.47058823529411764,
        1.0,
    ),
    "aqua": (0.0, 1.0, 1.0, 1.0),
    "aquamarine": (0.49803921568627452, 1.0, 0.83137254901960789, 1.0),
    "aquamarine1": (0.49803921568627452, 1.0, 0.83137254901960789, 1.0),
    "aquamarine2": (0.46274509803921571, 0.93333333333333335, 0.77647058823529413, 1.0),
    "aquamarine3": (0.40000000000000002, 0.80392156862745101, 0.66666666666666663, 1.0),
    "aquamarine4": (0.27058823529411763, 0.54509803921568623, 0.45490196078431372, 1.0),
    "azure": (0.94117647058823528, 1.0, 1.0, 1.0),
    "azure1": (0.94117647058823528, 1.0, 1.0, 1.0),
    "azure2": (0.8784313725490196, 0.93333333333333335, 0.93333333333333335, 1.0),
    "azure3": (0.75686274509803919, 0.80392156862745101, 0.80392156862745101, 1.0),
    "azure4": (0.51372549019607838, 0.54509803921568623, 0.54509803921568623, 1.0),
    "beige": (0.96078431372549022, 0.96078431372549022, 0.86274509803921573, 1.0),
    "bisque": (1.0, 0.89411764705882357, 0.7686274509803922, 1.0),
    "bisque1": (1.0, 0.89411764705882357, 0.7686274509803922, 1.0),
    "bisque2": (0.93333333333333335, 0.83529411764705885, 0.71764705882352942, 1.0),
    "bisque3": (0.80392156862745101, 0.71764705882352942, 0.61960784313725492, 1.0),
    "bisque4": (0.54509803921568623, 0.49019607843137253, 0.41960784313725491, 1.0),
    "black": (0.0, 0.0, 0.0, 1.0),
    "blanched almond": (1.0, 0.92156862745098034, 0.80392156862745101, 1.0),
    "blanchedalmond": (1.0, 0.92156862745098034, 0.80392156862745101, 1.0),
    "blue": (0.0, 0.0, 1.0, 1.0),
    "blue violet": (0.54117647058823526, 0.16862745098039217, 0.88627450980392153, 1.0),
    "blue1": (0.0, 0.0, 1.0, 1.0),
    "blue2": (0.0, 0.0, 0.93333333333333335, 1.0),
    "blue3": (0.0, 0.0, 0.80392156862745101, 1.0),
    "blue4": (0.0, 0.0, 0.54509803921568623, 1.0),
    "blueviolet": (0.54117647058823526, 0.16862745098039217, 0.88627450980392153, 1.0),
    "brown": (0.6470588235294118, 0.16470588235294117, 0.16470588235294117, 1.0),
    "brown1": (1.0, 0.25098039215686274, 0.25098039215686274, 1.0),
    "brown2": (0.93333333333333335, 0.23137254901960785, 0.23137254901960785, 1.0),
    "brown3": (0.80392156862745101, 0.20000000000000001, 0.20000000000000001, 1.0),
    "brown4": (0.54509803921568623, 0.13725490196078433, 0.13725490196078433, 1.0),
    "burlywood": (0.87058823529411766, 0.72156862745098038, 0.52941176470588236, 1.0),
    "burlywood1": (1.0, 0.82745098039215681, 0.60784313725490191, 1.0),
    "burlywood2": (0.93333333333333335, 0.77254901960784317, 0.56862745098039214, 1.0),
    "burlywood3": (0.80392156862745101, 0.66666666666666663, 0.49019607843137253, 1.0),
    "burlywood4": (0.54509803921568623, 0.45098039215686275, 0.33333333333333331, 1.0),
    "cadet blue": (0.37254901960784315, 0.61960784313725492, 0.62745098039215685, 1.0),
    "cadetblue": (0.37254901960784315, 0.61960784313725492, 0.62745098039215685, 1.0),
    "cadetblue1": (0.59607843137254901, 0.96078431372549022, 1.0, 1.0),
    "cadetblue2": (0.55686274509803924, 0.89803921568627454, 0.93333333333333335, 1.0),
    "cadetblue3": (0.47843137254901963, 0.77254901960784317, 0.80392156862745101, 1.0),
    "cadetblue4": (0.32549019607843138, 0.52549019607843139, 0.54509803921568623, 1.0),
    "chartreuse": (0.49803921568627452, 1.0, 0.0, 1.0),
    "chartreuse1": (0.49803921568627452, 1.0, 0.0, 1.0),
    "chartreuse2": (0.46274509803921571, 0.93333333333333335, 0.0, 1.0),
    "chartreuse3": (0.40000000000000002, 0.80392156862745101, 0.0, 1.0),
    "chartreuse4": (0.27058823529411763, 0.54509803921568623, 0.0, 1.0),
    "chocolate": (0.82352941176470584, 0.41176470588235292, 0.11764705882352941, 1.0),
    "chocolate1": (1.0, 0.49803921568627452, 0.14117647058823529, 1.0),
    "chocolate2": (0.93333333333333335, 0.46274509803921571, 0.12941176470588237, 1.0),
    "chocolate3": (0.80392156862745101, 0.40000000000000002, 0.11372549019607843, 1.0),
    "chocolate4": (0.54509803921568623, 0.27058823529411763, 0.074509803921568626, 1.0),
    "coral": (1.0, 0.49803921568627452, 0.31372549019607843, 1.0),
    "coral1": (1.0, 0.44705882352941179, 0.33725490196078434, 1.0),
    "coral2": (0.93333333333333335, 0.41568627450980394, 0.31372549019607843, 1.0),
    "coral3": (0.80392156862745101, 0.35686274509803922, 0.27058823529411763, 1.0),
    "coral4": (0.54509803921568623, 0.24313725490196078, 0.18431372549019609, 1.0),
    "cornflower blue": (
        0.39215686274509803,
        0.58431372549019611,
        0.92941176470588238,
        1.0,
    ),
    "cornflowerblue": (
        0.39215686274509803,
        0.58431372549019611,
        0.92941176470588238,
        1.0,
    ),
    "cornsilk": (1.0, 0.97254901960784312, 0.86274509803921573, 1.0),
    "cornsilk1": (1.0, 0.97254901960784312, 0.86274509803921573, 1.0),
    "cornsilk2": (0.93333333333333335, 0.90980392156862744, 0.80392156862745101, 1.0),
    "cornsilk3": (0.80392156862745101, 0.78431372549019607, 0.69411764705882351, 1.0),
    "cornsilk4": (0.54509803921568623, 0.53333333333333333, 0.47058823529411764, 1.0),
    "crimson": (0.8627450980392157, 0.0784313725490196, 0.23529411764705882, 1.0),
    "cyan": (0.0, 1.0, 1.0, 1.0),
    "cyan1": (0.0, 1.0, 1.0, 1.0),
    "cyan2": (0.0, 0.93333333333333335, 0.93333333333333335, 1.0),
    "cyan3": (0.0, 0.80392156862745101, 0.80392156862745101, 1.0),
    "cyan4": (0.0, 0.54509803921568623, 0.54509803921568623, 1.0),
    "dark blue": (0.0, 0.0, 0.54509803921568623, 1.0),
    "dark cyan": (0.0, 0.54509803921568623, 0.54509803921568623, 1.0),
    "dark goldenrod": (
        0.72156862745098038,
        0.52549019607843139,
        0.043137254901960784,
        1.0,
    ),
    "dark gray": (0.66274509803921566, 0.66274509803921566, 0.66274509803921566, 1.0),
    "dark green": (0.0, 0.39215686274509803, 0.0, 1.0),
    "dark grey": (0.66274509803921566, 0.66274509803921566, 0.66274509803921566, 1.0),
    "dark khaki": (0.74117647058823533, 0.71764705882352942, 0.41960784313725491, 1.0),
    "dark magenta": (0.54509803921568623, 0.0, 0.54509803921568623, 1.0),
    "dark olive green": (
        0.33333333333333331,
        0.41960784313725491,
        0.18431372549019609,
        1.0,
    ),
    "dark orange": (1.0, 0.5490196078431373, 0.0, 1.0),
    "dark orchid": (0.59999999999999998, 0.19607843137254902, 0.80000000000000004, 1.0),
    "dark red": (0.54509803921568623, 0.0, 0.0, 1.0),
    "dark salmon": (0.9137254901960784, 0.58823529411764708, 0.47843137254901963, 1.0),
    "dark sea green": (
        0.5607843137254902,
        0.73725490196078436,
        0.5607843137254902,
        1.0,
    ),
    "dark slate blue": (
        0.28235294117647058,
        0.23921568627450981,
        0.54509803921568623,
        1.0,
    ),
    "dark slate gray": (
        0.18431372549019609,
        0.30980392156862746,
        0.30980392156862746,
        1.0,
    ),
    "dark slate grey": (
        0.18431372549019609,
        0.30980392156862746,
        0.30980392156862746,
        1.0,
    ),
    "dark turquoise": (0.0, 0.80784313725490198, 0.81960784313725488, 1.0),
    "dark violet": (0.58039215686274515, 0.0, 0.82745098039215681, 1.0),
    "darkblue": (0.0, 0.0, 0.54509803921568623, 1.0),
    "darkcyan": (0.0, 0.54509803921568623, 0.54509803921568623, 1.0),
    "darkgoldenrod": (
        0.72156862745098038,
        0.52549019607843139,
        0.043137254901960784,
        1.0,
    ),
    "darkgoldenrod1": (1.0, 0.72549019607843135, 0.058823529411764705, 1.0),
    "darkgoldenrod2": (
        0.93333333333333335,
        0.67843137254901964,
        0.054901960784313725,
        1.0,
    ),
    "darkgoldenrod3": (
        0.80392156862745101,
        0.58431372549019611,
        0.047058823529411764,
        1.0,
    ),
    "darkgoldenrod4": (
        0.54509803921568623,
        0.396078431372549,
        0.031372549019607843,
        1.0,
    ),
    "darkgray": (0.66274509803921566, 0.66274509803921566, 0.66274509803921566, 1.0),
    "darkgreen": (0.0, 0.39215686274509803, 0.0, 1.0),
    "darkgrey": (0.66274509803921566, 0.66274509803921566, 0.66274509803921566, 1.0),
    "darkkhaki": (0.74117647058823533, 0.71764705882352942, 0.41960784313725491, 1.0),
    "darkmagenta": (0.54509803921568623, 0.0, 0.54509803921568623, 1.0),
    "darkolivegreen": (
        0.33333333333333331,
        0.41960784313725491,
        0.18431372549019609,
        1.0,
    ),
    "darkolivegreen1": (0.792156862745098, 1.0, 0.4392156862745098, 1.0),
    "darkolivegreen2": (
        0.73725490196078436,
        0.93333333333333335,
        0.40784313725490196,
        1.0,
    ),
    "darkolivegreen3": (
        0.63529411764705879,
        0.80392156862745101,
        0.35294117647058826,
        1.0,
    ),
    "darkolivegreen4": (
        0.43137254901960786,
        0.54509803921568623,
        0.23921568627450981,
        1.0,
    ),
    "darkorange": (1.0, 0.5490196078431373, 0.0, 1.0),
    "darkorange1": (1.0, 0.49803921568627452, 0.0, 1.0),
    "darkorange2": (0.93333333333333335, 0.46274509803921571, 0.0, 1.0),
    "darkorange3": (0.80392156862745101, 0.40000000000000002, 0.0, 1.0),
    "darkorange4": (0.54509803921568623, 0.27058823529411763, 0.0, 1.0),
    "darkorchid": (0.59999999999999998, 0.19607843137254902, 0.80000000000000004, 1.0),
    "darkorchid1": (0.74901960784313726, 0.24313725490196078, 1.0, 1.0),
    "darkorchid2": (0.69803921568627447, 0.22745098039215686, 0.93333333333333335, 1.0),
    "darkorchid3": (0.60392156862745094, 0.19607843137254902, 0.80392156862745101, 1.0),
    "darkorchid4": (0.40784313725490196, 0.13333333333333333, 0.54509803921568623, 1.0),
    "darkred": (0.54509803921568623, 0.0, 0.0, 1.0),
    "darksalmon": (0.9137254901960784, 0.58823529411764708, 0.47843137254901963, 1.0),
    "darkseagreen": (0.5607843137254902, 0.73725490196078436, 0.5607843137254902, 1.0),
    "darkseagreen1": (0.75686274509803919, 1.0, 0.75686274509803919, 1.0),
    "darkseagreen2": (
        0.70588235294117652,
        0.93333333333333335,
        0.70588235294117652,
        1.0,
    ),
    "darkseagreen3": (
        0.60784313725490191,
        0.80392156862745101,
        0.60784313725490191,
        1.0,
    ),
    "darkseagreen4": (
        0.41176470588235292,
        0.54509803921568623,
        0.41176470588235292,
        1.0,
    ),
    "darkslateblue": (
        0.28235294117647058,
        0.23921568627450981,
        0.54509803921568623,
        1.0,
    ),
    "darkslategray": (
        0.18431372549019609,
        0.30980392156862746,
        0.30980392156862746,
        1.0,
    ),
    "darkslategray1": (0.59215686274509804, 1.0, 1.0, 1.0),
    "darkslategray2": (
        0.55294117647058827,
        0.93333333333333335,
        0.93333333333333335,
        1.0,
    ),
    "darkslategray3": (
        0.47450980392156861,
        0.80392156862745101,
        0.80392156862745101,
        1.0,
    ),
    "darkslategray4": (
        0.32156862745098042,
        0.54509803921568623,
        0.54509803921568623,
        1.0,
    ),
    "darkslategrey": (
        0.18431372549019609,
        0.30980392156862746,
        0.30980392156862746,
        1.0,
    ),
    "darkturquoise": (0.0, 0.80784313725490198, 0.81960784313725488, 1.0),
    "darkviolet": (0.58039215686274515, 0.0, 0.82745098039215681, 1.0),
    "deep pink": (1.0, 0.078431372549019607, 0.57647058823529407, 1.0),
    "deep sky blue": (0.0, 0.74901960784313726, 1.0, 1.0),
    "deeppink": (1.0, 0.078431372549019607, 0.57647058823529407, 1.0),
    "deeppink1": (1.0, 0.078431372549019607, 0.57647058823529407, 1.0),
    "deeppink2": (0.93333333333333335, 0.070588235294117646, 0.53725490196078429, 1.0),
    "deeppink3": (0.80392156862745101, 0.062745098039215685, 0.46274509803921571, 1.0),
    "deeppink4": (0.54509803921568623, 0.039215686274509803, 0.31372549019607843, 1.0),
    "deepskyblue": (0.0, 0.74901960784313726, 1.0, 1.0),
    "deepskyblue1": (0.0, 0.74901960784313726, 1.0, 1.0),
    "deepskyblue2": (0.0, 0.69803921568627447, 0.93333333333333335, 1.0),
    "deepskyblue3": (0.0, 0.60392156862745094, 0.80392156862745101, 1.0),
    "deepskyblue4": (0.0, 0.40784313725490196, 0.54509803921568623, 1.0),
    "dim gray": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "dim grey": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "dimgray": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "dimgrey": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "dodger blue": (0.11764705882352941, 0.56470588235294117, 1.0, 1.0),
    "dodgerblue": (0.11764705882352941, 0.56470588235294117, 1.0, 1.0),
    "dodgerblue1": (0.11764705882352941, 0.56470588235294117, 1.0, 1.0),
    "dodgerblue2": (0.10980392156862745, 0.52549019607843139, 0.93333333333333335, 1.0),
    "dodgerblue3": (
        0.094117647058823528,
        0.45490196078431372,
        0.80392156862745101,
        1.0,
    ),
    "dodgerblue4": (
        0.062745098039215685,
        0.30588235294117649,
        0.54509803921568623,
        1.0,
    ),
    "firebrick": (0.69803921568627447, 0.13333333333333333, 0.13333333333333333, 1.0),
    "firebrick1": (1.0, 0.18823529411764706, 0.18823529411764706, 1.0),
    "firebrick2": (0.93333333333333335, 0.17254901960784313, 0.17254901960784313, 1.0),
    "firebrick3": (0.80392156862745101, 0.14901960784313725, 0.14901960784313725, 1.0),
    "firebrick4": (0.54509803921568623, 0.10196078431372549, 0.10196078431372549, 1.0),
    "floral white": (1.0, 0.98039215686274506, 0.94117647058823528, 1.0),
    "floralwhite": (1.0, 0.98039215686274506, 0.94117647058823528, 1.0),
    "forest green": (
        0.13333333333333333,
        0.54509803921568623,
        0.13333333333333333,
        1.0,
    ),
    "forestgreen": (0.13333333333333333, 0.54509803921568623, 0.13333333333333333, 1.0),
    "fuchsia": (1.0, 0.0, 1.0, 1.0),
    "gainsboro": (0.86274509803921573, 0.86274509803921573, 0.86274509803921573, 1.0),
    "ghost white": (0.97254901960784312, 0.97254901960784312, 1.0, 1.0),
    "ghostwhite": (0.97254901960784312, 0.97254901960784312, 1.0, 1.0),
    "gold": (1.0, 0.84313725490196079, 0.0, 1.0),
    "gold1": (1.0, 0.84313725490196079, 0.0, 1.0),
    "gold2": (0.93333333333333335, 0.78823529411764703, 0.0, 1.0),
    "gold3": (0.80392156862745101, 0.67843137254901964, 0.0, 1.0),
    "gold4": (0.54509803921568623, 0.45882352941176469, 0.0, 1.0),
    "goldenrod": (0.85490196078431369, 0.6470588235294118, 0.12549019607843137, 1.0),
    "goldenrod1": (1.0, 0.75686274509803919, 0.14509803921568629, 1.0),
    "goldenrod2": (0.93333333333333335, 0.70588235294117652, 0.13333333333333333, 1.0),
    "goldenrod3": (0.80392156862745101, 0.60784313725490191, 0.11372549019607843, 1.0),
    "goldenrod4": (0.54509803921568623, 0.41176470588235292, 0.078431372549019607, 1.0),
    "gray": (0.74509803921568629, 0.74509803921568629, 0.74509803921568629, 1.0),
    "gray0": (0.0, 0.0, 0.0, 1.0),
    "gray1": (0.011764705882352941, 0.011764705882352941, 0.011764705882352941, 1.0),
    "gray10": (0.10196078431372549, 0.10196078431372549, 0.10196078431372549, 1.0),
    "gray100": (1.0, 1.0, 1.0, 1.0),
    "gray11": (0.10980392156862745, 0.10980392156862745, 0.10980392156862745, 1.0),
    "gray12": (0.12156862745098039, 0.12156862745098039, 0.12156862745098039, 1.0),
    "gray13": (0.12941176470588237, 0.12941176470588237, 0.12941176470588237, 1.0),
    "gray14": (0.14117647058823529, 0.14117647058823529, 0.14117647058823529, 1.0),
    "gray15": (0.14901960784313725, 0.14901960784313725, 0.14901960784313725, 1.0),
    "gray16": (0.16078431372549021, 0.16078431372549021, 0.16078431372549021, 1.0),
    "gray17": (0.16862745098039217, 0.16862745098039217, 0.16862745098039217, 1.0),
    "gray18": (0.1803921568627451, 0.1803921568627451, 0.1803921568627451, 1.0),
    "gray19": (0.18823529411764706, 0.18823529411764706, 0.18823529411764706, 1.0),
    "gray2": (0.019607843137254902, 0.019607843137254902, 0.019607843137254902, 1.0),
    "gray20": (0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 1.0),
    "gray21": (0.21176470588235294, 0.21176470588235294, 0.21176470588235294, 1.0),
    "gray22": (0.2196078431372549, 0.2196078431372549, 0.2196078431372549, 1.0),
    "gray23": (0.23137254901960785, 0.23137254901960785, 0.23137254901960785, 1.0),
    "gray24": (0.23921568627450981, 0.23921568627450981, 0.23921568627450981, 1.0),
    "gray25": (0.25098039215686274, 0.25098039215686274, 0.25098039215686274, 1.0),
    "gray26": (0.25882352941176473, 0.25882352941176473, 0.25882352941176473, 1.0),
    "gray27": (0.27058823529411763, 0.27058823529411763, 0.27058823529411763, 1.0),
    "gray28": (0.27843137254901962, 0.27843137254901962, 0.27843137254901962, 1.0),
    "gray29": (0.29019607843137257, 0.29019607843137257, 0.29019607843137257, 1.0),
    "gray3": (0.031372549019607843, 0.031372549019607843, 0.031372549019607843, 1.0),
    "gray30": (0.30196078431372547, 0.30196078431372547, 0.30196078431372547, 1.0),
    "gray31": (0.30980392156862746, 0.30980392156862746, 0.30980392156862746, 1.0),
    "gray32": (0.32156862745098042, 0.32156862745098042, 0.32156862745098042, 1.0),
    "gray33": (0.32941176470588235, 0.32941176470588235, 0.32941176470588235, 1.0),
    "gray34": (0.3411764705882353, 0.3411764705882353, 0.3411764705882353, 1.0),
    "gray35": (0.34901960784313724, 0.34901960784313724, 0.34901960784313724, 1.0),
    "gray36": (0.36078431372549019, 0.36078431372549019, 0.36078431372549019, 1.0),
    "gray37": (0.36862745098039218, 0.36862745098039218, 0.36862745098039218, 1.0),
    "gray38": (0.38039215686274508, 0.38039215686274508, 0.38039215686274508, 1.0),
    "gray39": (0.38823529411764707, 0.38823529411764707, 0.38823529411764707, 1.0),
    "gray4": (0.039215686274509803, 0.039215686274509803, 0.039215686274509803, 1.0),
    "gray40": (0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 1.0),
    "gray41": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "gray42": (0.41960784313725491, 0.41960784313725491, 0.41960784313725491, 1.0),
    "gray43": (0.43137254901960786, 0.43137254901960786, 0.43137254901960786, 1.0),
    "gray44": (0.4392156862745098, 0.4392156862745098, 0.4392156862745098, 1.0),
    "gray45": (0.45098039215686275, 0.45098039215686275, 0.45098039215686275, 1.0),
    "gray46": (0.45882352941176469, 0.45882352941176469, 0.45882352941176469, 1.0),
    "gray47": (0.47058823529411764, 0.47058823529411764, 0.47058823529411764, 1.0),
    "gray48": (0.47843137254901963, 0.47843137254901963, 0.47843137254901963, 1.0),
    "gray49": (0.49019607843137253, 0.49019607843137253, 0.49019607843137253, 1.0),
    "gray5": (0.050980392156862744, 0.050980392156862744, 0.050980392156862744, 1.0),
    "gray50": (0.49803921568627452, 0.49803921568627452, 0.49803921568627452, 1.0),
    "gray51": (0.50980392156862742, 0.50980392156862742, 0.50980392156862742, 1.0),
    "gray52": (0.52156862745098043, 0.52156862745098043, 0.52156862745098043, 1.0),
    "gray53": (0.52941176470588236, 0.52941176470588236, 0.52941176470588236, 1.0),
    "gray54": (0.54117647058823526, 0.54117647058823526, 0.54117647058823526, 1.0),
    "gray55": (0.5490196078431373, 0.5490196078431373, 0.5490196078431373, 1.0),
    "gray56": (0.5607843137254902, 0.5607843137254902, 0.5607843137254902, 1.0),
    "gray57": (0.56862745098039214, 0.56862745098039214, 0.56862745098039214, 1.0),
    "gray58": (0.58039215686274515, 0.58039215686274515, 0.58039215686274515, 1.0),
    "gray59": (0.58823529411764708, 0.58823529411764708, 0.58823529411764708, 1.0),
    "gray6": (0.058823529411764705, 0.058823529411764705, 0.058823529411764705, 1.0),
    "gray60": (0.59999999999999998, 0.59999999999999998, 0.59999999999999998, 1.0),
    "gray61": (0.61176470588235299, 0.61176470588235299, 0.61176470588235299, 1.0),
    "gray62": (0.61960784313725492, 0.61960784313725492, 0.61960784313725492, 1.0),
    "gray63": (0.63137254901960782, 0.63137254901960782, 0.63137254901960782, 1.0),
    "gray64": (0.63921568627450975, 0.63921568627450975, 0.63921568627450975, 1.0),
    "gray65": (0.65098039215686276, 0.65098039215686276, 0.65098039215686276, 1.0),
    "gray66": (0.6588235294117647, 0.6588235294117647, 0.6588235294117647, 1.0),
    "gray67": (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, 1.0),
    "gray68": (0.67843137254901964, 0.67843137254901964, 0.67843137254901964, 1.0),
    "gray69": (0.69019607843137254, 0.69019607843137254, 0.69019607843137254, 1.0),
    "gray7": (0.070588235294117646, 0.070588235294117646, 0.070588235294117646, 1.0),
    "gray70": (0.70196078431372544, 0.70196078431372544, 0.70196078431372544, 1.0),
    "gray71": (0.70980392156862748, 0.70980392156862748, 0.70980392156862748, 1.0),
    "gray72": (0.72156862745098038, 0.72156862745098038, 0.72156862745098038, 1.0),
    "gray73": (0.72941176470588232, 0.72941176470588232, 0.72941176470588232, 1.0),
    "gray74": (0.74117647058823533, 0.74117647058823533, 0.74117647058823533, 1.0),
    "gray75": (0.74901960784313726, 0.74901960784313726, 0.74901960784313726, 1.0),
    "gray76": (0.76078431372549016, 0.76078431372549016, 0.76078431372549016, 1.0),
    "gray77": (0.7686274509803922, 0.7686274509803922, 0.7686274509803922, 1.0),
    "gray78": (0.7803921568627451, 0.7803921568627451, 0.7803921568627451, 1.0),
    "gray79": (0.78823529411764703, 0.78823529411764703, 0.78823529411764703, 1.0),
    "gray8": (0.078431372549019607, 0.078431372549019607, 0.078431372549019607, 1.0),
    "gray80": (0.80000000000000004, 0.80000000000000004, 0.80000000000000004, 1.0),
    "gray81": (0.81176470588235294, 0.81176470588235294, 0.81176470588235294, 1.0),
    "gray82": (0.81960784313725488, 0.81960784313725488, 0.81960784313725488, 1.0),
    "gray83": (0.83137254901960789, 0.83137254901960789, 0.83137254901960789, 1.0),
    "gray84": (0.83921568627450982, 0.83921568627450982, 0.83921568627450982, 1.0),
    "gray85": (0.85098039215686272, 0.85098039215686272, 0.85098039215686272, 1.0),
    "gray86": (0.85882352941176465, 0.85882352941176465, 0.85882352941176465, 1.0),
    "gray87": (0.87058823529411766, 0.87058823529411766, 0.87058823529411766, 1.0),
    "gray88": (0.8784313725490196, 0.8784313725490196, 0.8784313725490196, 1.0),
    "gray89": (0.8901960784313725, 0.8901960784313725, 0.8901960784313725, 1.0),
    "gray9": (0.090196078431372548, 0.090196078431372548, 0.090196078431372548, 1.0),
    "gray90": (0.89803921568627454, 0.89803921568627454, 0.89803921568627454, 1.0),
    "gray91": (0.90980392156862744, 0.90980392156862744, 0.90980392156862744, 1.0),
    "gray92": (0.92156862745098034, 0.92156862745098034, 0.92156862745098034, 1.0),
    "gray93": (0.92941176470588238, 0.92941176470588238, 0.92941176470588238, 1.0),
    "gray94": (0.94117647058823528, 0.94117647058823528, 0.94117647058823528, 1.0),
    "gray95": (0.94901960784313721, 0.94901960784313721, 0.94901960784313721, 1.0),
    "gray96": (0.96078431372549022, 0.96078431372549022, 0.96078431372549022, 1.0),
    "gray97": (0.96862745098039216, 0.96862745098039216, 0.96862745098039216, 1.0),
    "gray98": (0.98039215686274506, 0.98039215686274506, 0.98039215686274506, 1.0),
    "gray99": (0.9882352941176471, 0.9882352941176471, 0.9882352941176471, 1.0),
    "green": (0.0, 1.0, 0.0, 1.0),
    "green yellow": (0.67843137254901964, 1.0, 0.18431372549019609, 1.0),
    "green1": (0.0, 1.0, 0.0, 1.0),
    "green2": (0.0, 0.93333333333333335, 0.0, 1.0),
    "green3": (0.0, 0.80392156862745101, 0.0, 1.0),
    "green4": (0.0, 0.54509803921568623, 0.0, 1.0),
    "greenyellow": (0.67843137254901964, 1.0, 0.18431372549019609, 1.0),
    "grey": (0.74509803921568629, 0.74509803921568629, 0.74509803921568629, 1.0),
    "grey0": (0.0, 0.0, 0.0, 1.0),
    "grey1": (0.011764705882352941, 0.011764705882352941, 0.011764705882352941, 1.0),
    "grey10": (0.10196078431372549, 0.10196078431372549, 0.10196078431372549, 1.0),
    "grey100": (1.0, 1.0, 1.0, 1.0),
    "grey11": (0.10980392156862745, 0.10980392156862745, 0.10980392156862745, 1.0),
    "grey12": (0.12156862745098039, 0.12156862745098039, 0.12156862745098039, 1.0),
    "grey13": (0.12941176470588237, 0.12941176470588237, 0.12941176470588237, 1.0),
    "grey14": (0.14117647058823529, 0.14117647058823529, 0.14117647058823529, 1.0),
    "grey15": (0.14901960784313725, 0.14901960784313725, 0.14901960784313725, 1.0),
    "grey16": (0.16078431372549021, 0.16078431372549021, 0.16078431372549021, 1.0),
    "grey17": (0.16862745098039217, 0.16862745098039217, 0.16862745098039217, 1.0),
    "grey18": (0.1803921568627451, 0.1803921568627451, 0.1803921568627451, 1.0),
    "grey19": (0.18823529411764706, 0.18823529411764706, 0.18823529411764706, 1.0),
    "grey2": (0.019607843137254902, 0.019607843137254902, 0.019607843137254902, 1.0),
    "grey20": (0.20000000000000001, 0.20000000000000001, 0.20000000000000001, 1.0),
    "grey21": (0.21176470588235294, 0.21176470588235294, 0.21176470588235294, 1.0),
    "grey22": (0.2196078431372549, 0.2196078431372549, 0.2196078431372549, 1.0),
    "grey23": (0.23137254901960785, 0.23137254901960785, 0.23137254901960785, 1.0),
    "grey24": (0.23921568627450981, 0.23921568627450981, 0.23921568627450981, 1.0),
    "grey25": (0.25098039215686274, 0.25098039215686274, 0.25098039215686274, 1.0),
    "grey26": (0.25882352941176473, 0.25882352941176473, 0.25882352941176473, 1.0),
    "grey27": (0.27058823529411763, 0.27058823529411763, 0.27058823529411763, 1.0),
    "grey28": (0.27843137254901962, 0.27843137254901962, 0.27843137254901962, 1.0),
    "grey29": (0.29019607843137257, 0.29019607843137257, 0.29019607843137257, 1.0),
    "grey3": (0.031372549019607843, 0.031372549019607843, 0.031372549019607843, 1.0),
    "grey30": (0.30196078431372547, 0.30196078431372547, 0.30196078431372547, 1.0),
    "grey31": (0.30980392156862746, 0.30980392156862746, 0.30980392156862746, 1.0),
    "grey32": (0.32156862745098042, 0.32156862745098042, 0.32156862745098042, 1.0),
    "grey33": (0.32941176470588235, 0.32941176470588235, 0.32941176470588235, 1.0),
    "grey34": (0.3411764705882353, 0.3411764705882353, 0.3411764705882353, 1.0),
    "grey35": (0.34901960784313724, 0.34901960784313724, 0.34901960784313724, 1.0),
    "grey36": (0.36078431372549019, 0.36078431372549019, 0.36078431372549019, 1.0),
    "grey37": (0.36862745098039218, 0.36862745098039218, 0.36862745098039218, 1.0),
    "grey38": (0.38039215686274508, 0.38039215686274508, 0.38039215686274508, 1.0),
    "grey39": (0.38823529411764707, 0.38823529411764707, 0.38823529411764707, 1.0),
    "grey4": (0.039215686274509803, 0.039215686274509803, 0.039215686274509803, 1.0),
    "grey40": (0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 1.0),
    "grey41": (0.41176470588235292, 0.41176470588235292, 0.41176470588235292, 1.0),
    "grey42": (0.41960784313725491, 0.41960784313725491, 0.41960784313725491, 1.0),
    "grey43": (0.43137254901960786, 0.43137254901960786, 0.43137254901960786, 1.0),
    "grey44": (0.4392156862745098, 0.4392156862745098, 0.4392156862745098, 1.0),
    "grey45": (0.45098039215686275, 0.45098039215686275, 0.45098039215686275, 1.0),
    "grey46": (0.45882352941176469, 0.45882352941176469, 0.45882352941176469, 1.0),
    "grey47": (0.47058823529411764, 0.47058823529411764, 0.47058823529411764, 1.0),
    "grey48": (0.47843137254901963, 0.47843137254901963, 0.47843137254901963, 1.0),
    "grey49": (0.49019607843137253, 0.49019607843137253, 0.49019607843137253, 1.0),
    "grey5": (0.050980392156862744, 0.050980392156862744, 0.050980392156862744, 1.0),
    "grey50": (0.49803921568627452, 0.49803921568627452, 0.49803921568627452, 1.0),
    "grey51": (0.50980392156862742, 0.50980392156862742, 0.50980392156862742, 1.0),
    "grey52": (0.52156862745098043, 0.52156862745098043, 0.52156862745098043, 1.0),
    "grey53": (0.52941176470588236, 0.52941176470588236, 0.52941176470588236, 1.0),
    "grey54": (0.54117647058823526, 0.54117647058823526, 0.54117647058823526, 1.0),
    "grey55": (0.5490196078431373, 0.5490196078431373, 0.5490196078431373, 1.0),
    "grey56": (0.5607843137254902, 0.5607843137254902, 0.5607843137254902, 1.0),
    "grey57": (0.56862745098039214, 0.56862745098039214, 0.56862745098039214, 1.0),
    "grey58": (0.58039215686274515, 0.58039215686274515, 0.58039215686274515, 1.0),
    "grey59": (0.58823529411764708, 0.58823529411764708, 0.58823529411764708, 1.0),
    "grey6": (0.058823529411764705, 0.058823529411764705, 0.058823529411764705, 1.0),
    "grey60": (0.59999999999999998, 0.59999999999999998, 0.59999999999999998, 1.0),
    "grey61": (0.61176470588235299, 0.61176470588235299, 0.61176470588235299, 1.0),
    "grey62": (0.61960784313725492, 0.61960784313725492, 0.61960784313725492, 1.0),
    "grey63": (0.63137254901960782, 0.63137254901960782, 0.63137254901960782, 1.0),
    "grey64": (0.63921568627450975, 0.63921568627450975, 0.63921568627450975, 1.0),
    "grey65": (0.65098039215686276, 0.65098039215686276, 0.65098039215686276, 1.0),
    "grey66": (0.6588235294117647, 0.6588235294117647, 0.6588235294117647, 1.0),
    "grey67": (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, 1.0),
    "grey68": (0.67843137254901964, 0.67843137254901964, 0.67843137254901964, 1.0),
    "grey69": (0.69019607843137254, 0.69019607843137254, 0.69019607843137254, 1.0),
    "grey7": (0.070588235294117646, 0.070588235294117646, 0.070588235294117646, 1.0),
    "grey70": (0.70196078431372544, 0.70196078431372544, 0.70196078431372544, 1.0),
    "grey71": (0.70980392156862748, 0.70980392156862748, 0.70980392156862748, 1.0),
    "grey72": (0.72156862745098038, 0.72156862745098038, 0.72156862745098038, 1.0),
    "grey73": (0.72941176470588232, 0.72941176470588232, 0.72941176470588232, 1.0),
    "grey74": (0.74117647058823533, 0.74117647058823533, 0.74117647058823533, 1.0),
    "grey75": (0.74901960784313726, 0.74901960784313726, 0.74901960784313726, 1.0),
    "grey76": (0.76078431372549016, 0.76078431372549016, 0.76078431372549016, 1.0),
    "grey77": (0.7686274509803922, 0.7686274509803922, 0.7686274509803922, 1.0),
    "grey78": (0.7803921568627451, 0.7803921568627451, 0.7803921568627451, 1.0),
    "grey79": (0.78823529411764703, 0.78823529411764703, 0.78823529411764703, 1.0),
    "grey8": (0.078431372549019607, 0.078431372549019607, 0.078431372549019607, 1.0),
    "grey80": (0.80000000000000004, 0.80000000000000004, 0.80000000000000004, 1.0),
    "grey81": (0.81176470588235294, 0.81176470588235294, 0.81176470588235294, 1.0),
    "grey82": (0.81960784313725488, 0.81960784313725488, 0.81960784313725488, 1.0),
    "grey83": (0.83137254901960789, 0.83137254901960789, 0.83137254901960789, 1.0),
    "grey84": (0.83921568627450982, 0.83921568627450982, 0.83921568627450982, 1.0),
    "grey85": (0.85098039215686272, 0.85098039215686272, 0.85098039215686272, 1.0),
    "grey86": (0.85882352941176465, 0.85882352941176465, 0.85882352941176465, 1.0),
    "grey87": (0.87058823529411766, 0.87058823529411766, 0.87058823529411766, 1.0),
    "grey88": (0.8784313725490196, 0.8784313725490196, 0.8784313725490196, 1.0),
    "grey89": (0.8901960784313725, 0.8901960784313725, 0.8901960784313725, 1.0),
    "grey9": (0.090196078431372548, 0.090196078431372548, 0.090196078431372548, 1.0),
    "grey90": (0.89803921568627454, 0.89803921568627454, 0.89803921568627454, 1.0),
    "grey91": (0.90980392156862744, 0.90980392156862744, 0.90980392156862744, 1.0),
    "grey92": (0.92156862745098034, 0.92156862745098034, 0.92156862745098034, 1.0),
    "grey93": (0.92941176470588238, 0.92941176470588238, 0.92941176470588238, 1.0),
    "grey94": (0.94117647058823528, 0.94117647058823528, 0.94117647058823528, 1.0),
    "grey95": (0.94901960784313721, 0.94901960784313721, 0.94901960784313721, 1.0),
    "grey96": (0.96078431372549022, 0.96078431372549022, 0.96078431372549022, 1.0),
    "grey97": (0.96862745098039216, 0.96862745098039216, 0.96862745098039216, 1.0),
    "grey98": (0.98039215686274506, 0.98039215686274506, 0.98039215686274506, 1.0),
    "grey99": (0.9882352941176471, 0.9882352941176471, 0.9882352941176471, 1.0),
    "honeydew": (0.94117647058823528, 1.0, 0.94117647058823528, 1.0),
    "honeydew1": (0.94117647058823528, 1.0, 0.94117647058823528, 1.0),
    "honeydew2": (0.8784313725490196, 0.93333333333333335, 0.8784313725490196, 1.0),
    "honeydew3": (0.75686274509803919, 0.80392156862745101, 0.75686274509803919, 1.0),
    "honeydew4": (0.51372549019607838, 0.54509803921568623, 0.51372549019607838, 1.0),
    "hot pink": (1.0, 0.41176470588235292, 0.70588235294117652, 1.0),
    "hotpink": (1.0, 0.41176470588235292, 0.70588235294117652, 1.0),
    "hotpink1": (1.0, 0.43137254901960786, 0.70588235294117652, 1.0),
    "hotpink2": (0.93333333333333335, 0.41568627450980394, 0.65490196078431373, 1.0),
    "hotpink3": (0.80392156862745101, 0.37647058823529411, 0.56470588235294117, 1.0),
    "hotpink4": (0.54509803921568623, 0.22745098039215686, 0.3843137254901961, 1.0),
    "indian red": (0.80392156862745101, 0.36078431372549019, 0.36078431372549019, 1.0),
    "indianred": (0.80392156862745101, 0.36078431372549019, 0.36078431372549019, 1.0),
    "indianred1": (1.0, 0.41568627450980394, 0.41568627450980394, 1.0),
    "indianred2": (0.93333333333333335, 0.38823529411764707, 0.38823529411764707, 1.0),
    "indianred3": (0.80392156862745101, 0.33333333333333331, 0.33333333333333331, 1.0),
    "indianred4": (0.54509803921568623, 0.22745098039215686, 0.22745098039215686, 1.0),
    "indigo": (0.29411764705882354, 0.0, 0.5098039215686274, 1.0),
    "ivory": (1.0, 1.0, 0.94117647058823528, 1.0),
    "ivory1": (1.0, 1.0, 0.94117647058823528, 1.0),
    "ivory2": (0.93333333333333335, 0.93333333333333335, 0.8784313725490196, 1.0),
    "ivory3": (0.80392156862745101, 0.80392156862745101, 0.75686274509803919, 1.0),
    "ivory4": (0.54509803921568623, 0.54509803921568623, 0.51372549019607838, 1.0),
    "khaki": (0.94117647058823528, 0.90196078431372551, 0.5490196078431373, 1.0),
    "khaki1": (1.0, 0.96470588235294119, 0.5607843137254902, 1.0),
    "khaki2": (0.93333333333333335, 0.90196078431372551, 0.52156862745098043, 1.0),
    "khaki3": (0.80392156862745101, 0.77647058823529413, 0.45098039215686275, 1.0),
    "khaki4": (0.54509803921568623, 0.52549019607843139, 0.30588235294117649, 1.0),
    "lavender": (0.90196078431372551, 0.90196078431372551, 0.98039215686274506, 1.0),
    "lavender blush": (1.0, 0.94117647058823528, 0.96078431372549022, 1.0),
    "lavenderblush": (1.0, 0.94117647058823528, 0.96078431372549022, 1.0),
    "lavenderblush1": (1.0, 0.94117647058823528, 0.96078431372549022, 1.0),
    "lavenderblush2": (
        0.93333333333333335,
        0.8784313725490196,
        0.89803921568627454,
        1.0,
    ),
    "lavenderblush3": (
        0.80392156862745101,
        0.75686274509803919,
        0.77254901960784317,
        1.0,
    ),
    "lavenderblush4": (
        0.54509803921568623,
        0.51372549019607838,
        0.52549019607843139,
        1.0,
    ),
    "lawn green": (0.48627450980392156, 0.9882352941176471, 0.0, 1.0),
    "lawngreen": (0.48627450980392156, 0.9882352941176471, 0.0, 1.0),
    "lemon chiffon": (1.0, 0.98039215686274506, 0.80392156862745101, 1.0),
    "lemonchiffon": (1.0, 0.98039215686274506, 0.80392156862745101, 1.0),
    "lemonchiffon1": (1.0, 0.98039215686274506, 0.80392156862745101, 1.0),
    "lemonchiffon2": (
        0.93333333333333335,
        0.9137254901960784,
        0.74901960784313726,
        1.0,
    ),
    "lemonchiffon3": (
        0.80392156862745101,
        0.78823529411764703,
        0.6470588235294118,
        1.0,
    ),
    "lemonchiffon4": (
        0.54509803921568623,
        0.53725490196078429,
        0.4392156862745098,
        1.0,
    ),
    "light blue": (0.67843137254901964, 0.84705882352941175, 0.90196078431372551, 1.0),
    "light coral": (0.94117647058823528, 0.50196078431372548, 0.50196078431372548, 1.0),
    "light cyan": (0.8784313725490196, 1.0, 1.0, 1.0),
    "light goldenrod": (
        0.93333333333333335,
        0.8666666666666667,
        0.50980392156862742,
        1.0,
    ),
    "light goldenrod yellow": (
        0.98039215686274506,
        0.98039215686274506,
        0.82352941176470584,
        1.0,
    ),
    "light gray": (0.82745098039215681, 0.82745098039215681, 0.82745098039215681, 1.0),
    "light green": (0.56470588235294117, 0.93333333333333335, 0.56470588235294117, 1.0),
    "light grey": (0.82745098039215681, 0.82745098039215681, 0.82745098039215681, 1.0),
    "light pink": (1.0, 0.71372549019607845, 0.75686274509803919, 1.0),
    "light salmon": (1.0, 0.62745098039215685, 0.47843137254901963, 1.0),
    "light sea green": (
        0.12549019607843137,
        0.69803921568627447,
        0.66666666666666663,
        1.0,
    ),
    "light sky blue": (
        0.52941176470588236,
        0.80784313725490198,
        0.98039215686274506,
        1.0,
    ),
    "light slate blue": (0.51764705882352946, 0.4392156862745098, 1.0, 1.0),
    "light slate gray": (
        0.46666666666666667,
        0.53333333333333333,
        0.59999999999999998,
        1.0,
    ),
    "light slate grey": (
        0.46666666666666667,
        0.53333333333333333,
        0.59999999999999998,
        1.0,
    ),
    "light steel blue": (
        0.69019607843137254,
        0.7686274509803922,
        0.87058823529411766,
        1.0,
    ),
    "light yellow": (1.0, 1.0, 0.8784313725490196, 1.0),
    "lightblue": (0.67843137254901964, 0.84705882352941175, 0.90196078431372551, 1.0),
    "lightblue1": (0.74901960784313726, 0.93725490196078431, 1.0, 1.0),
    "lightblue2": (0.69803921568627447, 0.87450980392156863, 0.93333333333333335, 1.0),
    "lightblue3": (0.60392156862745094, 0.75294117647058822, 0.80392156862745101, 1.0),
    "lightblue4": (0.40784313725490196, 0.51372549019607838, 0.54509803921568623, 1.0),
    "lightcoral": (0.94117647058823528, 0.50196078431372548, 0.50196078431372548, 1.0),
    "lightcyan": (0.8784313725490196, 1.0, 1.0, 1.0),
    "lightcyan1": (0.8784313725490196, 1.0, 1.0, 1.0),
    "lightcyan2": (0.81960784313725488, 0.93333333333333335, 0.93333333333333335, 1.0),
    "lightcyan3": (0.70588235294117652, 0.80392156862745101, 0.80392156862745101, 1.0),
    "lightcyan4": (0.47843137254901963, 0.54509803921568623, 0.54509803921568623, 1.0),
    "lightgoldenrod": (
        0.93333333333333335,
        0.8666666666666667,
        0.50980392156862742,
        1.0,
    ),
    "lightgoldenrod1": (1.0, 0.92549019607843142, 0.54509803921568623, 1.0),
    "lightgoldenrod2": (
        0.93333333333333335,
        0.86274509803921573,
        0.50980392156862742,
        1.0,
    ),
    "lightgoldenrod3": (
        0.80392156862745101,
        0.74509803921568629,
        0.4392156862745098,
        1.0,
    ),
    "lightgoldenrod4": (
        0.54509803921568623,
        0.50588235294117645,
        0.29803921568627451,
        1.0,
    ),
    "lightgoldenrodyellow": (
        0.98039215686274506,
        0.98039215686274506,
        0.82352941176470584,
        1.0,
    ),
    "lightgray": (0.82745098039215681, 0.82745098039215681, 0.82745098039215681, 1.0),
    "lightgreen": (0.56470588235294117, 0.93333333333333335, 0.56470588235294117, 1.0),
    "lightgrey": (0.82745098039215681, 0.82745098039215681, 0.82745098039215681, 1.0),
    "lightpink": (1.0, 0.71372549019607845, 0.75686274509803919, 1.0),
    "lightpink1": (1.0, 0.68235294117647061, 0.72549019607843135, 1.0),
    "lightpink2": (0.93333333333333335, 0.63529411764705879, 0.67843137254901964, 1.0),
    "lightpink3": (0.80392156862745101, 0.5490196078431373, 0.58431372549019611, 1.0),
    "lightpink4": (0.54509803921568623, 0.37254901960784315, 0.396078431372549, 1.0),
    "lightsalmon": (1.0, 0.62745098039215685, 0.47843137254901963, 1.0),
    "lightsalmon1": (1.0, 0.62745098039215685, 0.47843137254901963, 1.0),
    "lightsalmon2": (
        0.93333333333333335,
        0.58431372549019611,
        0.44705882352941179,
        1.0,
    ),
    "lightsalmon3": (0.80392156862745101, 0.50588235294117645, 0.3843137254901961, 1.0),
    "lightsalmon4": (0.54509803921568623, 0.3411764705882353, 0.25882352941176473, 1.0),
    "lightseagreen": (
        0.12549019607843137,
        0.69803921568627447,
        0.66666666666666663,
        1.0,
    ),
    "lightskyblue": (
        0.52941176470588236,
        0.80784313725490198,
        0.98039215686274506,
        1.0,
    ),
    "lightskyblue1": (0.69019607843137254, 0.88627450980392153, 1.0, 1.0),
    "lightskyblue2": (
        0.64313725490196083,
        0.82745098039215681,
        0.93333333333333335,
        1.0,
    ),
    "lightskyblue3": (
        0.55294117647058827,
        0.71372549019607845,
        0.80392156862745101,
        1.0,
    ),
    "lightskyblue4": (
        0.37647058823529411,
        0.4823529411764706,
        0.54509803921568623,
        1.0,
    ),
    "lightslateblue": (0.51764705882352946, 0.4392156862745098, 1.0, 1.0),
    "lightslategray": (
        0.46666666666666667,
        0.53333333333333333,
        0.59999999999999998,
        1.0,
    ),
    "lightslategrey": (
        0.46666666666666667,
        0.53333333333333333,
        0.59999999999999998,
        1.0,
    ),
    "lightsteelblue": (
        0.69019607843137254,
        0.7686274509803922,
        0.87058823529411766,
        1.0,
    ),
    "lightsteelblue1": (0.792156862745098, 0.88235294117647056, 1.0, 1.0),
    "lightsteelblue2": (
        0.73725490196078436,
        0.82352941176470584,
        0.93333333333333335,
        1.0,
    ),
    "lightsteelblue3": (
        0.63529411764705879,
        0.70980392156862748,
        0.80392156862745101,
        1.0,
    ),
    "lightsteelblue4": (
        0.43137254901960786,
        0.4823529411764706,
        0.54509803921568623,
        1.0,
    ),
    "lightyellow": (1.0, 1.0, 0.8784313725490196, 1.0),
    "lightyellow1": (1.0, 1.0, 0.8784313725490196, 1.0),
    "lightyellow2": (
        0.93333333333333335,
        0.93333333333333335,
        0.81960784313725488,
        1.0,
    ),
    "lightyellow3": (
        0.80392156862745101,
        0.80392156862745101,
        0.70588235294117652,
        1.0,
    ),
    "lightyellow4": (
        0.54509803921568623,
        0.54509803921568623,
        0.47843137254901963,
        1.0,
    ),
    "lime": (0.0, 1.0, 0.0, 1.0),
    "lime green": (0.19607843137254902, 0.80392156862745101, 0.19607843137254902, 1.0),
    "limegreen": (0.19607843137254902, 0.80392156862745101, 0.19607843137254902, 1.0),
    "linen": (0.98039215686274506, 0.94117647058823528, 0.90196078431372551, 1.0),
    "magenta": (1.0, 0.0, 1.0, 1.0),
    "magenta1": (1.0, 0.0, 1.0, 1.0),
    "magenta2": (0.93333333333333335, 0.0, 0.93333333333333335, 1.0),
    "magenta3": (0.80392156862745101, 0.0, 0.80392156862745101, 1.0),
    "magenta4": (0.54509803921568623, 0.0, 0.54509803921568623, 1.0),
    "maroon": (0.69019607843137254, 0.18823529411764706, 0.37647058823529411, 1.0),
    "maroon1": (1.0, 0.20392156862745098, 0.70196078431372544, 1.0),
    "maroon2": (0.93333333333333335, 0.18823529411764706, 0.65490196078431373, 1.0),
    "maroon3": (0.80392156862745101, 0.16078431372549021, 0.56470588235294117, 1.0),
    "maroon4": (0.54509803921568623, 0.10980392156862745, 0.3843137254901961, 1.0),
    "medium aquamarine": (
        0.40000000000000002,
        0.80392156862745101,
        0.66666666666666663,
        1.0,
    ),
    "medium blue": (0.0, 0.0, 0.80392156862745101, 1.0),
    "medium orchid": (
        0.72941176470588232,
        0.33333333333333331,
        0.82745098039215681,
        1.0,
    ),
    "medium purple": (
        0.57647058823529407,
        0.4392156862745098,
        0.85882352941176465,
        1.0,
    ),
    "medium sea green": (
        0.23529411764705882,
        0.70196078431372544,
        0.44313725490196076,
        1.0,
    ),
    "medium slate blue": (
        0.4823529411764706,
        0.40784313725490196,
        0.93333333333333335,
        1.0,
    ),
    "medium spring green": (0.0, 0.98039215686274506, 0.60392156862745094, 1.0),
    "medium turquoise": (
        0.28235294117647058,
        0.81960784313725488,
        0.80000000000000004,
        1.0,
    ),
    "medium violet red": (
        0.7803921568627451,
        0.082352941176470587,
        0.52156862745098043,
        1.0,
    ),
    "mediumaquamarine": (
        0.40000000000000002,
        0.80392156862745101,
        0.66666666666666663,
        1.0,
    ),
    "mediumblue": (0.0, 0.0, 0.80392156862745101, 1.0),
    "mediumorchid": (
        0.72941176470588232,
        0.33333333333333331,
        0.82745098039215681,
        1.0,
    ),
    "mediumorchid1": (0.8784313725490196, 0.40000000000000002, 1.0, 1.0),
    "mediumorchid2": (
        0.81960784313725488,
        0.37254901960784315,
        0.93333333333333335,
        1.0,
    ),
    "mediumorchid3": (
        0.70588235294117652,
        0.32156862745098042,
        0.80392156862745101,
        1.0,
    ),
    "mediumorchid4": (
        0.47843137254901963,
        0.21568627450980393,
        0.54509803921568623,
        1.0,
    ),
    "mediumpurple": (0.57647058823529407, 0.4392156862745098, 0.85882352941176465, 1.0),
    "mediumpurple1": (0.6705882352941176, 0.50980392156862742, 1.0, 1.0),
    "mediumpurple2": (
        0.62352941176470589,
        0.47450980392156861,
        0.93333333333333335,
        1.0,
    ),
    "mediumpurple3": (
        0.53725490196078429,
        0.40784313725490196,
        0.80392156862745101,
        1.0,
    ),
    "mediumpurple4": (
        0.36470588235294116,
        0.27843137254901962,
        0.54509803921568623,
        1.0,
    ),
    "mediumseagreen": (
        0.23529411764705882,
        0.70196078431372544,
        0.44313725490196076,
        1.0,
    ),
    "mediumslateblue": (
        0.4823529411764706,
        0.40784313725490196,
        0.93333333333333335,
        1.0,
    ),
    "mediumspringgreen": (0.0, 0.98039215686274506, 0.60392156862745094, 1.0),
    "mediumturquoise": (
        0.28235294117647058,
        0.81960784313725488,
        0.80000000000000004,
        1.0,
    ),
    "mediumvioletred": (
        0.7803921568627451,
        0.082352941176470587,
        0.52156862745098043,
        1.0,
    ),
    "midnight blue": (
        0.098039215686274508,
        0.098039215686274508,
        0.4392156862745098,
        1.0,
    ),
    "midnightblue": (
        0.098039215686274508,
        0.098039215686274508,
        0.4392156862745098,
        1.0,
    ),
    "mint cream": (0.96078431372549022, 1.0, 0.98039215686274506, 1.0),
    "mintcream": (0.96078431372549022, 1.0, 0.98039215686274506, 1.0),
    "misty rose": (1.0, 0.89411764705882357, 0.88235294117647056, 1.0),
    "mistyrose": (1.0, 0.89411764705882357, 0.88235294117647056, 1.0),
    "mistyrose1": (1.0, 0.89411764705882357, 0.88235294117647056, 1.0),
    "mistyrose2": (0.93333333333333335, 0.83529411764705885, 0.82352941176470584, 1.0),
    "mistyrose3": (0.80392156862745101, 0.71764705882352942, 0.70980392156862748, 1.0),
    "mistyrose4": (0.54509803921568623, 0.49019607843137253, 0.4823529411764706, 1.0),
    "moccasin": (1.0, 0.89411764705882357, 0.70980392156862748, 1.0),
    "navajo white": (1.0, 0.87058823529411766, 0.67843137254901964, 1.0),
    "navajowhite": (1.0, 0.87058823529411766, 0.67843137254901964, 1.0),
    "navajowhite1": (1.0, 0.87058823529411766, 0.67843137254901964, 1.0),
    "navajowhite2": (
        0.93333333333333335,
        0.81176470588235294,
        0.63137254901960782,
        1.0,
    ),
    "navajowhite3": (
        0.80392156862745101,
        0.70196078431372544,
        0.54509803921568623,
        1.0,
    ),
    "navajowhite4": (
        0.54509803921568623,
        0.47450980392156861,
        0.36862745098039218,
        1.0,
    ),
    "navy": (0.0, 0.0, 0.50196078431372548, 1.0),
    "navy blue": (0.0, 0.0, 0.50196078431372548, 1.0),
    "navyblue": (0.0, 0.0, 0.50196078431372548, 1.0),
    "old lace": (0.99215686274509807, 0.96078431372549022, 0.90196078431372551, 1.0),
    "oldlace": (0.99215686274509807, 0.96078431372549022, 0.90196078431372551, 1.0),
    "olive": (0.5, 0.5, 0.0, 1.0),
    "olive drab": (0.41960784313725491, 0.55686274509803924, 0.13725490196078433, 1.0),
    "olivedrab": (0.41960784313725491, 0.55686274509803924, 0.13725490196078433, 1.0),
    "olivedrab1": (0.75294117647058822, 1.0, 0.24313725490196078, 1.0),
    "olivedrab2": (0.70196078431372544, 0.93333333333333335, 0.22745098039215686, 1.0),
    "olivedrab3": (0.60392156862745094, 0.80392156862745101, 0.19607843137254902, 1.0),
    "olivedrab4": (0.41176470588235292, 0.54509803921568623, 0.13333333333333333, 1.0),
    "orange": (1.0, 0.6470588235294118, 0.0, 1.0),
    "orange red": (1.0, 0.27058823529411763, 0.0, 1.0),
    "orange1": (1.0, 0.6470588235294118, 0.0, 1.0),
    "orange2": (0.93333333333333335, 0.60392156862745094, 0.0, 1.0),
    "orange3": (0.80392156862745101, 0.52156862745098043, 0.0, 1.0),
    "orange4": (0.54509803921568623, 0.35294117647058826, 0.0, 1.0),
    "orangered": (1.0, 0.27058823529411763, 0.0, 1.0),
    "orangered1": (1.0, 0.27058823529411763, 0.0, 1.0),
    "orangered2": (0.93333333333333335, 0.25098039215686274, 0.0, 1.0),
    "orangered3": (0.80392156862745101, 0.21568627450980393, 0.0, 1.0),
    "orangered4": (0.54509803921568623, 0.14509803921568629, 0.0, 1.0),
    "orchid": (0.85490196078431369, 0.4392156862745098, 0.83921568627450982, 1.0),
    "orchid1": (1.0, 0.51372549019607838, 0.98039215686274506, 1.0),
    "orchid2": (0.93333333333333335, 0.47843137254901963, 0.9137254901960784, 1.0),
    "orchid3": (0.80392156862745101, 0.41176470588235292, 0.78823529411764703, 1.0),
    "orchid4": (0.54509803921568623, 0.27843137254901962, 0.53725490196078429, 1.0),
    "pale goldenrod": (
        0.93333333333333335,
        0.90980392156862744,
        0.66666666666666663,
        1.0,
    ),
    "pale green": (0.59607843137254901, 0.98431372549019602, 0.59607843137254901, 1.0),
    "pale turquoise": (
        0.68627450980392157,
        0.93333333333333335,
        0.93333333333333335,
        1.0,
    ),
    "pale violet red": (
        0.85882352941176465,
        0.4392156862745098,
        0.57647058823529407,
        1.0,
    ),
    "palegoldenrod": (
        0.93333333333333335,
        0.90980392156862744,
        0.66666666666666663,
        1.0,
    ),
    "palegreen": (0.59607843137254901, 0.98431372549019602, 0.59607843137254901, 1.0),
    "palegreen1": (0.60392156862745094, 1.0, 0.60392156862745094, 1.0),
    "palegreen2": (0.56470588235294117, 0.93333333333333335, 0.56470588235294117, 1.0),
    "palegreen3": (0.48627450980392156, 0.80392156862745101, 0.48627450980392156, 1.0),
    "palegreen4": (0.32941176470588235, 0.54509803921568623, 0.32941176470588235, 1.0),
    "paleturquoise": (
        0.68627450980392157,
        0.93333333333333335,
        0.93333333333333335,
        1.0,
    ),
    "paleturquoise1": (0.73333333333333328, 1.0, 1.0, 1.0),
    "paleturquoise2": (
        0.68235294117647061,
        0.93333333333333335,
        0.93333333333333335,
        1.0,
    ),
    "paleturquoise3": (
        0.58823529411764708,
        0.80392156862745101,
        0.80392156862745101,
        1.0,
    ),
    "paleturquoise4": (
        0.40000000000000002,
        0.54509803921568623,
        0.54509803921568623,
        1.0,
    ),
    "palevioletred": (
        0.85882352941176465,
        0.4392156862745098,
        0.57647058823529407,
        1.0,
    ),
    "palevioletred1": (1.0, 0.50980392156862742, 0.6705882352941176, 1.0),
    "palevioletred2": (
        0.93333333333333335,
        0.47450980392156861,
        0.62352941176470589,
        1.0,
    ),
    "palevioletred3": (
        0.80392156862745101,
        0.40784313725490196,
        0.53725490196078429,
        1.0,
    ),
    "palevioletred4": (
        0.54509803921568623,
        0.27843137254901962,
        0.36470588235294116,
        1.0,
    ),
    "papaya whip": (1.0, 0.93725490196078431, 0.83529411764705885, 1.0),
    "papayawhip": (1.0, 0.93725490196078431, 0.83529411764705885, 1.0),
    "peach puff": (1.0, 0.85490196078431369, 0.72549019607843135, 1.0),
    "peachpuff": (1.0, 0.85490196078431369, 0.72549019607843135, 1.0),
    "peachpuff1": (1.0, 0.85490196078431369, 0.72549019607843135, 1.0),
    "peachpuff2": (0.93333333333333335, 0.79607843137254897, 0.67843137254901964, 1.0),
    "peachpuff3": (0.80392156862745101, 0.68627450980392157, 0.58431372549019611, 1.0),
    "peachpuff4": (0.54509803921568623, 0.46666666666666667, 0.396078431372549, 1.0),
    "peru": (0.80392156862745101, 0.52156862745098043, 0.24705882352941178, 1.0),
    "pink": (1.0, 0.75294117647058822, 0.79607843137254897, 1.0),
    "pink1": (1.0, 0.70980392156862748, 0.77254901960784317, 1.0),
    "pink2": (0.93333333333333335, 0.66274509803921566, 0.72156862745098038, 1.0),
    "pink3": (0.80392156862745101, 0.56862745098039214, 0.61960784313725492, 1.0),
    "pink4": (0.54509803921568623, 0.38823529411764707, 0.42352941176470588, 1.0),
    "plum": (0.8666666666666667, 0.62745098039215685, 0.8666666666666667, 1.0),
    "plum1": (1.0, 0.73333333333333328, 1.0, 1.0),
    "plum2": (0.93333333333333335, 0.68235294117647061, 0.93333333333333335, 1.0),
    "plum3": (0.80392156862745101, 0.58823529411764708, 0.80392156862745101, 1.0),
    "plum4": (0.54509803921568623, 0.40000000000000002, 0.54509803921568623, 1.0),
    "powder blue": (0.69019607843137254, 0.8784313725490196, 0.90196078431372551, 1.0),
    "powderblue": (0.69019607843137254, 0.8784313725490196, 0.90196078431372551, 1.0),
    "purple": (0.62745098039215685, 0.12549019607843137, 0.94117647058823528, 1.0),
    "purple1": (0.60784313725490191, 0.18823529411764706, 1.0, 1.0),
    "purple2": (0.56862745098039214, 0.17254901960784313, 0.93333333333333335, 1.0),
    "purple3": (0.49019607843137253, 0.14901960784313725, 0.80392156862745101, 1.0),
    "purple4": (0.33333333333333331, 0.10196078431372549, 0.54509803921568623, 1.0),
    "rebecca purple": (0.4, 0.2, 0.6, 1.0),
    "rebeccapurple": (0.4, 0.2, 0.6, 1.0),
    "red": (1.0, 0.0, 0.0, 1.0),
    "red1": (1.0, 0.0, 0.0, 1.0),
    "red2": (0.93333333333333335, 0.0, 0.0, 1.0),
    "red3": (0.80392156862745101, 0.0, 0.0, 1.0),
    "red4": (0.54509803921568623, 0.0, 0.0, 1.0),
    "rosy brown": (0.73725490196078436, 0.5607843137254902, 0.5607843137254902, 1.0),
    "rosybrown": (0.73725490196078436, 0.5607843137254902, 0.5607843137254902, 1.0),
    "rosybrown1": (1.0, 0.75686274509803919, 0.75686274509803919, 1.0),
    "rosybrown2": (0.93333333333333335, 0.70588235294117652, 0.70588235294117652, 1.0),
    "rosybrown3": (0.80392156862745101, 0.60784313725490191, 0.60784313725490191, 1.0),
    "rosybrown4": (0.54509803921568623, 0.41176470588235292, 0.41176470588235292, 1.0),
    "royal blue": (0.25490196078431371, 0.41176470588235292, 0.88235294117647056, 1.0),
    "royalblue": (0.25490196078431371, 0.41176470588235292, 0.88235294117647056, 1.0),
    "royalblue1": (0.28235294117647058, 0.46274509803921571, 1.0, 1.0),
    "royalblue2": (0.2627450980392157, 0.43137254901960786, 0.93333333333333335, 1.0),
    "royalblue3": (0.22745098039215686, 0.37254901960784315, 0.80392156862745101, 1.0),
    "royalblue4": (0.15294117647058825, 0.25098039215686274, 0.54509803921568623, 1.0),
    "saddle brown": (
        0.54509803921568623,
        0.27058823529411763,
        0.074509803921568626,
        1.0,
    ),
    "saddlebrown": (
        0.54509803921568623,
        0.27058823529411763,
        0.074509803921568626,
        1.0,
    ),
    "salmon": (0.98039215686274506, 0.50196078431372548, 0.44705882352941179, 1.0),
    "salmon1": (1.0, 0.5490196078431373, 0.41176470588235292, 1.0),
    "salmon2": (0.93333333333333335, 0.50980392156862742, 0.3843137254901961, 1.0),
    "salmon3": (0.80392156862745101, 0.4392156862745098, 0.32941176470588235, 1.0),
    "salmon4": (0.54509803921568623, 0.29803921568627451, 0.22352941176470589, 1.0),
    "sandy brown": (0.95686274509803926, 0.64313725490196083, 0.37647058823529411, 1.0),
    "sandybrown": (0.95686274509803926, 0.64313725490196083, 0.37647058823529411, 1.0),
    "sea green": (0.1803921568627451, 0.54509803921568623, 0.3411764705882353, 1.0),
    "seagreen": (0.1803921568627451, 0.54509803921568623, 0.3411764705882353, 1.0),
    "seagreen1": (0.32941176470588235, 1.0, 0.62352941176470589, 1.0),
    "seagreen2": (0.30588235294117649, 0.93333333333333335, 0.58039215686274515, 1.0),
    "seagreen3": (0.2627450980392157, 0.80392156862745101, 0.50196078431372548, 1.0),
    "seagreen4": (0.1803921568627451, 0.54509803921568623, 0.3411764705882353, 1.0),
    "seashell": (1.0, 0.96078431372549022, 0.93333333333333335, 1.0),
    "seashell1": (1.0, 0.96078431372549022, 0.93333333333333335, 1.0),
    "seashell2": (0.93333333333333335, 0.89803921568627454, 0.87058823529411766, 1.0),
    "seashell3": (0.80392156862745101, 0.77254901960784317, 0.74901960784313726, 1.0),
    "seashell4": (0.54509803921568623, 0.52549019607843139, 0.50980392156862742, 1.0),
    "sienna": (0.62745098039215685, 0.32156862745098042, 0.17647058823529413, 1.0),
    "sienna1": (1.0, 0.50980392156862742, 0.27843137254901962, 1.0),
    "sienna2": (0.93333333333333335, 0.47450980392156861, 0.25882352941176473, 1.0),
    "sienna3": (0.80392156862745101, 0.40784313725490196, 0.22352941176470589, 1.0),
    "sienna4": (0.54509803921568623, 0.27843137254901962, 0.14901960784313725, 1.0),
    "silver": (0.75, 0.75, 0.75, 1.0),
    "sky blue": (0.52941176470588236, 0.80784313725490198, 0.92156862745098034, 1.0),
    "skyblue": (0.52941176470588236, 0.80784313725490198, 0.92156862745098034, 1.0),
    "skyblue1": (0.52941176470588236, 0.80784313725490198, 1.0, 1.0),
    "skyblue2": (0.49411764705882355, 0.75294117647058822, 0.93333333333333335, 1.0),
    "skyblue3": (0.42352941176470588, 0.65098039215686276, 0.80392156862745101, 1.0),
    "skyblue4": (0.29019607843137257, 0.4392156862745098, 0.54509803921568623, 1.0),
    "slate blue": (0.41568627450980394, 0.35294117647058826, 0.80392156862745101, 1.0),
    "slate gray": (0.4392156862745098, 0.50196078431372548, 0.56470588235294117, 1.0),
    "slate grey": (0.4392156862745098, 0.50196078431372548, 0.56470588235294117, 1.0),
    "slateblue": (0.41568627450980394, 0.35294117647058826, 0.80392156862745101, 1.0),
    "slateblue1": (0.51372549019607838, 0.43529411764705883, 1.0, 1.0),
    "slateblue2": (0.47843137254901963, 0.40392156862745099, 0.93333333333333335, 1.0),
    "slateblue3": (0.41176470588235292, 0.34901960784313724, 0.80392156862745101, 1.0),
    "slateblue4": (0.27843137254901962, 0.23529411764705882, 0.54509803921568623, 1.0),
    "slategray": (0.4392156862745098, 0.50196078431372548, 0.56470588235294117, 1.0),
    "slategray1": (0.77647058823529413, 0.88627450980392153, 1.0, 1.0),
    "slategray2": (0.72549019607843135, 0.82745098039215681, 0.93333333333333335, 1.0),
    "slategray3": (0.62352941176470589, 0.71372549019607845, 0.80392156862745101, 1.0),
    "slategray4": (0.42352941176470588, 0.4823529411764706, 0.54509803921568623, 1.0),
    "slategrey": (0.4392156862745098, 0.50196078431372548, 0.56470588235294117, 1.0),
    "snow": (1.0, 0.98039215686274506, 0.98039215686274506, 1.0),
    "snow1": (1.0, 0.98039215686274506, 0.98039215686274506, 1.0),
    "snow2": (0.93333333333333335, 0.9137254901960784, 0.9137254901960784, 1.0),
    "snow3": (0.80392156862745101, 0.78823529411764703, 0.78823529411764703, 1.0),
    "snow4": (0.54509803921568623, 0.53725490196078429, 0.53725490196078429, 1.0),
    "spring green": (0.0, 1.0, 0.49803921568627452, 1.0),
    "springgreen": (0.0, 1.0, 0.49803921568627452, 1.0),
    "springgreen1": (0.0, 1.0, 0.49803921568627452, 1.0),
    "springgreen2": (0.0, 0.93333333333333335, 0.46274509803921571, 1.0),
    "springgreen3": (0.0, 0.80392156862745101, 0.40000000000000002, 1.0),
    "springgreen4": (0.0, 0.54509803921568623, 0.27058823529411763, 1.0),
    "steel blue": (0.27450980392156865, 0.50980392156862742, 0.70588235294117652, 1.0),
    "steelblue": (0.27450980392156865, 0.50980392156862742, 0.70588235294117652, 1.0),
    "steelblue1": (0.38823529411764707, 0.72156862745098038, 1.0, 1.0),
    "steelblue2": (0.36078431372549019, 0.67450980392156867, 0.93333333333333335, 1.0),
    "steelblue3": (0.30980392156862746, 0.58039215686274515, 0.80392156862745101, 1.0),
    "steelblue4": (0.21176470588235294, 0.39215686274509803, 0.54509803921568623, 1.0),
    "tan": (0.82352941176470584, 0.70588235294117652, 0.5490196078431373, 1.0),
    "tan1": (1.0, 0.6470588235294118, 0.30980392156862746, 1.0),
    "tan2": (0.93333333333333335, 0.60392156862745094, 0.28627450980392155, 1.0),
    "tan3": (0.80392156862745101, 0.52156862745098043, 0.24705882352941178, 1.0),
    "tan4": (0.54509803921568623, 0.35294117647058826, 0.16862745098039217, 1.0),
    "teal": (0.0, 0.5, 0.5, 1.0),
    "thistle": (0.84705882352941175, 0.74901960784313726, 0.84705882352941175, 1.0),
    "thistle1": (1.0, 0.88235294117647056, 1.0, 1.0),
    "thistle2": (0.93333333333333335, 0.82352941176470584, 0.93333333333333335, 1.0),
    "thistle3": (0.80392156862745101, 0.70980392156862748, 0.80392156862745101, 1.0),
    "thistle4": (0.54509803921568623, 0.4823529411764706, 0.54509803921568623, 1.0),
    "tomato": (1.0, 0.38823529411764707, 0.27843137254901962, 1.0),
    "tomato1": (1.0, 0.38823529411764707, 0.27843137254901962, 1.0),
    "tomato2": (0.93333333333333335, 0.36078431372549019, 0.25882352941176473, 1.0),
    "tomato3": (0.80392156862745101, 0.30980392156862746, 0.22352941176470589, 1.0),
    "tomato4": (0.54509803921568623, 0.21176470588235294, 0.14901960784313725, 1.0),
    "turquoise": (0.25098039215686274, 0.8784313725490196, 0.81568627450980391, 1.0),
    "turquoise1": (0.0, 0.96078431372549022, 1.0, 1.0),
    "turquoise2": (0.0, 0.89803921568627454, 0.93333333333333335, 1.0),
    "turquoise3": (0.0, 0.77254901960784317, 0.80392156862745101, 1.0),
    "turquoise4": (0.0, 0.52549019607843139, 0.54509803921568623, 1.0),
    "violet": (0.93333333333333335, 0.50980392156862742, 0.93333333333333335, 1.0),
    "violet red": (0.81568627450980391, 0.12549019607843137, 0.56470588235294117, 1.0),
    "violetred": (0.81568627450980391, 0.12549019607843137, 0.56470588235294117, 1.0),
    "violetred1": (1.0, 0.24313725490196078, 0.58823529411764708, 1.0),
    "violetred2": (0.93333333333333335, 0.22745098039215686, 0.5490196078431373, 1.0),
    "violetred3": (0.80392156862745101, 0.19607843137254902, 0.47058823529411764, 1.0),
    "violetred4": (0.54509803921568623, 0.13333333333333333, 0.32156862745098042, 1.0),
    "web gray": (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0),
    "webgray": (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0),
    "web green": (0.0, 0.5019607843137255, 0.0, 1.0),
    "webgreen": (0.0, 0.5019607843137255, 0.0, 1.0),
    "webgray": (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0),
    "web grey": (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0),
    "webgrey": (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0),
    "web maroon": (0.5019607843137255, 0.0, 0.0, 1.0),
    "webmaroon": (0.5019607843137255, 0.0, 0.0, 1.0),
    "web purple": (0.4980392156862745, 0.0, 0.4980392156862745, 1.0),
    "webpurple": (0.4980392156862745, 0.0, 0.4980392156862745, 1.0),
    "wheat": (0.96078431372549022, 0.87058823529411766, 0.70196078431372544, 1.0),
    "wheat1": (1.0, 0.90588235294117647, 0.72941176470588232, 1.0),
    "wheat2": (0.93333333333333335, 0.84705882352941175, 0.68235294117647061, 1.0),
    "wheat3": (0.80392156862745101, 0.72941176470588232, 0.58823529411764708, 1.0),
    "wheat4": (0.54509803921568623, 0.49411764705882355, 0.40000000000000002, 1.0),
    "white": (1.0, 1.0, 1.0, 1.0),
    "white smoke": (0.96078431372549022, 0.96078431372549022, 0.96078431372549022, 1.0),
    "whitesmoke": (0.96078431372549022, 0.96078431372549022, 0.96078431372549022, 1.0),
    "yellow": (1.0, 1.0, 0.0, 1.0),
    "yellow green": (
        0.60392156862745094,
        0.80392156862745101,
        0.19607843137254902,
        1.0,
    ),
    "yellow1": (1.0, 1.0, 0.0, 1.0),
    "yellow2": (0.93333333333333335, 0.93333333333333335, 0.0, 1.0),
    "yellow3": (0.80392156862745101, 0.80392156862745101, 0.0, 1.0),
    "yellow4": (0.54509803921568623, 0.54509803921568623, 0.0, 1.0),
    "yellowgreen": (0.60392156862745094, 0.80392156862745101, 0.19607843137254902, 1.0),
}

palettes = {
    "gray": GradientPalette("black", "white"),
    "red-blue": GradientPalette("red", "blue"),
    "red-purple-blue": AdvancedGradientPalette(["red", "purple", "blue"]),
    "red-green": GradientPalette("red", "green"),
    "red-yellow-green": AdvancedGradientPalette(["red", "yellow", "green"]),
    "red-black-green": AdvancedGradientPalette(["red", "black", "green"]),
    "rainbow": RainbowPalette(),
    "heat": AdvancedGradientPalette(["red", "yellow", "white"], indices=[0, 192, 255]),
    "terrain": AdvancedGradientPalette(
        ["hsv(120, 100%, 65%)", "hsv(60, 100%, 90%)", "hsv(0, 0%, 95%)"]
    ),
}
