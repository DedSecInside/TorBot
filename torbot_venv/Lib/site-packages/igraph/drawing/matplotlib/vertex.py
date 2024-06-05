"""This module provides implementations of Matplotlib-specific vertex drawers,
i.e. drawers that the Matplotlib graph drawer will use to draw vertices.
"""

from math import pi

from igraph.drawing.baseclasses import AbstractVertexDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.shapes import ShapeDrawerDirectory

__all__ = ("MatplotlibVertexDrawer",)


class MatplotlibVertexDrawer(AbstractVertexDrawer):
    """Matplotlib backend-specific vertex drawer."""

    def __init__(self, ax, palette, layout):
        self.context = ax
        super().__init__(palette, layout)
        self.VisualVertexBuilder = self._construct_visual_vertex_builder()

    def _construct_visual_vertex_builder(self):
        class VisualVertexBuilder(AttributeCollectorBase):
            """Collects some visual properties of a vertex for drawing"""

            _kwds_prefix = "vertex_"
            color = ("red", self.palette.get)
            frame_color = ("black", self.palette.get)
            frame_width = 1.0
            label = None
            label_angle = -pi / 2
            label_dist = 0.0
            label_color = ("black", self.palette.get)
            font = "sans-serif"
            label_size = 12.0
            # FIXME? mpl.rcParams["font.size"])
            position = dict(func=self.layout.__getitem__)
            shape = ("circle", ShapeDrawerDirectory.resolve_default)
            size = 0.2
            width = None
            height = None
            zorder = 2

        return VisualVertexBuilder

    def draw(self, visual_vertex, vertex, coords):
        """Build the Artist for a vertex and return it."""
        ax = self.context

        width = (
            visual_vertex.width
            if visual_vertex.width is not None
            else visual_vertex.size
        )
        height = (
            visual_vertex.height
            if visual_vertex.height is not None
            else visual_vertex.size
        )

        art = visual_vertex.shape.draw_path(
            ax,
            coords[0],
            coords[1],
            width,
            height,
            facecolor=visual_vertex.color,
            edgecolor=visual_vertex.frame_color,
            linewidth=visual_vertex.frame_width,
            zorder=visual_vertex.zorder,
        )
        return art
