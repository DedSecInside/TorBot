from igraph.drawing.utils import calculate_corner_radii
from igraph.utils import consecutive_pairs

from .utils import find_plotly, format_path_step

__all__ = ("PlotlyPolygonDrawer",)

plotly = find_plotly()


class PlotlyPolygonDrawer:
    """Class that is used to draw polygons in matplotlib.

    The corner points of the polygon can be set by the C{points}
    property of the drawer, or passed at construction time. Most
    drawing methods in this class also have an extra C{points}
    argument that can be used to override the set of points in the
    C{points} property."""

    def __init__(self, fig):
        """Constructs a new polygon drawer that draws on the given
        Matplotlib axes.

        @param  fig: the plotly Figure to draw on
        """
        self.context = fig

    def draw(self, points, corner_radius=0, **kwds):
        """Draws a polygon to the associated axes.

        @param points: the coordinates of the corners of the polygon,
          in clockwise or counter-clockwise order, or C{None} if we are
          about to use the C{points} property of the class.
        @param corner_radius: if zero, an ordinary polygon will be drawn.
          If positive, the corners of the polygon will be rounded with
          the given radius.
        """
        if len(points) < 2:
            # Well, a polygon must have at least two corner points
            return

        fig = self.context
        if corner_radius <= 0:
            # No rounded corners, this is simple
            # We need to repeat the initial point to get a closed shape
            x = [p[0] for p in points] + [points[0][0]]
            y = [p[1] for p in points] + [points[0][1]]
            kwds["mode"] = kwds.get("mode", "line")
            stroke = plotly.graph_objects.Scatter(
                x=x,
                y=y,
                **kwds,
            )
            fig.add_trace(stroke)

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
        path = []
        path.append(
            format_path_step(
                "M",
                [points[-1].towards(points[0], corner_radii[-1])],
            )
        )

        # Now, for each point in points, draw a line towards the
        # corner, stopping before it in a distance of corner_radii[idx],
        # then draw the corner
        u = points[-1]
        for idx, (v, w) in enumerate(consecutive_pairs(points, True)):
            radius = corner_radii[idx]
            path.append(
                format_path_step(
                    "L",
                    [v.towards(u, radius)],
                )
            )

            aux1 = v.towards(u, radius / 2)
            aux2 = v.towards(w, radius / 2)

            path.append(
                format_path_step(
                    "C",
                    [aux1, aux2, v.towards(w, corner_radii[idx])],
                )
            )
            u = v

        # Close path
        path = "".join(path).strip(" ") + " Z"
        stroke = dict(
            type="path",
            path=path,
            **kwds,
        )
        fig.update_layout(
            shapes=[stroke],
        )
