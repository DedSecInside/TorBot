"""
Drawers for various edge styles in graph plots.
"""

from math import atan2, cos, pi, sin

from igraph.drawing.baseclasses import AbstractEdgeDrawer
from igraph.drawing.colors import clamp
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.utils import (
    euclidean_distance,
    get_bezier_control_points_for_curved_edge,
    intersect_bezier_curve_and_circle,
)

from .utils import find_cairo

__all__ = (
    "AbstractCairoEdgeDrawer",
    "AlphaVaryingEdgeDrawer",
    "CairoArrowEdgeDrawer",
    "DarkToLightEdgeDrawer",
    "LightToDarkEdgeDrawer",
    "TaperedEdgeDrawer",
)

cairo = find_cairo()


class AbstractCairoEdgeDrawer(AbstractEdgeDrawer):
    """Cairo-specific abstract edge drawer object."""

    def __init__(self, context, palette):
        """Constructs the edge drawer.

        @param context: a Cairo context on which the edges will be drawn.
        @param palette: the palette that can be used to map integer color
            indices to colors when drawing edges
        """
        self.context = context
        self.palette = palette
        self.VisualEdgeBuilder = self._construct_visual_edge_builder()

    def _construct_visual_edge_builder(self):
        """Construct the visual edge builder that will collect the visual
        attributes of an edge when it is being drawn."""

        class VisualEdgeBuilder(AttributeCollectorBase):
            """Builder that collects some visual properties of an edge for
            drawing"""

            _kwds_prefix = "edge_"
            arrow_size = 1.0
            arrow_width = 1.0
            color = ("#444", self.palette.get)
            curved = (0.0, self._curvature_to_float)
            label = None
            label_color = ("black", self.palette.get)
            label_size = 12.0
            font = "sans-serif"
            width = 1.0

        return VisualEdgeBuilder

    def draw_loop_edge(self, edge, vertex):
        """Draws a loop edge.

        The default implementation draws a small circle.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param vertex: the vertex to which the edge is attached. Visual
          properties are given again as attributes.
        """
        ctx = self.context
        ctx.set_source_rgba(*edge.color)
        ctx.set_line_width(edge.width)
        radius = vertex.size * 1.5
        center_x = vertex.position[0] + cos(pi / 4) * radius / 2.0
        center_y = vertex.position[1] - sin(pi / 4) * radius / 2.0
        ctx.arc(center_x, center_y, radius / 2.0, 0, pi * 2)
        ctx.stroke()

    def draw_undirected_edge(self, edge, src_vertex, dest_vertex):
        """Draws an undirected edge.

        The default implementation of this method draws undirected edges
        as straight lines. Loop edges are drawn as small circles.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are given
          again as attributes.
        @param dest_vertex: the target vertex. Visual properties are given
          again as attributes.
        """
        if src_vertex == dest_vertex:  # TODO
            return self.draw_loop_edge(edge, src_vertex)

        ctx = self.context
        ctx.set_source_rgba(*edge.color)
        ctx.set_line_width(edge.width)
        ctx.move_to(*src_vertex.position)

        if edge.curved:
            (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                x1, y1, x2, y2, edge.curved,
            )
            ctx.curve_to(aux1[0], aux1[1], aux2[0], aux2[1], *dest_vertex.position)
        else:
            ctx.line_to(*dest_vertex.position)

        ctx.stroke()


class CairoArrowEdgeDrawer(AbstractCairoEdgeDrawer):
    """Edge drawer implementation that draws undirected edges as
    straight lines and directed edges as arrows.
    """

    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        if src_vertex == dest_vertex:  # TODO
            return self.draw_loop_edge(edge, src_vertex)

        ctx = self.context
        (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
        (x_src, y_src), (x_dest, y_dest) = src_vertex.position, dest_vertex.position

        # Draw the edge
        ctx.set_source_rgba(*edge.color)
        ctx.set_line_width(edge.width)
        ctx.move_to(x1, y1)

        if edge.curved:
            # Calculate the curve
            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                x1, y1, x2, y2, edge.curved
            )

            # Coordinates of the control points of the Bezier curve
            xc1, yc1 = aux1
            xc2, yc2 = aux2

            # Determine where the edge intersects the circumference of the
            # vertex shape: Tip of the arrow
            x2, y2 = intersect_bezier_curve_and_circle(
                x_src, y_src, xc1, yc1, xc2, yc2, x_dest, y_dest, dest_vertex.size / 2.0
            )

            # Calculate the arrow head coordinates
            angle = atan2(y_dest - y2, x_dest - x2)  # navid
            arrow_size = 15.0 * edge.arrow_size
            arrow_width = 10.0 / edge.arrow_width
            aux_points = [
                (
                    x2 - arrow_size * cos(angle - pi / arrow_width),
                    y2 - arrow_size * sin(angle - pi / arrow_width),
                ),
                (
                    x2 - arrow_size * cos(angle + pi / arrow_width),
                    y2 - arrow_size * sin(angle + pi / arrow_width),
                ),
            ]

            # Midpoint of the base of the arrow triangle
            x_arrow_mid, y_arrow_mid = (aux_points[0][0] + aux_points[1][0]) / 2.0, (
                aux_points[0][1] + aux_points[1][1]
            ) / 2.0

            # Vector representing the base of the arrow triangle
            x_arrow_base_vec, y_arrow_base_vec = (
                aux_points[0][0] - aux_points[1][0]
            ), (aux_points[0][1] - aux_points[1][1])

            # Recalculate the curve such that it lands on the base of the arrow triangle
            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                x1, y1, x_arrow_mid, y_arrow_mid, edge.curved
            )

            # Offset the second control point (aux2) such that it falls precisely
            # on the normal to the arrow base vector. Strictly speaking,
            # offset_length is the offset length divided by the length of the
            # arrow base vector.
            offset_length = (x_arrow_mid - aux2[0]) * x_arrow_base_vec + (
                y_arrow_mid - aux2[1]
            ) * y_arrow_base_vec
            offset_length /= (
                euclidean_distance(0, 0, x_arrow_base_vec, y_arrow_base_vec) ** 2
            )

            aux2 = (
                aux2[0] + x_arrow_base_vec * offset_length,
                aux2[1] + y_arrow_base_vec * offset_length,
            )

            # Draw the curve from the first vertex to the midpoint of the base
            # of the arrow head
            ctx.curve_to(aux1[0], aux1[1], aux2[0], aux2[1], x_arrow_mid, y_arrow_mid)
        else:
            # Determine where the edge intersects the circumference of the
            # vertex shape.
            x2, y2 = dest_vertex.shape.intersection_point(
                x2, y2, x1, y1, dest_vertex.size
            )

            # Draw the arrowhead
            angle = atan2(y_dest - y2, x_dest - x2)
            arrow_size = 15.0 * edge.arrow_size
            arrow_width = 10.0 / edge.arrow_width
            aux_points = [
                (
                    x2 - arrow_size * cos(angle - pi / arrow_width),
                    y2 - arrow_size * sin(angle - pi / arrow_width),
                ),
                (
                    x2 - arrow_size * cos(angle + pi / arrow_width),
                    y2 - arrow_size * sin(angle + pi / arrow_width),
                ),
            ]

            # Midpoint of the base of the arrow triangle
            x_arrow_mid, y_arrow_mid = (aux_points[0][0] + aux_points[1][0]) / 2.0, (
                aux_points[0][1] + aux_points[1][1]
            ) / 2.0

            # Draw the line
            ctx.line_to(x_arrow_mid, y_arrow_mid)

        # Draw the edge
        ctx.stroke()

        # Draw the arrow head
        ctx.move_to(x2, y2)
        ctx.line_to(*aux_points[0])
        ctx.line_to(*aux_points[1])
        ctx.line_to(x2, y2)
        ctx.fill()


class TaperedEdgeDrawer(AbstractCairoEdgeDrawer):
    """Edge drawer implementation that draws undirected edges as
    straight lines and directed edges as tapered lines that are
    wider at the source and narrow at the destination.
    """

    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        if src_vertex == dest_vertex:  # TODO
            return self.draw_loop_edge(edge, src_vertex)

        # Determine where the edge intersects the circumference of the
        # destination vertex.
        src_pos, dest_pos = src_vertex.position, dest_vertex.position
        dest_pos = dest_vertex.shape.intersection_point(
            dest_pos[0], dest_pos[1], src_pos[0], src_pos[1], dest_vertex.size
        )

        ctx = self.context

        # Draw the edge
        ctx.set_source_rgba(*edge.color)
        ctx.set_line_width(edge.width)
        angle = atan2(dest_pos[1] - src_pos[1], dest_pos[0] - src_pos[0])
        arrow_size = src_vertex.size / 4.0
        aux_points = [
            (
                src_pos[0] + arrow_size * cos(angle + pi / 2),
                src_pos[1] + arrow_size * sin(angle + pi / 2),
            ),
            (
                src_pos[0] + arrow_size * cos(angle - pi / 2),
                src_pos[1] + arrow_size * sin(angle - pi / 2),
            ),
        ]
        ctx.move_to(*dest_pos)
        ctx.line_to(*aux_points[0])
        ctx.line_to(*aux_points[1])
        ctx.line_to(*dest_pos)
        ctx.fill()


class AlphaVaryingEdgeDrawer(AbstractCairoEdgeDrawer):
    """Edge drawer implementation that draws undirected edges as
    straight lines and directed edges by varying the alpha value
    of the specified edge color between the source and the destination.
    """

    def __init__(self, context, palette, alpha_at_src, alpha_at_dest):
        super().__init__(context, palette)
        self.alpha_at_src = (clamp(float(alpha_at_src), 0.0, 1.0),)
        self.alpha_at_dest = (clamp(float(alpha_at_dest), 0.0, 1.0),)

    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        if src_vertex == dest_vertex:  # TODO
            return self.draw_loop_edge(edge, src_vertex)

        src_pos, dest_pos = src_vertex.position, dest_vertex.position
        ctx = self.context

        # Set up the gradient
        lg = cairo.LinearGradient(src_pos[0], src_pos[1], dest_pos[0], dest_pos[1])
        edge_color = edge.color[:3] + self.alpha_at_src
        edge_color_end = edge_color[:3] + self.alpha_at_dest
        lg.add_color_stop_rgba(0, *edge_color)
        lg.add_color_stop_rgba(1, *edge_color_end)

        # Draw the edge
        ctx.set_source(lg)
        ctx.set_line_width(edge.width)
        ctx.move_to(*src_pos)
        ctx.line_to(*dest_pos)
        ctx.stroke()


class LightToDarkEdgeDrawer(AlphaVaryingEdgeDrawer):
    """Edge drawer implementation that draws undirected edges as
    straight lines and directed edges by using an alpha value of
    zero (total transparency) at the source and an alpha value of
    one (full opacity) at the destination. The alpha value is
    interpolated in-between.
    """

    def __init__(self, context, palette):
        super().__init__(context, palette, 0.0, 1.0)


class DarkToLightEdgeDrawer(AlphaVaryingEdgeDrawer):
    """Edge drawer implementation that draws undirected edges as
    straight lines and directed edges by using an alpha value of
    one (full opacity) at the source and an alpha value of zero
    (total transparency) at the destination. The alpha value is
    interpolated in-between.
    """

    def __init__(self, context, palette):
        super().__init__(context, palette, 1.0, 0.0)
