"""This module provides implementation for a Cairo-specific palette drawer"""

from igraph.drawing.cairo.base import AbstractCairoDrawer

__all__ = ("CairoPaletteDrawer",)


class CairoPaletteDrawer(AbstractCairoDrawer):
    """Default Cairo drawer object for palettes"""

    def __init__(self, context):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param context: the context on which we will draw
        """
        super().__init__(context, bbox=None)

    def draw(self, palette, **kwds):
        """TODO"""
        from igraph.datatypes import Matrix
        from igraph.drawing.utils import str_to_orientation

        context = self.context
        orientation = str_to_orientation(kwds.get("orientation", "lr"))

        # Construct a matrix and plot that
        indices = list(range(len(self)))
        if orientation in ("rl", "bt"):
            indices.reverse()
        if orientation in ("lr", "rl"):
            matrix = Matrix([indices])
        else:
            matrix = Matrix([[i] for i in indices])

        bbox = self.bbox = kwds.pop("bbox", None)
        if bbox is None:
            raise ValueError("bbox is required for Cairo plots")

        border_width = float(kwds.get("border_width", 1.0))
        grid_width = float(kwds.get("grid_width", 0.0))

        return matrix.__plot__(
            "cairo",
            context,
            bbox=bbox,
            palette=self,
            style="palette",
            square=False,
            grid_width=grid_width,
            border_width=border_width,
        )
