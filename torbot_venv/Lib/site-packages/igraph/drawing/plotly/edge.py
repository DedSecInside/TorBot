"""Drawers for various edge styles in Matplotlib graph plots."""

from math import atan2, cos, pi, sin

from igraph.drawing.baseclasses import AbstractEdgeDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.plotly.utils import (
    find_plotly,
    format_path_step,
    format_arc,
    format_rgba,
)
from igraph.drawing.utils import (
    Point,
    euclidean_distance,
    get_bezier_control_points_for_curved_edge,
    intersect_bezier_curve_and_circle,
)

__all__ = ("PlotlyEdgeDrawer",)

plotly = find_plotly()


class PlotlyEdgeDrawer(AbstractEdgeDrawer):
    """Matplotlib-specific abstract edge drawer object."""

    def __init__(self, context, palette):
        """Constructs the edge drawer.

        @param context: a plotly Figure object on which the edges will be
            drawn.
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
            arrow_size = 0.007
            arrow_width = 1.4
            color = "#444"
            curved = (0.0, self._curvature_to_float)
            label = None
            label_color = ("black", self.palette.get)
            label_size = 12.0
            font = "sans-serif"
            width = 2.0

        return VisualEdgeBuilder

    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        if src_vertex == dest_vertex:  # TODO
            return self.draw_loop_edge(edge, src_vertex)

        fig = self.context
        (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
        (x_src, y_src), (x_dest, y_dest) = src_vertex.position, dest_vertex.position

        # Draw the edge
        path = [
            format_path_step("M", [x1, y1]),
        ]

        if edge.curved:
            # Calculate the curve
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x1, y1, x2, y2, edge.curved)

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
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x_src, y_src, x_arrow_mid, y_arrow_mid, edge.curved)

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
            path.append(format_path_step("C", [aux1, aux2, [x_arrow_mid, y_arrow_mid]]))

        else:
            # FIXME: this is tricky in plotly, let's skip for now
            ## Determine where the edge intersects the circumference of the
            ## vertex shape.
            # x2, y2 = dest_vertex.shape.intersection_point(
            #    x2, y2, x1, y1, dest_vertex.size
            # )

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
            path.append(
                format_path_step(
                    "L",
                    Point(x_arrow_mid, y_arrow_mid),
                )
            )

        path = " ".join(path)

        # Draw the edge
        stroke = dict(
            type="path",
            path=path,
            line_color=format_rgba(edge.color),
            line_width=edge.width,
        )
        fig.add_shape(stroke)

        # Draw the arrow head
        arrowhead = plotly.graph_objects.Scatter(
            x=[x2, aux_points[0][0], aux_points[1][0], x2],
            y=[y2, aux_points[0][1], aux_points[1][1], y2],
            fillcolor=format_rgba(edge.color),
            mode="lines",
        )
        fig.add_trace(arrowhead)

    def draw_loop_edge(self, edge, vertex):
        """Draws a loop edge.

        The default implementation draws a small circle.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param vertex: the vertex to which the edge is attached. Visual
          properties are given again as attributes.
        """
        fig = self.context
        radius = vertex.size * 1.5
        center_x = vertex.position[0] + cos(pi / 4) * radius / 2.0
        center_y = vertex.position[1] - sin(pi / 4) * radius / 2.0
        stroke = dict(
            type="path",
            path=format_arc(
                (center_x, center_y),
                radius / 2.0,
                radius / 2.0,
                theta1=0,
                theta2=360.0,
            ),
            line_color=edge.color,
            line_width=edge.width,
        )
        fig.add_shape(stroke)

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
        if src_vertex == dest_vertex:
            return self.draw_loop_edge(edge, src_vertex)

        fig = self.context

        path = [format_path_step("M", src_vertex.position)]

        if edge.curved:
            (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
            aux1, aux2 = get_bezier_control_points_for_curved_edge(x1, y1, x2, y2, edge.curved)

            path.append(
                format_path_step(
                    "C",
                    [aux1, aux2, dest_vertex.position],
                )
            )

        else:
            path.append(
                format_path_step(
                    "L",
                    dest_vertex.position,
                )
            )

        path = " ".join(path)

        stroke = dict(
            type="path",
            path=path,
            line_color=format_rgba(edge.color),
            line_width=edge.width,
        )
        fig.add_shape(stroke)
