from igraph.drawing.utils import calculate_corner_radii
from igraph.utils import consecutive_pairs

from .utils import find_matplotlib

__all__ = ("MatplotlibPolygonDrawer",)

mpl, plt = find_matplotlib()


class MatplotlibPolygonDrawer:
    """Class that is used to draw polygons in matplotlib.

    The corner points of the polygon can be set by the C{points}
    property of the drawer, or passed at construction time. Most
    drawing methods in this class also have an extra C{points}
    argument that can be used to override the set of points in the
    C{points} property."""

    def __init__(self, ax):
        """Constructs a new polygon drawer that draws on the given
        Matplotlib axes.

        @param  ax: the matplotlib Axes to draw on
        """
        self.context = ax

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

        ax = self.context
        if corner_radius <= 0:
            # No rounded corners, this is simple
            stroke = mpl.patches.Polygon(points, **kwds)
            ax.add_patch(stroke)

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
        codes = []
        path.append((points[-1].towards(points[0], corner_radii[-1])))
        codes.append(mpl.path.Path.MOVETO)

        # Now, for each point in points, draw a line towards the
        # corner, stopping before it in a distance of corner_radii[idx],
        # then draw the corner
        u = points[-1]
        for idx, (v, w) in enumerate(consecutive_pairs(points, True)):
            radius = corner_radii[idx]
            path.append(v.towards(u, radius))
            codes.append(mpl.path.Path.LINETO)

            aux1 = v.towards(u, radius / 2)
            aux2 = v.towards(w, radius / 2)

            path.append(aux1)
            path.append(aux2)
            path.append(v.towards(w, corner_radii[idx]))
            codes.extend([mpl.path.Path.CURVE4] * 3)
            u = v

        art = mpl.patches.PathPatch(
            mpl.path.Path(path, codes=codes, closed=True),
            transform=ax.transData,
            clip_on=True,
            zorder=4,
            **kwds,
        )
        return art
