"""This module provides implementation for a Matplotlib-specific histogram drawer."""

from igraph.drawing.baseclasses import AbstractDrawer

__all__ = ("MatplotlibHistogramDrawer",)


class MatplotlibHistogramDrawer(AbstractDrawer):
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
        ax = self.context

        xmin = kwds.get("min", self._min)
        ymin = 0
        xmax = kwds.get("max", self._max)
        ymax = kwds.get("max_value", max(self._bins))
        width = self._bin_width

        x = [self._min + width * i for i, _ in enumerate(self._bins)]
        y = self._bins
        # Draw the boxes/bars
        ax.bar(x, y, align="left")
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
