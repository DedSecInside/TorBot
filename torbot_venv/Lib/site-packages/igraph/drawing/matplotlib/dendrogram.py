"""
Drawing routines to draw the matrices.

This module provides implementations of matrix drawers.
"""

from igraph.drawing.baseclasses import AbstractDrawer
from igraph.drawing.utils import str_to_orientation

from .utils import find_matplotlib

__all__ = ("MatplotlibDendrogramDrawer",)

mpl, _ = find_matplotlib()


class MatplotlibDendrogramDrawer(AbstractDrawer):
    """Matplotlib drawer object for dendrograms."""

    def __init__(self, ax):
        """Constructs the drawer and associates it to the given Axes.

        @param ax: the Axes on which we will draw
        """
        super().__init__()
        self.context = ax

    def _plot_item(self, dendro, ax, orientation, idx, x, y):
        """Plots a dendrogram item to the given Cairo context

        @param dendro: the dendrogram object
        @param orientation: whether the dendrogram is horizontally oriented
        @param idx: the index of the item
        @param x: the X position of the item
        @param y: the Y position of the item
        """
        if dendro._names is None or dendro._names[idx] is None:
            return

        if orientation == "lr":
            ha, va, rotation = "right", "center", 0
        elif orientation == "rl":
            ha, va, rotation = "left", "center", 0
        elif orientation == "tb":
            ha, va, rotation = "center", "bottom", 90
        else:
            ha, va, rotation = "center", "top", 90

        # TODO: offset a little? But remember zoom in callbacks

        ax.text(
            x,
            y,
            dendro._names[idx],
            ha=ha,
            va=va,
            rotation=rotation,
        )

    def draw(self, dendro, orientation="lr", **kwds):
        """Draws the given Dendrogram in a matplotlib Axes.

        Other keyword arguments are passed to mpl.patches.Polygon.

        @param dendro: the igraph.Dendrogram to plot.
        @param orientation: the direction of the plot. Accepted values are "lr"
          (root on the right), "rl" (root on the left), "tb" (root at the bottom),
          and "bt" (root at the top). A few aliases are available (see
          L{utils.str_to_orientation}).
        """
        from igraph.layout import Layout

        ax = self.context

        # Pop unneeded arguments from kwds that are passed down to us by
        # default but cannot be interpreted by Matplotlib
        kwds.pop("palette", None)

        # Styling defaults
        kwds["edgecolor"] = kwds.pop("color", "black")
        if ("lw" not in kwds) and ("linewidth" not in kwds):
            kwds["linewidth"] = 1

        if dendro._names is None:
            dendro._names = [str(x) for x in range(dendro._nitems)]

        orientation = str_to_orientation(orientation, reversed_vertical=True)
        horiz = orientation in ("lr", "rl")

        # Calculate node coordinates
        layout = Layout([(0, 0)] * dendro._nitems, dim=2)
        inorder = dendro._traverse_inorder()
        if not horiz:
            x, y = 0, 0
            # Leaves
            for idx, element in enumerate(inorder):
                layout[element] = (x, 0)
                x += 1

            # Internal nodes
            for id1, id2 in dendro._merges:
                x = (layout[id1][0] + layout[id2][0]) / 2.0
                # TODO: this is a little restrictive, but alright
                # for such a simple layout. More complex tree layouts
                # should be in a separate Layout anyway
                y += 1
                layout.append((x, y))

            # Mirror or rotate the layout if necessary
            if orientation == "bt":
                layout.mirror(1)
        else:
            x, y = 0, 0
            for idx, element in enumerate(inorder):
                layout[element] = (0, y)
                y += 1

            for id1, id2 in dendro._merges:
                y = (layout[id1][1] + layout[id2][1]) / 2.0
                # TODO: this is a little restrictive, but alright
                # for such a simple layout. More complex tree layouts
                # should be in a separate Layout anyway
                x += 1
                layout.append((x, y))

            # Mirror or rotate the layout if necessary
            if orientation == "rl":
                layout.mirror(0)

        # Draw leaf names
        #
        # for idx in range(dendro._nitems):
        #    x, y = layout[idx]
        #    self._plot_item(dendro, ax, orientation, idx, x, y)
        ticks, ticklabels = [], []
        for idx in range(dendro._nitems):
            x, y = layout[idx]
            if not horiz:
                ticks.append(x)
            else:
                ticks.append(y)
            ticklabels.append(dendro._names[idx])

        if not horiz:
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticklabels)
            ax.set_yticks([])
        else:
            ax.set_yticks(ticks)
            ax.set_yticklabels(ticklabels)
            ax.set_xticks([])

        # Draw dendrogram lines
        # Each path is a U-shaped fork
        if not horiz:
            for idx, (id1, id2) in enumerate(dendro._merges):
                x0, y0 = layout[id1]
                x1, y1 = layout[id2]
                x2, y2 = layout[idx + dendro._nitems]
                poly = mpl.patches.Polygon(
                    [[x0, y0], [x0, y2], [x1, y2], [x1, y1]],
                    closed=False,
                    facecolor="none",
                    **kwds,
                )
                ax.add_patch(poly)
        else:
            for idx, (id1, id2) in enumerate(dendro._merges):
                x0, y0 = layout[id1]
                x1, y1 = layout[id2]
                x2, y2 = layout[idx + dendro._nitems]
                poly = mpl.patches.Polygon(
                    [[x0, y0], [x2, y0], [x2, y1], [x1, y1]],
                    closed=False,
                    facecolor="none",
                    **kwds,
                )
                ax.add_patch(poly)

        ax.autoscale_view()
