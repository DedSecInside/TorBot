"""
Utility classes for drawing routines.
"""

from collections import defaultdict
from math import atan2, cos, hypot, sin
from typing import NamedTuple

from igraph.utils import consecutive_pairs

__all__ = (
    "BoundingBox",
    "Point",
    "Rectangle",
    "calculate_corner_radii",
    "euclidean_distance",
    "evaluate_cubic_bezier",
    "get_bezier_control_points_for_curved_edge",
    "intersect_bezier_curve_and_circle",
    "str_to_orientation",
    "autocurve",
)

#####################################################################


class Rectangle:
    """Class representing a rectangle."""

    __slots__ = ("_left", "_top", "_right", "_bottom")

    def __init__(self, *args):
        """Creates a rectangle.

        The corners of the rectangle can be specified by either a tuple
        (four items, two for each corner, respectively), four separate numbers
        (X and Y coordinates for each corner) or two separate numbers (width
        and height, the upper left corner is assumed to be at (0,0))"""
        coords = None
        if len(args) == 1:
            if isinstance(args[0], Rectangle):
                coords = args[0].coords
            elif len(args[0]) >= 4:
                coords = tuple(args[0])[0:4]
            elif len(args[0]) == 2:
                coords = (0, 0, args[0][0], args[0][1])
        elif len(args) == 4:
            coords = tuple(args)
        elif len(args) == 2:
            coords = (0, 0, args[0], args[1])
        if coords is None:
            raise ValueError("invalid coordinate format")

        try:
            coords = tuple(float(coord) for coord in coords)
        except ValueError:
            raise ValueError("invalid coordinate format, numbers expected")

        self.coords = coords

    @property
    def coords(self):
        """The coordinates of the corners.

        The coordinates are returned as a 4-tuple in the following order:
        left edge, top edge, right edge, bottom edge.
        """
        return self._left, self._top, self._right, self._bottom

    @coords.setter
    def coords(self, coords):
        """Sets the coordinates of the corners.

        @param coords: a 4-tuple with the coordinates of the corners
        """
        self._left, self._top, self._right, self._bottom = coords
        if self._left > self._right:
            self._left, self._right = self._right, self._left
        if self._top > self._bottom:
            self._bottom, self._top = self._top, self._bottom

    @property
    def width(self):
        """The width of the rectangle"""
        return self._right - self._left

    @width.setter
    def width(self, value):
        """Sets the width of the rectangle by adjusting the right edge."""
        self._right = self._left + value

    @property
    def height(self):
        """The height of the rectangle"""
        return self._bottom - self._top

    @height.setter
    def height(self, value):
        """Sets the height of the rectangle by adjusting the bottom edge."""
        self._bottom = self._top + value

    @property
    def left(self):
        """The X coordinate of the left side of the box"""
        return self._left

    @left.setter
    def left(self, value):
        """Sets the X coordinate of the left side of the box"""
        self._left = float(value)
        self._right = max(self._left, self._right)

    @property
    def right(self):
        """The X coordinate of the right side of the box"""
        return self._right

    @right.setter
    def right(self, value):
        """Sets the X coordinate of the right side of the box"""
        self._right = float(value)
        self._left = min(self._left, self._right)

    @property
    def top(self):
        """The Y coordinate of the top edge of the box"""
        return self._top

    @top.setter
    def top(self, value):
        """Sets the Y coordinate of the top edge of the box"""
        self._top = value
        self._bottom = max(self._bottom, self._top)

    @property
    def bottom(self):
        """The Y coordinate of the bottom edge of the box"""
        return self._bottom

    @bottom.setter
    def bottom(self, value):
        """Sets the Y coordinate of the bottom edge of the box"""
        self._bottom = value
        self._top = min(self._bottom, self._top)

    @property
    def midx(self):
        """The X coordinate of the center of the box"""
        return (self._left + self._right) / 2.0

    @midx.setter
    def midx(self, value):
        """Moves the center of the box to the given X coordinate"""
        dx = value - (self._left + self._right) / 2.0
        self._left += dx
        self._right += dx

    @property
    def midy(self):
        """The Y coordinate of the center of the box"""
        return (self._top + self._bottom) / 2.0

    @midy.setter
    def midy(self, value):
        """Moves the center of the box to the given Y coordinate"""
        dy = value - (self._top + self._bottom) / 2.0
        self._top += dy
        self._bottom += dy

    @property
    def shape(self):
        """The shape of the rectangle (width, height)"""
        return self._right - self._left, self._bottom - self._top

    @shape.setter
    def shape(self, shape):
        """Sets the shape of the rectangle (width, height)."""
        self.width, self.height = shape

    def contract(self, margins):
        """Contracts the rectangle by the given margins.

        @return: a new L{Rectangle} object.
        """
        if isinstance(margins, int) or isinstance(margins, float):
            margins = [float(margins)] * 4
        if len(margins) != 4:
            raise ValueError("margins must be a 4-tuple or a single number")
        nx1, ny1 = self._left + margins[0], self._top + margins[1]
        nx2, ny2 = self._right - margins[2], self._bottom - margins[3]
        if nx1 > nx2:
            nx1 = (nx1 + nx2) / 2.0
            nx2 = nx1
        if ny1 > ny2:
            ny1 = (ny1 + ny2) / 2.0
            ny2 = ny1
        return self.__class__(nx1, ny1, nx2, ny2)

    def expand(self, margins):
        """Expands the rectangle by the given margins.

        @return: a new L{Rectangle} object.
        """
        if isinstance(margins, int) or isinstance(margins, float):
            return self.contract(-float(margins))
        return self.contract([-float(margin) for margin in margins])

    def isdisjoint(self, other):
        """Returns C{True} if the two rectangles have no intersection.

        Example::

            >>> r1 = Rectangle(10, 10, 30, 30)
            >>> r2 = Rectangle(20, 20, 50, 50)
            >>> r3 = Rectangle(70, 70, 90, 90)
            >>> r1.isdisjoint(r2)
            False
            >>> r2.isdisjoint(r1)
            False
            >>> r1.isdisjoint(r3)
            True
            >>> r3.isdisjoint(r1)
            True
        """
        return (
            self._left > other._right
            or self._right < other._left
            or self._top > other._bottom
            or self._bottom < other._top
        )

    def isempty(self):
        """Returns C{True} if the rectangle is empty (i.e. it has zero
        width and height).

        Example::

            >>> r1 = Rectangle(10, 10, 30, 30)
            >>> r2 = Rectangle(70, 70, 90, 90)
            >>> r1.isempty()
            False
            >>> r2.isempty()
            False
            >>> r1.intersection(r2).isempty()
            True
        """
        return self._left == self._right and self._top == self._bottom

    def intersection(self, other):
        """Returns the intersection of this rectangle with another.

        Example::

            >>> r1 = Rectangle(10, 10, 30, 30)
            >>> r2 = Rectangle(20, 20, 50, 50)
            >>> r3 = Rectangle(70, 70, 90, 90)
            >>> r1.intersection(r2)
            Rectangle(20.0, 20.0, 30.0, 30.0)
            >>> r2 & r1
            Rectangle(20.0, 20.0, 30.0, 30.0)
            >>> r2.intersection(r1) == r1.intersection(r2)
            True
            >>> r1.intersection(r3)
            Rectangle(0.0, 0.0, 0.0, 0.0)
        """
        if self.isdisjoint(other):
            return Rectangle(0, 0, 0, 0)
        return Rectangle(
            max(self._left, other._left),
            max(self._top, other._top),
            min(self._right, other._right),
            min(self._bottom, other._bottom),
        )

    __and__ = intersection

    def translate(self, dx, dy):
        """Translates the rectangle in-place.

        Example:

            >>> r = Rectangle(10, 20, 50, 70)
            >>> r.translate(30, -10)
            >>> r
            Rectangle(40.0, 10.0, 80.0, 60.0)

        @param dx: the X coordinate of the translation vector
        @param dy: the Y coordinate of the translation vector
        """
        self._left += dx
        self._right += dx
        self._top += dy
        self._bottom += dy

    def union(self, other):
        """Returns the union of this rectangle with another.

        The resulting rectangle is the smallest rectangle that contains both
        rectangles.

        Example::

            >>> r1 = Rectangle(10, 10, 30, 30)
            >>> r2 = Rectangle(20, 20, 50, 50)
            >>> r3 = Rectangle(70, 70, 90, 90)
            >>> r1.union(r2)
            Rectangle(10.0, 10.0, 50.0, 50.0)
            >>> r2 | r1
            Rectangle(10.0, 10.0, 50.0, 50.0)
            >>> r2.union(r1) == r1.union(r2)
            True
            >>> r1.union(r3)
            Rectangle(10.0, 10.0, 90.0, 90.0)
        """
        return Rectangle(
            min(self._left, other._left),
            min(self._top, other._top),
            max(self._right, other._right),
            max(self._bottom, other._bottom),
        )

    __or__ = union

    def __ior__(self, other):
        """Expands this rectangle to include itself and another completely while
        still being as small as possible.

        Example::

            >>> r1 = Rectangle(10, 10, 30, 30)
            >>> r2 = Rectangle(20, 20, 50, 50)
            >>> r3 = Rectangle(70, 70, 90, 90)
            >>> r1 |= r2
            >>> r1
            Rectangle(10.0, 10.0, 50.0, 50.0)
            >>> r1 |= r3
            >>> r1
            Rectangle(10.0, 10.0, 90.0, 90.0)
        """
        self._left = min(self._left, other._left)
        self._top = min(self._top, other._top)
        self._right = max(self._right, other._right)
        self._bottom = max(self._bottom, other._bottom)
        return self

    def __repr__(self):
        return "%s(%s, %s, %s, %s)" % (
            self.__class__.__name__,
            self._left,
            self._top,
            self._right,
            self._bottom,
        )

    def __eq__(self, other):
        return self.coords == other.coords

    def __ne__(self, other):
        return self.coords != other.coords

    def __bool__(self):
        return self._left != self._right or self._top != self._bottom

    def __hash__(self):
        return hash(self.coords)


#####################################################################


class BoundingBox(Rectangle):
    """Class representing a bounding box (a rectangular area) that
    encloses some objects."""

    def __ior__(self, other):
        """Replaces this bounding box with the union of itself and
        another.

        Example::

            >>> box1 = BoundingBox(10, 20, 50, 60)
            >>> box2 = BoundingBox(70, 40, 100, 90)
            >>> box1 |= box2
            >>> print(box1)
            BoundingBox(10.0, 20.0, 100.0, 90.0)
        """
        self._left = min(self._left, other._left)
        self._top = min(self._top, other._top)
        self._right = max(self._right, other._right)
        self._bottom = max(self._bottom, other._bottom)
        return self

    def __or__(self, other):
        """Takes the union of this bounding box with another.

        The result is a bounding box which encloses both bounding
        boxes.

        Example::

            >>> box1 = BoundingBox(10, 20, 50, 60)
            >>> box2 = BoundingBox(70, 40, 100, 90)
            >>> box1 | box2
            BoundingBox(10.0, 20.0, 100.0, 90.0)
        """
        return self.__class__(
            min(self._left, other._left),
            min(self._top, other._top),
            max(self._right, other._right),
            max(self._bottom, other._bottom),
        )


#####################################################################


class FakeModule:
    """Fake module that raises an exception for everything"""

    def __init__(self, message):
        """Constructor.

        @param message: message to print in exceptions raised from this module
        """
        self._message = message

    def __getattr__(self, _):
        raise AttributeError(self._message)

    def __call__(self, _):
        raise TypeError(self._message)

    def __setattr__(self, key, value):
        if key == "_message":
            super().__setattr__(key, value)
        else:
            raise AttributeError(self._message)


#####################################################################


class Point(NamedTuple("_Point", [("x", float), ("y", float)])):
    """Class representing a point on the 2D plane."""

    def __add__(self, other):
        """Adds the coordinates of a point to another one"""
        return self.__class__(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        """Subtracts the coordinates of a point to another one"""
        return self.__class__(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, scalar):
        """Multiplies the coordinates by a scalar"""
        return self.__class__(x=self.x * scalar, y=self.y * scalar)

    __rmul__ = __mul__

    def __div__(self, scalar):
        """Divides the coordinates by a scalar"""
        return self.__class__(x=self.x / scalar, y=self.y / scalar)

    def as_polar(self):
        """Returns the polar coordinate representation of the point.

        @return: the radius and the angle in a tuple.
        """
        return len(self), atan2(self.y, self.x)

    def distance(self, other):
        """Returns the distance of the point from another one.

        Example:

            >>> p1 = Point(5, 7)
            >>> p2 = Point(8, 3)
            >>> p1.distance(p2)
            5.0
        """
        dx, dy = self.x - other.x, self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def interpolate(self, other, ratio=0.5):
        """Linearly interpolates between the coordinates of this point and
        another one.

        @param  other:  the other point
        @param  ratio:  the interpolation ratio between 0 and 1. Zero will
          return this point, 1 will return the other point.
        """
        ratio = float(ratio)
        return self.__class__(
            x=self.x * (1.0 - ratio) + other.x * ratio,
            y=self.y * (1.0 - ratio) + other.y * ratio,
        )

    def length(self):
        """Returns the length of the vector pointing from the origin to this
        point."""
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalized(self):
        """Normalizes the coordinates of the point s.t. its length will be 1
        after normalization. Returns the normalized point."""
        len = self.length()
        if len == 0:
            return self.__class__(x=self.x, y=self.y)
        return self.__class__(x=self.x / len, y=self.y / len)

    def sq_length(self):
        """Returns the squared length of the vector pointing from the origin
        to this point."""
        return self.x ** 2 + self.y ** 2

    def towards(self, other, distance=0):
        """Returns the point that is at a given distance from this point
        towards another one."""
        if not distance:
            return self

        angle = atan2(other.y - self.y, other.x - self.x)
        return self.__class__(
            self.x + distance * cos(angle), self.y + distance * sin(angle)
        )

    @classmethod
    def FromPolar(cls, radius, angle):
        """Constructs a point from polar coordinates.

        C{radius} is the distance of the point from the origin; C{angle} is the
        angle between the X axis and the vector pointing to the point from
        the origin.
        """
        return cls(radius * cos(angle), radius * sin(angle))


def calculate_corner_radii(points, corner_radius):
    """Given a list of points and a desired corner radius, returns a list
    containing proposed corner radii for each of the points such that it is
    ensured that the corner radius at a point is never larger than half of
    the minimum distance between the point and its neighbors.
    """
    points = [Point(*point) for point in points]
    side_vecs = [v - u for u, v in consecutive_pairs(points, circular=True)]
    half_side_lengths = [side.length() / 2 for side in side_vecs]
    corner_radii = [corner_radius] * len(points)
    for idx in range(len(corner_radii)):
        prev_idx = -1 if idx == 0 else idx - 1
        radii = [corner_radius, half_side_lengths[prev_idx], half_side_lengths[idx]]
        corner_radii[idx] = min(radii)
    return corner_radii


def euclidean_distance(x1, y1, x2, y2):
    """Computes the Euclidean distance between points (x1,y1) and (x2,y2)."""
    return hypot(x2 - x1, y2 - y1)


def evaluate_cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, t):
    """Evaluates the Bezier curve from point (x0,y0) to (x3,y3)
    via control points (x1,y1) and (x2,y2) at t. t is typically in the range
    [0; 1] such that 0 returns (x0, y0) and 1 returns (x3, y3).
    """
    xt = (
        (1.0 - t) ** 3 * x0
        + 3.0 * t * (1.0 - t) ** 2 * x1
        + 3.0 * t ** 2 * (1.0 - t) * x2
        + t ** 3 * x3
    )
    yt = (
        (1.0 - t) ** 3 * y0
        + 3.0 * t * (1.0 - t) ** 2 * y1
        + 3.0 * t ** 2 * (1.0 - t) * y2
        + t ** 3 * y3
    )
    return xt, yt


def get_bezier_control_points_for_curved_edge(x1, y1, x2, y2, curvature):
    """Helper function that calculates the Bezier control points for a
    curved edge that goes from (x1, y1) to (x2, y2).
    """
    aux1 = (
        (2 * x1 + x2) / 3.0 - curvature * 0.5 * (y2 - y1),
        (2 * y1 + y2) / 3.0 + curvature * 0.5 * (x2 - x1)
    )
    aux2 = (
        (x1 + 2 * x2) / 3.0 - curvature * 0.5 * (y2 - y1),
        (y1 + 2 * y2) / 3.0 + curvature * 0.5 * (x2 - x1)
    )
    return aux1, aux2


def intersect_bezier_curve_and_circle(
    x0, y0, x1, y1, x2, y2, x3, y3, radius, max_iter=10
):
    """Binary search solver for finding the intersection of a Bezier curve
    and a circle centered at the curve's end point.

    Returns the x, y coordinates of the intersection point.
    """
    # The exact formulation of the problem is a quartic equation and it is
    # probably not worth coding up an exact quartic solver. The solution below
    # uses binary search. Another solution would be simply to intersect the
    # circle with the line pointing from (x2, y2) to (x3, y3) as the difference
    # is likely to be negligible.

    precision = radius / 20.0
    source_target_distance = euclidean_distance(x0, y0, x3, y3)
    radius = float(radius)
    t0 = 1.0
    t1 = 1.0 - radius / source_target_distance

    xt1, yt1 = evaluate_cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, t1)

    distance_t0 = 0
    distance_t1 = euclidean_distance(x3, y3, xt1, yt1)
    counter = 0
    while abs(distance_t1 - radius) > precision and counter < max_iter:
        if ((distance_t1 - radius) > 0) != ((distance_t0 - radius) > 0):
            t_new = (t0 + t1) / 2.0
        else:
            if abs(distance_t1 - radius) < abs(distance_t0 - radius):
                # If t1 gets us closer to the circumference step in the
                # same direction
                t_new = t1 + (t1 - t0) / 2.0
            else:
                t_new = t1 - (t1 - t0)
        t_new = 1 if t_new > 1 else (0 if t_new < 0 else t_new)
        t0, t1 = t1, t_new
        distance_t0 = distance_t1
        xt1, yt1 = evaluate_cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, t1)
        distance_t1 = euclidean_distance(x3, y3, xt1, yt1)
        counter += 1

    return evaluate_cubic_bezier(x0, y0, x1, y1, x2, y2, x3, y3, t1)


def str_to_orientation(value, reversed_horizontal=False, reversed_vertical=False):
    """Tries to interpret a string as an orientation value.

    The following basic values are understood: ``left-right``, ``bottom-top``,
    ``right-left``, ``top-bottom``. Possible aliases are:

      - ``horizontal``, ``horiz``, ``h`` and ``lr`` for ``left-right``

      - ``vertical``, ``vert``, ``v`` and ``tb`` for top-bottom.

      - ``lr`` for ``left-right``.

      - ``rl`` for ``right-left``.

    ``reversed_horizontal`` reverses the meaning of ``horizontal``, ``horiz``
    and ``h`` to ``rl`` (instead of ``lr``); similarly, ``reversed_vertical``
    reverses the meaning of ``vertical``, ``vert`` and ``v`` to ``bt``
    (instead of ``tb``).

    Returns one of ``lr``, ``rl``, ``tb`` or ``bt``, or throws ``ValueError``
    if the string cannot be interpreted as an orientation.
    """

    aliases = {
        "left-right": "lr",
        "right-left": "rl",
        "top-bottom": "tb",
        "bottom-top": "bt",
        "top-down": "tb",
        "bottom-up": "bt",
        "top-bottom": "tb",
        "bottom-top": "bt",
        "td": "tb",
        "bu": "bt",
    }

    dir = ["lr", "rl"][reversed_horizontal]
    aliases.update(horizontal=dir, horiz=dir, h=dir)

    dir = ["tb", "bt"][reversed_vertical]
    aliases.update(vertical=dir, vert=dir, v=dir)

    result = aliases.get(value, value)
    if result not in ("lr", "rl", "tb", "bt"):
        raise ValueError("unknown orientation: %s" % result)
    return result


def autocurve(graph, attribute="curved", default=0):
    """Calculates curvature values for each of the edges in the graph to make
    sure that multiple edges are shown properly on a graph plot.

    This function checks the multiplicity of each edge in the graph and
    assigns curvature values (numbers between -1 and 1, corresponding to
    CCW (-1), straight (0) and CW (1) curved edges) to them. The assigned
    values are either stored in an edge attribute or returned as a list,
    depending on the value of the I{attribute} argument.

    @param graph: the graph on which the calculation will be run
    @param attribute: the name of the edge attribute to save the curvature
      values to. The default value is C{curved}, which is the name of the
      edge attribute the default graph plotter checks to decide whether an
      edge should be curved on the plot or not. If I{attribute} is C{None},
      the result will not be stored.
    @param default: the default curvature for single edges. Zero means that
      single edges will be straight. If you want single edges to be curved
      as well, try passing 0.5 or -0.5 here.
    @return: the list of curvature values if I{attribute} is C{None},
      otherwise C{None}.
    """

    # The following loop could be re-written in C if it turns out to be a
    # bottleneck. Unfortunately we cannot use Graph.count_multiple() here
    # because we have to ignore edge directions.
    multiplicities = defaultdict(list)
    for edge in graph.es:
        u, v = edge.tuple
        if u > v:
            multiplicities[v, u].append(edge.index)
        else:
            multiplicities[u, v].append(edge.index)

    result = [default] * graph.ecount()
    for eids in multiplicities.values():
        # Is it a single edge?
        if len(eids) < 2:
            continue

        if len(eids) % 2 == 1:
            # Odd number of edges; the last will be straight
            result[eids.pop()] = 0

        # Arrange the remaining edges
        curve = 2.0 / (len(eids) + 2)
        dcurve, sign = curve, 1
        for idx, eid in enumerate(eids):
            edge = graph.es[eid]
            if edge.source > edge.target:
                result[eid] = -sign * curve
            else:
                result[eid] = sign * curve
            if idx % 2 == 1:
                curve += dcurve
            sign *= -1

    if attribute is None:
        return result

    graph.es[attribute] = result
