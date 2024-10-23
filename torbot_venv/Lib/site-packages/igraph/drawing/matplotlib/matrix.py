"""This module provides implementation for a Matplotlib-specific matrix drawer."""

from igraph.drawing.baseclasses import AbstractDrawer

__all__ = ("MatplotlibMatrixDrawer",)


class MatplotlibMatrixDrawer(AbstractDrawer):
    """Matplotlib drawer object for matrices."""

    def __init__(self, ax):
        """Constructs the drawer and associates it to the given Axes.

        @param ax: the Axes on which we will draw
        """
        self.context = ax

    def draw(self, matrix, **kwds):
        """Draws the given Matrix in a matplotlib Axes.

        @param matrix: the igraph.Matrix to plot.

        Keyword arguments are passed to Axes.imshow.
        """
        ax = self.context
        ax.imshow(matrix.data, interpolation="nearest", **kwds)
