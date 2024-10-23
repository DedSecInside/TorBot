"""
Drawing routines to draw graphs.

This module contains routines to draw graphs on:

  - Cairo surfaces (L{DefaultGraphDrawer})
  - Matplotlib axes (L{MatplotlibGraphDrawer})

It also contains routines to send an igraph graph directly to
(U{Cytoscape<http://www.cytoscape.org>}) using the
(U{CytoscapeRPC plugin<http://gforge.nbic.nl/projects/cytoscaperpc/>}), see
L{CytoscapeGraphDrawer}. L{CytoscapeGraphDrawer} can also fetch the current
network from Cytoscape and convert it to igraph format.
"""

from warnings import warn

from igraph.drawing.baseclasses import AbstractGraphDrawer, AbstractXMLRPCDrawer

__all__ = ("CytoscapeGraphDrawer", "__plot__")


class CytoscapeGraphDrawer(AbstractXMLRPCDrawer, AbstractGraphDrawer):
    """Graph drawer that sends/receives graphs to/from Cytoscape using
    CytoscapeRPC.

    This graph drawer cooperates with U{Cytoscape<http://www.cytoscape.org>}
    using U{CytoscapeRPC<http://wiki.nbic.nl/index.php/CytoscapeRPC>}.
    You need to install the CytoscapeRPC plugin first and start the
    XML-RPC server on a given port (port 9000 by default) from the
    appropriate Plugins submenu in Cytoscape.

    Graph, vertex and edge attributes are transferred to Cytoscape whenever
    possible (i.e. when a suitable mapping exists between a Python type
    and a Cytoscape type). If there is no suitable Cytoscape type for a
    Python type, the drawer will use a string attribute on the Cytoscape
    side and invoke C{str()} on the Python attributes.

    If an attribute to be created on the Cytoscape side already exists with
    a different type, an underscore will be appended to the attribute name
    to resolve the type conflict.

    You can use the C{network_id} attribute of this class to figure out the
    network ID of the last graph drawn with this drawer.
    """

    def __init__(self, url="http://localhost:9000/Cytoscape"):
        """Constructs a Cytoscape graph drawer using the XML-RPC interface
        of Cytoscape at the given URL."""
        super().__init__(url, "Cytoscape")
        self.network_id = None

    def draw(self, graph, name="Network from igraph", create_view=True, *args, **kwds):
        """Sends the given graph to Cytoscape as a new network.

        @param name: the name of the network in Cytoscape.
        @param create_view: whether to create a view for the network
          in Cytoscape.The default is C{True}.
        @keyword node_ids: specifies the identifiers of the nodes to
          be used in Cytoscape. This must either be the name of a
          vertex attribute or a list specifying the identifiers, one
          for each node in the graph. The default is C{None}, which
          simply uses the vertex index for each vertex."""
        from xmlrpc.client import Fault

        # Positional arguments are not used
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        cy = self.service

        # Create the network
        if not create_view:
            try:
                network_id = cy.createNetwork(name, False)
            except Fault:
                warn(
                    "CytoscapeRPC too old, cannot create network without view."
                    " Consider upgrading CytoscapeRPC to use this feature."
                )
                network_id = cy.createNetwork(name)
        else:
            network_id = cy.createNetwork(name)
        self.network_id = network_id

        # Create the nodes
        if "node_ids" in kwds:
            node_ids = kwds["node_ids"]
            if isinstance(node_ids, str):
                node_ids = graph.vs[node_ids]
        else:
            node_ids = list(range(graph.vcount()))
        node_ids = [str(identifier) for identifier in node_ids]
        cy.createNodes(network_id, node_ids)

        # Create the edges
        edgelists = [[], []]
        for v1, v2 in graph.get_edgelist():
            edgelists[0].append(node_ids[v1])
            edgelists[1].append(node_ids[v2])
        edge_ids = cy.createEdges(
            network_id,
            edgelists[0],
            edgelists[1],
            ["unknown"] * graph.ecount(),
            [graph.is_directed()] * graph.ecount(),
            False,
        )

        if "layout" in kwds:
            # Calculate/get the layout of the graph
            layout = self.ensure_layout(kwds["layout"], graph)
            size = 100 * graph.vcount() ** 0.5
            layout.fit_into((size, size), keep_aspect_ratio=True)
            layout.translate(-size / 2.0, -size / 2.0)
            cy.setNodesPositions(network_id, node_ids, *list(zip(*list(layout))))
        else:
            # Ask Cytoscape to perform the default layout so the user can
            # at least see something in Cytoscape while the attributes are
            # being transferred
            cy.performDefaultLayout(network_id)

        # Send the network attributes
        attr_names = set(cy.getNetworkAttributeNames())
        for attr in graph.attributes():
            cy_type, value = self.infer_cytoscape_type([graph[attr]])
            value = value[0]
            if value is None:
                continue

            # Resolve type conflicts (if any)
            try:
                while (
                    attr in attr_names and cy.getNetworkAttributeType(attr) != cy_type
                ):
                    attr += "_"
            except Fault:
                # getNetworkAttributeType is not available in some older versions
                # so we simply pass here
                pass
            cy.addNetworkAttributes(attr, cy_type, {network_id: value})

        # Send the node attributes
        attr_names = set(cy.getNodeAttributeNames())
        for attr in graph.vertex_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.vs[attr])
            values = dict(pair for pair in zip(node_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getNodeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addNodeAttributes(attr, cy_type, values, True)

        # Send the edge attributes
        attr_names = set(cy.getEdgeAttributeNames())
        for attr in graph.edge_attributes():
            cy_type, values = self.infer_cytoscape_type(graph.es[attr])
            values = dict(pair for pair in zip(edge_ids, values) if pair[1] is not None)
            # Resolve type conflicts (if any)
            while attr in attr_names and cy.getEdgeAttributeType(attr) != cy_type:
                attr += "_"
            # Send the attribute values
            cy.addEdgeAttributes(attr, cy_type, values)

    def fetch(self, name=None, directed=False, keep_canonical_names=False):
        """Fetches the network with the given name from Cytoscape.

        When fetching networks from Cytoscape, the C{canonicalName} attributes
        of vertices and edges are not converted by default. Use the
        C{keep_canonical_names} parameter to retrieve these attributes as well.

        @param name: the name of the network in Cytoscape.
        @param directed: whether the network is directed.
        @param keep_canonical_names: whether to keep the C{canonicalName}
            vertex/edge attributes that are added automatically by Cytoscape
        @return: an appropriately constructed igraph L{Graph}."""
        from igraph import Graph

        cy = self.service

        # Check the version number. Anything older than 1.3 is bad.
        version = cy.version()
        if " " in version:
            version = version.split(" ")[0]
        version = tuple(map(int, version.split(".")[:2]))
        if version < (1, 3):
            raise NotImplementedError(
                "CytoscapeGraphDrawer requires Cytoscape-RPC 1.3 or newer"
            )

        # Find out the ID of the network we are interested in
        if name is None:
            network_id = cy.getNetworkID()
        else:
            network_id = [k for k, v in cy.getNetworkList().items() if v == name]
            if not network_id:
                raise ValueError("no such network: %r" % name)
            elif len(network_id) > 1:
                raise ValueError("more than one network exists with name: %r" % name)
            network_id = network_id[0]

        # Fetch the list of all the nodes and edges
        vertices = cy.getNodes(network_id)
        edges = cy.getEdges(network_id)
        n, m = len(vertices), len(edges)

        # Fetch the graph attributes
        graph_attrs = cy.getNetworkAttributes(network_id)

        # Fetch the vertex attributes
        vertex_attr_names = cy.getNodeAttributeNames()
        vertex_attrs = {}
        for attr_name in vertex_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.nodesHaveAttribute(attr_name, vertices)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getNodesAttributes(
                attr_name, [name for name, ok in zip(vertices, has_attr) if ok]
            )
            attrs = [None] * n
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            vertex_attrs[attr_name] = attrs

        # Fetch the edge attributes
        edge_attr_names = cy.getEdgeAttributeNames()
        edge_attrs = {}
        for attr_name in edge_attr_names:
            if attr_name == "canonicalName" and not keep_canonical_names:
                continue
            has_attr = cy.edgesHaveAttribute(attr_name, edges)
            filtered = [idx for idx, ok in enumerate(has_attr) if ok]
            values = cy.getEdgesAttributes(
                attr_name, [name for name, ok in zip(edges, has_attr) if ok]
            )
            attrs = [None] * m
            for idx, value in zip(filtered, values):
                attrs[idx] = value
            edge_attrs[attr_name] = attrs

        # Create a vertex name index
        vertex_name_index = dict((v, k) for k, v in enumerate(vertices))
        del vertices

        # Remap the edges list to numeric IDs
        edge_list = []
        for edge in edges:
            parts = edge.split()
            edge_list.append((vertex_name_index[parts[0]], vertex_name_index[parts[2]]))
        del edges

        return Graph(
            n,
            edge_list,
            directed=directed,
            graph_attrs=graph_attrs,
            vertex_attrs=vertex_attrs,
            edge_attrs=edge_attrs,
        )

    @staticmethod
    def infer_cytoscape_type(values):
        """Returns a Cytoscape type that can be used to represent all the
        values in C{values} and an appropriately converted copy of C{values} that
        is suitable for an XML-RPC call.  Note that the string type in
        Cytoscape is used as a catch-all type; if no other type fits, attribute
        values will be converted to string and then posted to Cytoscape.

        C{None} entries are allowed in C{values}, they will be ignored on the
        Cytoscape side.
        """
        types = [type(value) for value in values if value is not None]
        if all(t == bool for t in types):
            return "BOOLEAN", values
        if all(issubclass(t, (int, int)) for t in types):
            return "INTEGER", values
        if all(issubclass(t, float) for t in types):
            return "FLOATING", values
        return "STRING", [
            str(value) if not isinstance(value, str) else value for value in values
        ]


#####################################################################


class GephiGraphStreamingDrawer(AbstractGraphDrawer):
    """Graph drawer that sends a graph to a file-like object (e.g., socket, URL
    connection, file) using the Gephi graph streaming format.

    The Gephi graph streaming format is a simple JSON-based format that can be used
    to post mutations to a graph (i.e. node and edge additions, removals and updates)
    to a remote component. For instance, one can open up Gephi
    (U{http://www.gephi.org}), install the Gephi graph streaming plugin and then
    send a graph from igraph straight into the Gephi window by using
    C{GephiGraphStreamingDrawer} with the appropriate URL where Gephi is
    listening.

    The C{connection} property exposes the L{GephiConnection} that the drawer
    uses. The drawer also has a property called C{streamer} which exposes the underlying
    L{GephiGraphStreamer} that is responsible for generating the JSON objects,
    encoding them and writing them to a file-like object. If you want to customize
    the encoding process, this is the object where you can tweak things to your taste.
    """

    def __init__(self, conn=None, *args, **kwds):
        """Constructs a Gephi graph streaming drawer that will post graphs to the
        given Gephi connection. If C{conn} is C{None}, the remaining arguments of
        the constructor are forwarded intact to the constructor of
        L{GephiConnection} in order to create a connection. This means that any of
        the following are valid:

          - C{GephiGraphStreamingDrawer()} will construct a drawer that connects to
            workspace 0 of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(workspace=2)} will connect to workspace 2
            of the local Gephi instance on port 8080.

          - C{GephiGraphStreamingDrawer(port=1234)} will connect to workspace 0
            of the local Gephi instance on port 1234.

          - C{GephiGraphStreamingDrawer(host="remote", port=1234, workspace=7)}
            will connect to workspace 7 of the Gephi instance on host C{remote},
            port 1234.

          - C{GephiGraphStreamingDrawer(url="http://remote:1234/workspace7)} is
            the same as above, but with an explicit URL.
        """
        super().__init__()

        from igraph.remote.gephi import GephiGraphStreamer, GephiConnection

        self.connection = conn or GephiConnection(*args, **kwds)
        self.streamer = GephiGraphStreamer()

    def draw(self, graph, *args, **kwds):
        """Draws (i.e. sends) the given graph to the destination of the drawer using
        the Gephi graph streaming API.

        The following keyword arguments are allowed:

            - C{encoder} lets one specify an instance of C{json.JSONEncoder} that
              will be used to encode the JSON objects.
        """
        # Positional arguments are not used
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        self.streamer.post(graph, self.connection, encoder=kwds.get("encoder"))


def __plot__(self, backend, context, *args, **kwds):
    """Plots the graph to the given Cairo context or matplotlib Axes.

    The visual style of vertices and edges can be modified at three
    places in the following order of precedence (lower indices override
    higher indices):

      1. Keyword arguments of this function (or of L{plot()} which is
         passed intact to C{Graph.__plot__()}.

      2. Vertex or edge attributes, specified later in the list of
         keyword arguments.

      3. igraph-wide plotting defaults (see
         L{igraph.config.Configuration})

      4. Built-in defaults.

    E.g., if the C{vertex_size} keyword attribute is not present,
    but there exists a vertex attribute named C{size}, the sizes of
    the vertices will be specified by that attribute.

    Besides the usual self-explanatory plotting parameters (C{context},
    C{bbox}, C{palette}), it accepts the following keyword arguments:

      - C{autocurve}: whether to use curves instead of straight lines for
        multiple edges on the graph plot. This argument may be C{True}
        or C{False}; when omitted, C{True} is assumed for graphs with
        less than 10.000 edges and C{False} otherwise.

      - C{drawer_factory}: a subclass of L{AbstractCairoGraphDrawer}
        which will be used to draw the graph. You may also provide
        a function here which takes two arguments: the Cairo context
        to draw on and a bounding box (an instance of L{BoundingBox}).
        If this keyword argument is missing, igraph will use the
        default graph drawer which should be suitable for most purposes.
        It is safe to omit this keyword argument unless you need to use
        a specific graph drawer.

      - C{keep_aspect_ratio}: whether to keep the aspect ratio of the layout
        that igraph calculates to place the nodes. C{True} means that the
        layout will be scaled proportionally to fit into the bounding box
        where the graph is to be drawn but the aspect ratio will be kept
        the same (potentially leaving empty space next to, below or above
        the graph). C{False} means that the layout will be scaled independently
        along the X and Y axis in order to fill the entire bounding box.
        The default is C{False}.

      - C{layout}: the layout to be used. If not an instance of
        L{Layout}, it will be passed to L{layout} to calculate
        the layout. Note that if you want a deterministic layout that
        does not change with every plot, you must either use a
        deterministic layout function (like L{GraphBase.layout_circle}) or
        calculate the layout in advance and pass a L{Layout} object here.

      - C{margin}: the top, right, bottom, left margins as a 4-tuple.
        If it has less than 4 elements or is a single float, the elements
        will be re-used until the length is at least 4.

      - C{mark_groups}: whether to highlight some of the vertex groups by
        colored polygons. This argument can be one of the following:

          - C{False}: no groups will be highlighted

          - C{True}: only valid if the object plotted is a
            L{VertexClustering} or L{VertexCover}. The vertex groups in the
            clutering or cover will be highlighted such that the i-th
            group will be colored by the i-th color from the current
            palette. If used when plotting a graph, it will throw an error.

          - A dict mapping tuples of vertex indices to color names.
            The given vertex groups will be highlighted by the given
            colors.

          - A list containing pairs or an iterable yielding pairs, where
            the first element of each pair is a list of vertex indices and
            the second element is a color.

          - A L{VertexClustering} or L{VertexCover} instance. The vertex
            groups in the clustering or cover will be highlighted such that
            the i-th group will be colored by the i-th color from the
            current palette.

        In place of lists of vertex indices, you may also use L{VertexSeq}
        instances.

        In place of color names, you may also use color indices into the
        current palette. C{None} as a color name will mean that the
        corresponding group is ignored.

      - C{vertex_size}: size of the vertices. The corresponding vertex
        attribute is called C{size}. The default is 10. Vertex sizes
        are measured in the unit of the Cairo context on which igraph
        is drawing.

      - C{vertex_color}: color of the vertices. The corresponding vertex
        attribute is C{color}, the default is red.  Colors can be
        specified either by common X11 color names (see the source
        code of L{igraph.drawing.colors} for a list of known colors), by
        3-tuples of floats (ranging between 0 and 255 for the R, G and
        B components), by CSS-style string specifications (C{#rrggbb})
        or by integer color indices of the specified palette.

      - C{vertex_frame_color}: color of the frame (i.e. stroke) of the
        vertices. The corresponding vertex attribute is C{frame_color},
        the default is black. See C{vertex_color} for the possible ways
        of specifying a color.

      - C{vertex_frame_width}: the width of the frame (i.e. stroke) of the
        vertices. The corresponding vertex attribute is C{frame_width}.
        The default is 1. Vertex frame widths are measured in the unit of the
        Cairo context on which igraph is drawing.

      - C{vertex_shape}: shape of the vertices. Alternatively it can
        be specified by the C{shape} vertex attribute. Possibilities
        are: C{square}, {circle}, {triangle}, {triangle-down} or
        C{hidden}. See the source code of L{igraph.drawing} for a
        list of alternative shape names that are also accepted and
        mapped to these.

      - C{vertex_label}: labels drawn next to the vertices.
        The corresponding vertex attribute is C{label}.

      - C{vertex_label_dist}: distance of the midpoint of the vertex
        label from the center of the corresponding vertex.
        The corresponding vertex attribute is C{label_dist}.

      - C{vertex_label_color}: color of the label. Corresponding
        vertex attribute: C{label_color}. See C{vertex_color} for
        color specification syntax.

      - C{vertex_label_size}: font size of the label, specified
        in the unit of the Cairo context on which we are drawing.
        Corresponding vertex attribute: C{label_size}.

      - C{vertex_label_angle}: the direction of the line connecting
        the midpoint of the vertex with the midpoint of the label.
        This can be used to position the labels relative to the
        vertices themselves in conjunction with C{vertex_label_dist}.
        Corresponding vertex attribute: C{label_angle}. The
        default is C{-math.pi/2}.

      - C{vertex_order}: drawing order of the vertices. This must be
        a list or tuple containing vertex indices; vertices are then
        drawn according to this order.

      - C{vertex_order_by}: an alternative way to specify the drawing
        order of the vertices; this attribute is interpreted as the name
        of a vertex attribute, and vertices are drawn such that those
        with a smaller attribute value are drawn first. You may also
        reverse the order by passing a tuple here; the first element of
        the tuple should be the name of the attribute, the second element
        specifies whether the order is reversed (C{True}, C{False},
        C{"asc"} and C{"desc"} are accepted values).

      - C{edge_color}: color of the edges. The corresponding edge
        attribute is C{color}, the default is red. See C{vertex_color}
        for color specification syntax.

      - C{edge_curved}: whether the edges should be curved. Positive
        numbers correspond to edges curved in a counter-clockwise
        direction, negative numbers correspond to edges curved in a
        clockwise direction. Zero represents straight edges. C{True}
        is interpreted as 0.5, C{False} is interpreted as 0. The
        default is 0 which makes all the edges straight.

      - C{edge_width}: width of the edges in the default unit of the
        Cairo context on which we are drawing. The corresponding
        edge attribute is C{width}, the default is 1.

      - C{edge_arrow_size}: arrow size of the edges. The
        corresponding edge attribute is C{arrow_size}, the default
        is 1.

      - C{edge_arrow_width}: width of the arrowhead on the edge. The
        corresponding edge attribute is C{arrow_width}, the default
        is 1.

      - C{edge_order}: drawing order of the edges. This must be
        a list or tuple containing edge indices; edges are then
        drawn according to this order.

      - C{edge_order_by}: an alternative way to specify the drawing
        order of the edges; this attribute is interpreted as the name
        of an edge attribute, and edges are drawn such that those
        with a smaller attribute value are drawn first. You may also
        reverse the order by passing a tuple here; the first element of
        the tuple should be the name of the attribute, the second element
        specifies whether the order is reversed (C{True}, C{False},
        C{"asc"} and C{"desc"} are accepted values).
    """
    from igraph.drawing import DrawerDirectory

    drawer = kwds.pop(
        "drawer_factory",
        DrawerDirectory.resolve(self, backend)(context),
    )
    return drawer.draw(self, *args, **kwds)
