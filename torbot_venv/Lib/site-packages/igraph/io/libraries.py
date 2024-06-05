def _export_graph_to_networkx(
    graph, create_using=None, vertex_attr_hashable: str = "_nx_name",
):
    """Converts the graph to networkx format.

    igraph has ordered vertices and edges, but networkx does not. To keep
    track of the original order, the '_igraph_index' vertex property is
    added to both vertices and edges.

    @param create_using: specifies which NetworkX graph class to use when
        constructing the graph. C{None} means to let igraph infer the most
        appropriate class based on whether the graph is directed and whether
        it has multi-edges.
    @param vertex_attr_hashable: vertex attribute used to name vertices
        in the exported network. The default "_nx_name" ensures round trip
        conversions to/from networkx are lossless.
    """
    import networkx as nx

    # Graph: decide on directness and mutliplicity
    if create_using is None:
        if graph.has_multiple():
            cls = nx.MultiDiGraph if graph.is_directed() else nx.MultiGraph
        else:
            cls = nx.DiGraph if graph.is_directed() else nx.Graph
    else:
        cls = create_using

    # Graph attributes
    kw = {x: graph[x] for x in graph.attributes()}
    g = cls(**kw)

    multigraph = isinstance(g, (nx.MultiGraph, nx.MultiDiGraph))

    # Nodes and node attributes
    for i, v in enumerate(graph.vs):
        vattr = v.attributes()
        vattr["_igraph_index"] = i

        # use _nx_name if the attribute is present so we can achieve
        # a lossless round-trip in terms of vertex names
        if vertex_attr_hashable in vattr:
            hashable = vattr.pop(vertex_attr_hashable)
        else:
            hashable = i

        # adding nodes one at a time is not slower in networkx
        g.add_node(hashable, **vattr)

    # Edges and edge attributes
    for i, edge in enumerate(graph.es):
        eattr = edge.attributes()
        eattr["_igraph_index"] = i

        if multigraph and "_nx_multiedge_key" in eattr:
            eattr["key"] = eattr.pop["_nx_multiedge_key"]

        if vertex_attr_hashable in graph.vertex_attributes():
            hashable_source = graph.vs[vertex_attr_hashable][edge.source]
            hashable_target = graph.vs[vertex_attr_hashable][edge.target]
        else:
            hashable_source = edge.source
            hashable_target = edge.target

        # adding edges one at a time is not slower in networkx
        g.add_edge(hashable_source, hashable_target, **eattr)

    return g


def _construct_graph_from_networkx(cls, g, vertex_attr_hashable : str = "_nx_name"):
    """Converts the graph from networkx

    Vertex names will be stored as a vertex_attr_hashable attribute (usually
    "_nx_name", but see below). Because igraph stored vertices in an
    ordered manner, vertices will get new IDs from 0 up. In case of
    multigraphs, each edge will have an "_nx_multiedge_key" attribute, to
    distinguish edges that connect the same two vertices.

    @param g: networkx Graph or DiGraph
    @param vertex_attr_hashable: attribute used to store the Python
        hashable used by networkx to identify each vertex. The default value
        '_nx_name' ensures lossless round trip conversions to/from networkx. An
        alternative choice is 'name': in that case, using strings for vertex
        names is recommended and, if the graph is re-exported to networkx,
        Graph.to_networkx(vertex_attr_hashable="name") must be used to recover
        the correct vertex nomenclature in the exported network.

    """
    import networkx as nx

    # Graph attributes
    gattr = dict(g.graph)

    # Nodes
    vnames = list(g.nodes)
    vattr = {vertex_attr_hashable: vnames}
    vcount = len(vnames)

    # Dictionary connecting networkx hashables with igraph indices
    if len(g) and "_igraph_index" in next(iter(g.nodes.values())):
        # Collect _igraph_index and fill gaps
        idx = [x["_igraph_index"] for v, x in g.nodes.data()]
        idx.sort()
        idx_dict = {x: i for i, x in enumerate(idx)}

        vd = {}
        for v, datum in g.nodes.data():
            vd[v] = idx_dict[datum["_igraph_index"]]
    else:
        vd = {v: i for i, v in enumerate(vnames)}

    # NOTE: we do not need a special class for multigraphs, it is taken
    # care for at the edge level rather than at the graph level.
    graph = cls(
        n=vcount, directed=g.is_directed(), graph_attrs=gattr, vertex_attrs=vattr
    )

    # Vertex attributes
    for v, datum in g.nodes.data():
        for key, val in datum.items():
            # Get rid of _igraph_index (we used it already)
            if key == "_igraph_index":
                continue
            graph.vs[vd[v]][key] = val

    # Edges and edge attributes
    eattr_names = {name for (_, _, data) in g.edges.data() for name in data}
    eattr = {name: [] for name in eattr_names}
    edges = []
    # Multigraphs need a hidden attribute for multiedges
    if isinstance(g, (nx.MultiGraph, nx.MultiDiGraph)):
        eattr["_nx_multiedge_key"] = []
        for (u, v, edgekey, data) in g.edges.data(keys=True):
            edges.append((vd[u], vd[v]))
            for name in eattr_names:
                eattr[name].append(data.get(name))
            eattr["_nx_multiedge_key"].append(edgekey)

    else:
        for (u, v, data) in g.edges.data():
            edges.append((vd[u], vd[v]))
            for name in eattr_names:
                eattr[name].append(data.get(name))

    # Sort edges if there is a trace of a previous igraph ordering
    if "_igraph_index" in eattr:
        # Poor man's argsort
        sortd = [(i, x) for i, x in enumerate(eattr["_igraph_index"])]
        sortd.sort(key=lambda x: x[1])
        idx = [i for i, x in sortd]

        # Get rid of the _igraph_index now
        del eattr["_igraph_index"]

        # Sort edges
        edges = [edges[i] for i in idx]
        # Sort each attribute
        eattr = {key: [val[i] for i in idx] for key, val in eattr.items()}

    graph.add_edges(edges, eattr)

    return graph


def _export_graph_to_graph_tool(
    graph, graph_attributes=None, vertex_attributes=None, edge_attributes=None
):
    """Converts the graph to graph-tool

    Data types: graph-tool only accepts specific data types. See the
    following web page for a list:

    https://graph-tool.skewed.de/static/doc/quickstart.html

    Note: because of the restricted data types in graph-tool, vertex and
    edge attributes require to be type-consistent across all vertices or
    edges. If you set the property for only some vertices/edges, the other
    will be tagged as None in igraph, so they can only be converted
    to graph-tool with the type 'object' and any other conversion will
    fail.

    @param graph_attributes: dictionary of graph attributes to transfer.
      Keys are attributes from the graph, values are data types (see
      below). C{None} means no graph attributes are transferred.
    @param vertex_attributes: dictionary of vertex attributes to transfer.
      Keys are attributes from the vertices, values are data types (see
      below). C{None} means no vertex attributes are transferred.
    @param edge_attributes: dictionary of edge attributes to transfer.
      Keys are attributes from the edges, values are data types (see
      below). C{None} means no vertex attributes are transferred.
    """
    import graph_tool as gt

    # Graph
    g = gt.Graph(directed=graph.is_directed())

    # Nodes
    vc = graph.vcount()
    g.add_vertex(vc)

    # Graph attributes
    if graph_attributes is not None:
        for x, dtype in graph_attributes.items():
            # Strange syntax for setting internal properties
            gprop = g.new_graph_property(str(dtype))
            g.graph_properties[x] = gprop
            g.graph_properties[x] = graph[x]

    # Vertex attributes
    if vertex_attributes is not None:
        for x, dtype in vertex_attributes.items():
            # Create a new vertex property
            g.vertex_properties[x] = g.new_vertex_property(str(dtype))
            # Fill the values from the igraph.Graph
            for i in range(vc):
                g.vertex_properties[x][g.vertex(i)] = graph.vs[i][x]

    # Edges and edge attributes
    if edge_attributes is not None:
        for x, dtype in edge_attributes.items():
            g.edge_properties[x] = g.new_edge_property(str(dtype))
    for edge in graph.es:
        e = g.add_edge(edge.source, edge.target)
        if edge_attributes is not None:
            for x, dtype in edge_attributes.items():
                prop = edge.attributes().get(x, None)
                g.edge_properties[x][e] = prop

    return g


def _construct_graph_from_graph_tool(cls, g):
    """Converts the graph from graph-tool

    @param g: graph-tool Graph
    """
    # Graph attributes
    gattr = dict(g.graph_properties)

    # Nodes
    vcount = g.num_vertices()

    # Graph
    graph = cls(n=vcount, directed=g.is_directed(), graph_attrs=gattr)

    # Node attributes
    for key, val in g.vertex_properties.items():
        prop = val.get_array()
        for i in range(vcount):
            graph.vs[i][key] = prop[i]

    # Edges and edge attributes
    # NOTE: graph-tool is quite strongly typed, so each property is always
    # defined for all edges, using default values for the type. E.g. for a
    # string property/attribute the missing edges get an empty string.
    edges = []
    eattr_names = list(g.edge_properties)
    eattr = {name: [] for name in eattr_names}
    for e in g.edges():
        edges.append((int(e.source()), int(e.target())))
        for name, attr_map in g.edge_properties.items():
            eattr[name].append(attr_map[e])

    graph.add_edges(edges, eattr)

    return graph
