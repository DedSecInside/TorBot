"""This module provides implementation for a Cairo-specific histogram drawer"""

from igraph.drawing.cairo.base import AbstractCairoDrawer

__all__ = ("CairoHistogramDrawer",)


class CairoHistogramDrawer(AbstractCairoDrawer):
    """Default Cairo drawer object for histograms"""

    def __init__(self, context):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param context: the context on which we will draw
        """
        super().__init__(context, bbox=None)

    def draw(self, histogram, **kwds):
        """TODO"""
        from igraph.drawing.cairo.coord import DescartesCoordinateSystem

        context = self.context

        bbox = self.bbox = kwds.pop("bbox", None)
        if bbox is None:
            raise ValueError("bbox is required for Cairo plots")

        xmin = kwds.get("min", self._min)
        ymin = 0
        xmax = kwds.get("max", self._max)
        ymax = kwds.get("max_value", max(self._bins))
        width = self._bin_width

        coord_system = DescartesCoordinateSystem(
            context,
            bbox,
            (xmin, ymin, xmax, ymax),
        )

        # Draw the boxes
        context.set_line_width(1)
        context.set_source_rgb(1.0, 0.0, 0.0)
        x = self._min
        for value in self._bins:
            top_left_x, top_left_y = coord_system.local_to_context(x, value)
            x += width
            bottom_right_x, bottom_right_y = coord_system.local_to_context(x, 0)
            context.rectangle(
                top_left_x,
                top_left_y,
                bottom_right_x - top_left_x,
                bottom_right_y - top_left_y,
            )
            context.fill()

        # Draw the axes
        coord_system.draw()
