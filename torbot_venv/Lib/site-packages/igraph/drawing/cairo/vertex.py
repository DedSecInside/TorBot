"""This module provides implementations of Cairo-specific vertex drawers, i.e.
drawers that the Cairo graph drawer will use to draw vertices.
"""

from math import pi

from igraph.drawing.baseclasses import AbstractVertexDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.shapes import ShapeDrawerDirectory

from .base import AbstractCairoDrawer

__all__ = ("AbstractCairoVertexDrawer", "CairoVertexDrawer")


class AbstractCairoVertexDrawer(AbstractVertexDrawer, AbstractCairoDrawer):
    """Abstract base class for vertex drawers that draw on a Cairo canvas."""

    def __init__(self, context, bbox, palette, layout):
        """Constructs the vertex drawer and associates it to the given
        Cairo context and the given L{BoundingBox}.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        @param layout:  the layout of the vertices in the graph being drawn
        """
        AbstractCairoDrawer.__init__(self, context, bbox)
        AbstractVertexDrawer.__init__(self, palette, layout)


class CairoVertexDrawer(AbstractCairoVertexDrawer):
    """The default vertex drawer implementation of igraph."""

    def __init__(self, context, bbox, palette, layout):
        super().__init__(context, bbox, palette, layout)
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
            label_size = 14.0
            position = dict(func=self.layout.__getitem__)
            shape = ("circle", ShapeDrawerDirectory.resolve_default)
            size = 20.0
            width = None
            height = None

        return VisualVertexBuilder

    def draw(self, visual_vertex, vertex, coords):
        context = self.context

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

        visual_vertex.shape.draw_path(context, coords[0], coords[1], width, height)
        context.set_source_rgba(*visual_vertex.color)
        context.fill_preserve()
        context.set_source_rgba(*visual_vertex.frame_color)
        context.set_line_width(visual_vertex.frame_width)
        context.stroke()
