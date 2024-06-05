from igraph.drawing.utils import calculate_corner_radii
from igraph.utils import consecutive_pairs

from .base import AbstractCairoDrawer

__all__ = ("CairoPolygonDrawer",)


class CairoPolygonDrawer(AbstractCairoDrawer):
    """Class that is used to draw polygons in Cairo.

    The corner points of the polygon can be set by the C{points}
    property of the drawer, or passed at construction time. Most
    drawing methods in this class also have an extra C{points}
    argument that can be used to override the set of points in the
    C{points} property."""

    def __init__(self, context, bbox=(1, 1)):
        """Constructs a new polygon drawer that draws on the given
        Cairo context.

        @param  context: the Cairo context to draw on
        @param  bbox:    ignored, leave it at its default value
        """
        super().__init__(context, bbox)

    def draw_path(self, points, corner_radius=0):
        """Sets up a Cairo path for the outline of a polygon on the given
        Cairo context.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order.
        @param corner_radius: if zero, an ordinary polygon will be drawn.
          If positive, the corners of the polygon will be rounded with
          the given radius.
        """
        self.context.new_path()

        if len(points) < 2:
            # Well, a polygon must have at least two corner points
            return

        ctx = self.context
        if corner_radius <= 0:
            # No rounded corners, this is simple
            ctx.move_to(*points[-1])
            for point in points:
                ctx.line_to(*point)
            return

        # Rounded corners. First, we will take each side of the
        # polygon and find what the corner radius should be on
        # each corner. If the side is longer than 2r (where r is
        # equal to corner_radius), the radius allowed by that side
        # is r; if the side is shorter, the radius is the length
        # of the side / 2. For each corner, the final corner radius
        # is the smaller of the radii on the two sides adjacent to
        # the corner.
        corner_radii = calculate_corner_radii(points, corner_radius)

        # Okay, move to the last corner, adjusted by corner_radii[-1]
        # towards the first corner
        ctx.move_to(*(points[-1].towards(points[0], corner_radii[-1])))
        # Now, for each point in points, draw a line towards the
        # corner, stopping before it in a distance of corner_radii[idx],
        # then draw the corner
        u = points[-1]
        for idx, (v, w) in enumerate(consecutive_pairs(points, True)):
            radius = corner_radii[idx]
            ctx.line_to(*v.towards(u, radius))
            aux1 = v.towards(u, radius / 2)
            aux2 = v.towards(w, radius / 2)
            ctx.curve_to(
                aux1.x, aux1.y, aux2.x, aux2.y, *v.towards(w, corner_radii[idx])
            )
            u = v

    def draw(self, points):
        """Draws the polygon using the current stroke of the Cairo context.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order.
        """
        self.draw_path(points)
        self.context.stroke()
