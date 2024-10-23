"""This module provides implementation for a Matplotlib-specific palette drawer."""

from igraph.drawing.baseclasses import AbstractDrawer

__all__ = ("MatplotlibPaletteDrawer",)


class MatplotlibPaletteDrawer(AbstractDrawer):
    """Matplotlib drawer object for matrices."""

    def __init__(self, ax):
        """Constructs the drawer and associates it to the given Axes.

        @param ax: the Axes on which we will draw
        """
        self.context = ax

    def draw(self, matrix, **kwds):
        """Draws the given Matrix in a matplotlib Axes.

        @param matrix: the igraph.Histogram to plot.

        """
        from igraph.datatypes import Matrix
        from igraph.drawing.utils import find_matplotlib, str_to_orientation

        mpl, _ = find_matplotlib()
        ax = self.context

        orientation = str_to_orientation(kwds.get("orientation", "lr"))

        # Construct a matrix and plot that
        indices = list(range(len(self)))
        if orientation in ("rl", "bt"):
            indices.reverse()
        if orientation in ("lr", "rl"):
            matrix = Matrix([indices])
        else:
            matrix = Matrix([[i] for i in indices])

        cmap = mpl.colors.ListedColormap(
            [self.get(i) for i in range(self.length)],
        )
        matrix.__plot__(
            "matplotlib",
            ax,
            cmap=cmap,
            **kwds,
        )
