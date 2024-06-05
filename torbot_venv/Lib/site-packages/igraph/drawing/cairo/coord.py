"""
Coordinate systems and related plotting routines
"""

from abc import abstractmethod

from igraph.drawing.cairo.base import AbstractCairoDrawer
from igraph.drawing.utils import BoundingBox

#####################################################################


class CoordinateSystem(AbstractCairoDrawer):
    """Class implementing a coordinate system object.

    Coordinate system objects are used when drawing plots which
    2D or 3D coordinate system axes. This is an abstract class
    which must be extended in order to use it. In general, you'll
    only need the documentation of this class if you intend to
    implement an own coordinate system not present in igraph yet.
    """

    @abstractmethod
    def draw(self):
        """Draws the coordinate system.

        This method must be overridden in derived classes.
        """
        raise NotImplementedError

    @abstractmethod
    def local_to_context(self, x, y):
        """Converts local coordinates to the context coordinate system (given
        by the bounding box).

        This method must be overridden in derived classes."""
        raise NotImplementedError


class DescartesCoordinateSystem(CoordinateSystem):
    """Class implementing a 2D Descartes coordinate system object."""

    def __init__(self, context, bbox, bounds):
        """Initializes the coordinate system.

        @param context: the context on which the coordinate system will
          be drawn.
        @param bbox: the bounding box that will contain the coordinate
          system.
        @param bounds: minimum and maximum X and Y values in a 4-tuple.
        """
        self._bounds, self._bbox = None, None
        self._sx, self._sy = None, None
        self._ox, self._oy, self._ox2, self._oy2 = None, None, None, None

        super().__init__(context, bbox)

        self.bbox = bbox
        self.bounds = bounds

    @property
    def bbox(self):
        """Returns the bounding box of the coordinate system"""
        return BoundingBox(self._bbox.coords)

    @bbox.setter
    def bbox(self, bbox):
        """Sets the bounding box of the coordinate system"""
        self._bbox = bbox
        self._recalc_scale_factors()

    @property
    def bounds(self):
        """Returns the lower and upper bounds of the X and Y values"""
        return self._bounds.coords

    @bounds.setter
    def bounds(self, bounds):
        """Sets the lower and upper bounds of the X and Y values"""
        self._bounds = BoundingBox(bounds)
        self._recalc_scale_factors()

    def _recalc_scale_factors(self):
        """Recalculates some cached scale factors used within the class"""
        if self._bounds is None:
            return
        self._sx = self._bbox.width / self._bounds.width
        self._sy = self._bbox.height / self._bounds.height
        self._ox = self._bounds.left
        self._oy = self._bounds.top
        self._ox2 = self._bbox.left
        self._oy2 = self._bbox.bottom

    def draw(self):
        """Draws the coordinate system."""
        # Draw the frame
        coords = self.bbox.coords
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.rectangle(
            coords[0], coords[1], coords[2] - coords[0], coords[3] - coords[1]
        )
        self.context.stroke()

    def local_to_context(self, x, y):
        """Converts local coordinates to the context coordinate system (given
        by the bounding box).
        """
        return (x - self._ox) * self._sx + self._ox2, self._oy2 - (
            y - self._oy
        ) * self._sy
