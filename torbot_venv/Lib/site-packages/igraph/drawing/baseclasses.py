"""
Abstract base classes for the drawing routines.
"""

from abc import ABCMeta, abstractmethod
from math import atan2, pi

from .text import TextAlignment
from .utils import get_bezier_control_points_for_curved_edge, evaluate_cubic_bezier

#####################################################################


class AbstractDrawer(metaclass=ABCMeta):
    """Abstract class that serves as a base class for anything that
    draws an igraph object."""

    @abstractmethod
    def draw(self, *args, **kwds):
        """Abstract method, must be implemented in derived classes."""
        raise NotImplementedError


#####################################################################


class AbstractXMLRPCDrawer(AbstractDrawer):
    """Abstract drawer that uses a remote service via XML-RPC
    to draw something on a remote display.
    """

    def __init__(self, url, service=None):
        """Constructs an abstract drawer using the XML-RPC service
        at the given URL.

        @param url: the URL where the XML-RPC calls for the service should
          be addressed to.
        @param service: the name of the service at the XML-RPC address. If
          C{None}, requests will be directed to the server proxy object
          constructed by C{xmlrpclib.ServerProxy}; if not C{None}, the
          given attribute will be looked up in the server proxy object.
        """
        import xmlrpc.client

        url = self._resolve_hostname(url)
        self.server = xmlrpc.client.ServerProxy(url)
        if service is None:
            self.service = self.server
        else:
            self.service = getattr(self.server, service)

    @staticmethod
    def _resolve_hostname(url):
        """Parses the given URL, resolves the hostname to an IP address
        and returns a new URL with the resolved IP address. This speeds
        up things big time on Mac OS X where an IP lookup would be
        performed for every XML-RPC call otherwise."""
        from urllib.parse import urlparse, urlunparse
        import re

        url_parts = urlparse(url)
        hostname = url_parts.netloc
        if re.match("[0-9.:]+$", hostname):
            # the hostname is already an IP address, possibly with a port
            return url

        from socket import gethostbyname

        if ":" in hostname:
            hostname = hostname[0 : hostname.index(":")]
        hostname = gethostbyname(hostname)
        if url_parts.port is not None:
            hostname = "%s:%d" % (hostname, url_parts.port)
        url_parts = list(url_parts)
        url_parts[1] = hostname
        return urlunparse(url_parts)


#####################################################################


class AbstractEdgeDrawer(metaclass=ABCMeta):
    """Abstract edge drawer object from which all concrete edge drawer
    implementations are derived.
    """

    @staticmethod
    def _curvature_to_float(value):
        """Converts values given to the 'curved' edge style argument
        in plotting calls to floating point values."""
        if value is None or value is False:
            return 0.0
        if value is True:
            return 0.5
        return float(value)

    @abstractmethod
    def draw_directed_edge(self, edge, src_vertex, dest_vertex):
        """Draws a directed edge.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        @param dest_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_undirected_edge(self, edge, src_vertex, dest_vertex):
        """Draws an undirected edge.

        @param edge: the edge to be drawn. Visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        @param dest_vertex: the source vertex. Visual properties are defined
          by the attributes of this object.
        """
        raise NotImplementedError

    def get_label_position(self, edge, src_vertex, dest_vertex):
        """Returns the position where the label of an edge should be drawn. the
        default implementation returns the midpoint of the edge and an alignment
        that tries to avoid overlapping the label with the edge.

        @param edge: the edge to be drawn. visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. visual properties are given
          again as attributes.
        @param dest_vertex: the target vertex. visual properties are given
          again as attributes.
        @return: a tuple containing two more tuples: the desired position of the
          label and the desired alignment of the label, where the position is
          given as c{(x, y)} and the alignment is given as c{(horizontal, vertical)}.
          members of the alignment tuple are taken from constants in the
          l{textalignment} class.
        """
        # TODO: curved edges don't play terribly well with this function,
        # we could try to get the mid point of the actual curved arrow
        # (Bezier curve) and use that.

        # Determine the angle of the line
        dx = dest_vertex.position[0] - src_vertex.position[0]
        dy = dest_vertex.position[1] - src_vertex.position[1]
        if dx != 0 or dy != 0:
            # Note that we use -dy because the Y axis points downwards
            angle = atan2(-dy, dx) % (2 * pi)
        else:
            angle = None

        # Determine the midpoint
        if edge.curved:
            (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
            aux1, aux2 = get_bezier_control_points_for_curved_edge(
                    x1, y1, x2, y2, edge.curved,
                )
            pos = evaluate_cubic_bezier(x1, y1, *aux1, *aux2, x2, y2, 0.5)
        else:
            pos = (
                (src_vertex.position[0] + dest_vertex.position[0]) / 2.0,
                (src_vertex.position[1] + dest_vertex.position[1]) / 2.0,
            )

        # Determine the alignment based on the angle
        pi4 = pi / 4
        if angle is None:
            halign, valign = TextAlignment.CENTER, TextAlignment.CENTER
        else:
            index = int((angle / pi4) % 8)
            halign = [
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.RIGHT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
                TextAlignment.LEFT,
            ][index]
            valign = [
                TextAlignment.BOTTOM,
                TextAlignment.CENTER,
                TextAlignment.CENTER,
                TextAlignment.TOP,
                TextAlignment.TOP,
                TextAlignment.CENTER,
                TextAlignment.CENTER,
                TextAlignment.BOTTOM,
            ][index]

        return pos, (halign, valign)

    def get_label_rotation(self, edge, src_vertex, dest_vertex):
        """Get the rotation angle of the label to align with the edge.

        @param edge: the edge to be drawn. visual properties of the edge
          are defined by the attributes of this object.
        @param src_vertex: the source vertex. visual properties are given
          again as attributes.
        @param dest_vertex: the target vertex. visual properties are given
          again as attributes.
        @return: a float with the desired angle, in degrees (out of 360).
        """
        (x1, y1), (x2, y2) = src_vertex.position, dest_vertex.position
        rotation = (360 + 180. / pi * atan2(y2 - y1, x2 - x1)) % 360
        # Try to keep text on its head
        if 90 < rotation <= 270:
            rotation = (180 + rotation) % 360
        return rotation

#####################################################################


class AbstractVertexDrawer(AbstractDrawer):
    """Abstract vertex drawer object from which all concrete vertex drawer
    implementations are derived."""

    def __init__(self, palette, layout):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        @param layout:  the layout of the vertices in the graph being drawn
        """
        self.layout = layout
        self.palette = palette

    @abstractmethod
    def draw(self, visual_vertex, vertex, coords):
        """Draws the given vertex.

        @param visual_vertex: object specifying the visual properties of the
            vertex. Its structure is defined by the VisualVertexBuilder of the
            L{CairoGraphDrawer}; see its source code.
        @param vertex: the raw igraph vertex being drawn
        @param coords: the X and Y coordinates of the vertex as specified by the
            layout algorithm, scaled into the bounding box.
        """
        raise NotImplementedError


#####################################################################


class AbstractGraphDrawer(AbstractDrawer):
    """Abstract class that serves as a base class for anything that
    draws an igraph.Graph.
    """

    @abstractmethod
    def draw(self, graph, *args, **kwds):
        """Abstract method, must be implemented in derived classes."""
        raise NotImplementedError

    @staticmethod
    def ensure_layout(layout, graph=None):
        """Helper method that ensures that I{layout} is an instance
        of L{Layout}. If it is not, the method will try to convert
        it to a L{Layout} according to the following rules:

          - If I{layout} is a string, it is assumed to be a name
            of an igraph layout, and it will be passed on to the
            C{layout} method of the given I{graph} if I{graph} is
            not C{None}.

          - If I{layout} is C{None} and I{graph} has a "layout"
            attribute, call this same function with the value of that
            attribute.

          - If I{layout} is C{None} and I{graph} does not have a "layout"
            attribute, the C{layout} method of I{graph} will be invoked
            with no parameters, which will call the default layout algorithm.

          - Otherwise, I{layout} will be passed on to the constructor
            of L{Layout}. This handles lists of lists, lists of tuples
            and such.

        If I{layout} is already a L{Layout} instance, it will still
        be copied and a copy will be returned. This is because graph
        drawers are allowed to transform the layout for their purposes,
        and we don't want the transformation to propagate back to the
        caller.
        """
        from igraph.layout import Layout  # avoid circular imports

        if isinstance(layout, Layout):
            layout = Layout(layout.coords)
        elif isinstance(layout, str):
            layout = graph.layout(layout)
        elif (layout is None) and hasattr(graph, "attributes") and \
                ('layout' in graph.attributes()):
            layout = AbstractGraphDrawer.ensure_layout(graph['layout'], graph=graph)
        elif layout is None:
            layout = graph.layout(layout)
        else:
            layout = Layout(layout)

        return layout

    @staticmethod
    def _determine_edge_order(graph, kwds):
        """Returns the order in which the edge of the given graph have to be
        drawn, assuming that the relevant keyword arguments (C{edge_order} and
        C{edge_order_by}) are given in C{kwds} as a dictionary. If neither
        C{edge_order} nor C{edge_order_by} is present in C{kwds}, this
        function returns C{None} to indicate that the graph drawer is free to
        choose the most convenient edge ordering."""
        if "edge_order" in kwds:
            # Edge order specified explicitly
            return kwds["edge_order"]

        if kwds.get("edge_order_by") is None:
            # No edge order specified
            return None

        # Order edges by the value of some attribute
        edge_order_by = kwds["edge_order_by"]
        reverse = False
        if isinstance(edge_order_by, tuple):
            edge_order_by, reverse = edge_order_by
            if isinstance(reverse, str):
                reverse = reverse.lower().startswith("desc")
        attrs = graph.es[edge_order_by]
        edge_order = sorted(
            list(range(len(attrs))), key=attrs.__getitem__, reverse=bool(reverse)
        )

        return edge_order

    @staticmethod
    def _determine_vertex_order(graph, kwds):
        """Returns the order in which the vertices of the given graph have to be
        drawn, assuming that the relevant keyword arguments (C{vertex_order} and
        C{vertex_order_by}) are given in C{kwds} as a dictionary. If neither
        C{vertex_order} nor C{vertex_order_by} is present in C{kwds}, this
        function returns C{None} to indicate that the graph drawer is free to
        choose the most convenient vertex ordering."""
        if "vertex_order" in kwds:
            # Vertex order specified explicitly
            return kwds["vertex_order"]

        if kwds.get("vertex_order_by") is None:
            # No vertex order specified
            return None

        # Order vertices by the value of some attribute
        vertex_order_by = kwds["vertex_order_by"]
        reverse = False
        if isinstance(vertex_order_by, tuple):
            vertex_order_by, reverse = vertex_order_by
            if isinstance(reverse, str):
                reverse = reverse.lower().startswith("desc")
        attrs = graph.vs[vertex_order_by]
        vertex_order = sorted(
            list(range(len(attrs))), key=attrs.__getitem__, reverse=bool(reverse)
        )

        return vertex_order
