# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Shape drawing classes for igraph

Vertex shapes in igraph are usually referred to by short names like
C{"rect"} or C{"circle"}. This module contains the classes that
implement the actual drawing routines for these shapes, and a
resolver class that determines the appropriate shape drawer class
given the short name.

Classes that are derived from L{ShapeDrawer} in this module are
automatically registered by L{ShapeDrawerDirectory}. If you
implement a custom shape drawer, you must register it in
L{ShapeDrawerDirectory} manually if you wish to refer to it by a
name in the C{shape} attribute of vertices.
"""


__all__ = ("ShapeDrawerDirectory",)

from abc import ABCMeta, abstractmethod
from math import atan2, copysign, cos, pi, sin
import sys

from igraph.drawing.matplotlib.utils import find_matplotlib

mpl, plt = find_matplotlib()


class ShapeDrawer(metaclass=ABCMeta):
    """Static class, the ancestor of all vertex shape drawer classes.

    Custom shapes must implement at least the C{draw_path} method of the class.
    The method I{must not} stroke or fill, it should just set up the current
    Cairo path appropriately."""

    @staticmethod
    @abstractmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws the path of the shape on the given Cairo context, without
        stroking or filling it.

        This method must be overridden in derived classes implementing custom shapes
        and declared as a static method using C{staticmethod(...)}.

        @param ctx: the context to draw on
        @param center_x: the X coordinate of the center of the object
        @param center_y: the Y coordinate of the center of the object
        @param width: the width of the object
        @param height: the height of the object. If C{None}, equals to the width.
        """
        raise NotImplementedError

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the shape centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        Can be overridden in derived classes. Must always be defined as a static
        method using C{staticmethod(...)}

        @param width: the width of the shape
        @param height: the height of the shape. If C{None}, defaults to the width
        @return: the intersection point (the closest to (source_x, source_y) if
            there are more than one) or (center_x, center_y) if there is no
            intersection
        """
        return center_x, center_y


class NullDrawer(ShapeDrawer):
    """Static drawer class which draws nothing.

    This class is used for graph vertices with unknown shapes"""

    names = ["null", "none", "empty", "hidden", ""]

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None):
        """Draws nothing."""
        pass


class RectangleDrawer(ShapeDrawer):
    """Static class which draws rectangular vertices"""

    names = "rectangle rect rectangular square box s"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a rectangle-shaped path on the Cairo context without stroking
        or filling it.
        @see: ShapeDrawer.draw_path"""
        height = height or width
        if hasattr(plt, "Axes") and isinstance(ctx, plt.Axes):
            return mpl.patches.Rectangle(
                (center_x - width / 2, center_y - height / 2),
                width,
                height,
                transform=ctx.transData,
                clip_on=True,
                **kwargs,
            )
        else:
            ctx.rectangle(center_x - width / 2, center_y - height / 2, width, height)

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the rectangle centered at (center_x, center_y)
        having the given width and height intersects with a line drawn from
        (source_x, source_y) to (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width
        delta_x, delta_y = center_x - source_x, center_y - source_y

        if delta_x == 0 and delta_y == 0:
            return center_x, center_y

        if delta_y > 0 and delta_x <= delta_y and delta_x >= -delta_y:
            # this is the top edge
            ry = center_y - height / 2
            ratio = (height / 2) / delta_y
            return center_x - ratio * delta_x, ry

        if delta_y < 0 and delta_x <= -delta_y and delta_x >= delta_y:
            # this is the bottom edge
            ry = center_y + height / 2
            ratio = (height / 2) / -delta_y
            return center_x - ratio * delta_x, ry

        if delta_x > 0 and delta_y <= delta_x and delta_y >= -delta_x:
            # this is the left edge
            rx = center_x - width / 2
            ratio = (width / 2) / delta_x
            return rx, center_y - ratio * delta_y

        if delta_x < 0 and delta_y <= -delta_x and delta_y >= delta_x:
            # this is the right edge
            rx = center_x + width / 2
            ratio = (width / 2) / -delta_x
            return rx, center_y - ratio * delta_y

        if delta_x == 0:
            if delta_y > 0:
                return center_x, center_y - height / 2
            return center_x, center_y + height / 2

        if delta_y == 0:
            if delta_x > 0:
                return center_x - width / 2, center_y
            return center_x + width / 2, center_y


class CircleDrawer(ShapeDrawer):
    """Static class which draws circular vertices"""

    names = "circle circular o"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a circular path on the Cairo context without stroking or
        filling it.

        Height is ignored, it is the width that determines the diameter of the circle.

        @see: ShapeDrawer.draw_path"""
        if hasattr(plt, "Axes") and isinstance(ctx, plt.Axes):
            return mpl.patches.Circle(
                (center_x, center_y),
                width / 2,
                transform=ctx.transData,
                clip_on=True,
                **kwargs,
            )
        else:
            ctx.arc(center_x, center_y, width / 2, 0, 2 * pi)

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the circle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width
        angle = atan2(center_y - source_y, center_x - source_x)
        return center_x - width / 2 * cos(angle), center_y - height / 2 * sin(angle)


class UpTriangleDrawer(ShapeDrawer):
    """Static class which draws upright triangles"""

    names = "triangle triangle-up up-triangle arrow arrow-up up-arrow ^"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws an upright triangle on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if hasattr(plt, "Axes") and isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y - 0.333 * height],
                [center_x + 0.5 * width, center_y - 0.333 * height],
                [center_x, center_x + 0.667 * height],
            ]
            return mpl.patches.Polygon(
                vertices,
                closed=True,
                transform=ctx.transData,
                clip_on=True,
                **kwargs,
            )
        else:
            ctx.move_to(center_x - width / 2, center_y + height / 2)
            ctx.line_to(center_x, center_y - height / 2)
            ctx.line_to(center_x + width / 2, center_y + height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the triangle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        # TODO: finish it properly
        height = height or width
        return center_x, center_y


class DownTriangleDrawer(ShapeDrawer):
    """Static class which draws triangles pointing down"""

    names = "down-triangle triangle-down arrow-down down-arrow v"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a triangle on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if hasattr(plt, "Axes") and isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y + 0.333 * height],
                [center_x + 0.5 * width, center_y + 0.333 * height],
                [center_x, center_y - 0.667 * height],
            ]
            return mpl.patches.Polygon(
                vertices,
                closed=True,
                transform=ctx.transData,
                clip_on=True,
                **kwargs,
            )

        else:
            ctx.move_to(center_x - width / 2, center_y - height / 2)
            ctx.line_to(center_x, center_y + height / 2)
            ctx.line_to(center_x + width / 2, center_y - height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the triangle centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        # TODO: finish it properly
        height = height or width
        return center_x, center_y


class DiamondDrawer(ShapeDrawer):
    """Static class which draws diamonds (i.e. rhombuses)"""

    names = "diamond rhombus d"

    @staticmethod
    def draw_path(ctx, center_x, center_y, width, height=None, **kwargs):
        """Draws a rhombus on the Cairo context without stroking or
        filling it.

        @see: ShapeDrawer.draw_path"""
        height = height or width
        if hasattr(plt, "Axes") and isinstance(ctx, plt.Axes):
            vertices = [
                [center_x - 0.5 * width, center_y],
                [center_x, center_y - 0.5 * height],
                [center_x + 0.5 * width, center_y],
                [center_x, center_y + 0.5 * height],
            ]
            return mpl.patches.Polygon(
                vertices,
                closed=True,
                transform=ctx.transData,
                clip_on=True,
                **kwargs,
            )
        else:
            ctx.move_to(center_x - width / 2, center_y)
            ctx.line_to(center_x, center_y + height / 2)
            ctx.line_to(center_x + width / 2, center_y)
            ctx.line_to(center_x, center_y - height / 2)
            ctx.close_path()

    @staticmethod
    def intersection_point(center_x, center_y, source_x, source_y, width, height=None):
        """Determines where the rhombus centered at (center_x, center_y)
        intersects with a line drawn from (source_x, source_y) to
        (center_x, center_y).

        @see: ShapeDrawer.intersection_point"""
        height = height or width

        if height == 0 and width == 0:
            return center_x, center_y

        delta_x, delta_y = source_x - center_x, source_y - center_y

        # Treat edge case when delta_x = 0
        if delta_x == 0:
            if delta_y == 0:
                return center_x, center_y
            else:
                return center_x, center_y + copysign(height / 2, delta_y)

        width = copysign(width, delta_x)
        height = copysign(height, delta_y)

        f = height / (height + width * delta_y / delta_x)
        return center_x + f * width / 2, center_y + (1 - f) * height / 2


#####################################################################


class ShapeDrawerDirectory:
    """Static class that resolves shape names to their corresponding
    shape drawer classes.

    Classes that are derived from L{ShapeDrawer} in this module are
    automatically registered by L{ShapeDrawerDirectory} when the module
    is loaded for the first time.
    """

    known_shapes = {}

    @classmethod
    def register(cls, drawer_class):
        """Registers the given shape drawer class under the given names.

        @param drawer_class: the shape drawer class to be registered
        """
        names = drawer_class.names
        if isinstance(names, str):
            names = names.split()

        for name in names:
            cls.known_shapes[name] = drawer_class

    @classmethod
    def register_namespace(cls, namespace):
        """Registers all L{ShapeDrawer} classes in the given namespace

        @param namespace: a Python dict mapping names to Python objects."""
        for name, value in namespace.items():
            if name.startswith("__"):
                continue
            if isinstance(value, type):
                if issubclass(value, ShapeDrawer) and value != ShapeDrawer:
                    cls.register(value)

    @classmethod
    def resolve(cls, shape):
        """Given a shape name, returns the corresponding shape drawer class

        @param shape: the name of the shape
        @return: the corresponding shape drawer class

        @raise ValueError: if the shape is unknown
        """
        try:
            return cls.known_shapes[shape]
        except KeyError:
            raise ValueError("unknown shape: %s" % shape)

    @classmethod
    def resolve_default(cls, shape, default=NullDrawer):
        """Given a shape name, returns the corresponding shape drawer class
        or the given default shape drawer if the shape name is unknown.

        @param shape: the name of the shape
        @param default: the default shape drawer to return when the shape
          is unknown
        @return: the shape drawer class corresponding to the given name or
          the default shape drawer class if the name is unknown
        """
        return cls.known_shapes.get(shape, default)


ShapeDrawerDirectory.register_namespace(sys.modules[__name__].__dict__)
