"""Vertices drawer. Unlike other backends, all vertices are drawn at once"""

from math import pi

from igraph.drawing.baseclasses import AbstractVertexDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from .utils import find_plotly, format_rgba

__all__ = ("PlotlyVerticesDrawer",)

plotly = find_plotly()


class PlotlyVerticesDrawer(AbstractVertexDrawer):
    """Plotly backend-specific vertex drawer."""

    def __init__(self, fig, palette, layout):
        self.fig = fig
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
            label_color = "black"
            font = "sans-serif"
            label_size = 12.0
            # FIXME? mpl.rcParams["font.size"])
            position = dict(func=self.layout.__getitem__)
            shape = "circle"
            size = 20.0
            width = None
            height = None
            zorder = 2

        return VisualVertexBuilder

    def draw(self, visual_vertex, vertex, point):
        if visual_vertex.size <= 0:
            return

        fig = self.fig

        marker_kwds = {}
        marker_kwds["x"] = [point[0]]
        marker_kwds["y"] = [point[1]]
        marker_kwds["marker"] = {
            "symbol": visual_vertex.shape,
            "size": visual_vertex.size,
            "color": format_rgba(visual_vertex.color),
            "line_color": format_rgba(visual_vertex.frame_color),
        }

        # if visual_vertex.label is not None:
        #    text_kwds['x'].append(point[0])
        #    text_kwds['y'].append(point[1])
        #    text_kwds['text'].append(visual_vertex.label)

        # Draw dots
        stroke = plotly.graph_objects.Scatter(
            mode="markers",
            **marker_kwds,
        )
        fig.add_trace(stroke)

    def draw_label(self, visual_vertex, point, **kwds):
        if visual_vertex.label is None:
            return

        fig = self.fig

        text_kwds = {}
        text_kwds["x"] = [point[0]]
        text_kwds["y"] = [point[1]]
        text_kwds["text"].append(visual_vertex.label)

        # TODO: add more options

        # Draw text labels
        stroke = plotly.graph_objects.Scatter(
            mode="text",
            **text_kwds,
        )
        fig.add_trace(stroke)
