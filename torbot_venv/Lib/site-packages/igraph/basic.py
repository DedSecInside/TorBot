from igraph._igraph import GraphBase
from igraph.seq import EdgeSeq
from igraph.utils import deprecated


def _add_edge(graph, source, target, **kwds):
    """Adds a single edge to the graph.

    Keyword arguments (except the source and target arguments) will be
    assigned to the edge as attributes.

    The performance cost of adding a single edge or several edges
    to a graph is similar. Thus, when adding several edges, a single
    C{add_edges()} call is more efficient than multiple C{add_edge()} calls.

    @param source: the source vertex of the edge or its name.
    @param target: the target vertex of the edge or its name.

    @return: the newly added edge as an L{Edge} object. Use
        C{add_edges([(source, target)])} if you don't need the L{Edge}
        object and want to avoid the overhead of creating it.
    """
    eid = graph.ecount()
    graph.add_edges([(source, target)])
    edge = graph.es[eid]
    for key, value in kwds.items():
        edge[key] = value
    return edge


def _add_edges(graph, es, attributes=None):
    """Adds some edges to the graph.

    @param es: the list of edges to be added. Every edge is represented
      with a tuple containing the vertex IDs or names of the two
      endpoints. Vertices are enumerated from zero.
    @param attributes: dict of sequences, all of length equal to the
      number of edges to be added, containing the attributes of the new
      edges.
    """
    eid = graph.ecount()
    res = GraphBase.add_edges(graph, es)
    n = graph.ecount() - eid
    if (attributes is not None) and (n > 0):
        for key, val in attributes.items():
            graph.es[eid:][key] = val
    return res


def _add_vertex(graph, name=None, **kwds):
    """Adds a single vertex to the graph. Keyword arguments will be assigned
    as vertex attributes. Note that C{name} as a keyword argument is treated
    specially; if a graph has C{name} as a vertex attribute, it allows one
    to refer to vertices by their names in most places where igraph expects
    a vertex ID.

    @return: the newly added vertex as a L{Vertex} object. Use
        C{add_vertices(1)} if you don't need the L{Vertex} object and want
        to avoid the overhead of creating t.
    """
    if isinstance(name, int):
        # raise TypeError("cannot use integers as vertex names; use strings instead")
        deprecated(
            "You are using integers as vertex names. This is discouraged because "
            "most igraph functions interpret integers as vertex _IDs_ and strings "
            "as vertex names. For sake of consistency, convert your vertex "
            "names to strings before assigning them. Future versions from igraph "
            "0.11.0 will disallow integers as vertex names."
        )

    vid = graph.vcount()
    graph.add_vertices(1)
    vertex = graph.vs[vid]

    for key, value in kwds.items():
        vertex[key] = value

    if name is not None:
        vertex["name"] = name

    return vertex


def _add_vertices(graph, n, attributes=None):
    """Adds some vertices to the graph.

    Note that if C{n} is a sequence of strings, indicating the names of the
    new vertices, and attributes has a key C{name}, the two conflict. In
    that case the attribute will be applied.

    @param n: the number of vertices to be added, or the name of a single
      vertex to be added, or a sequence of strings, each corresponding to the
      name of a vertex to be added. Names will be assigned to the C{name}
      vertex attribute.
    @param attributes: dict of sequences, all of length equal to the
      number of vertices to be added, containing the attributes of the new
      vertices. If n is a string (so a single vertex is added), then the
      values of this dict are the attributes themselves, but if n=1 then
      they have to be lists of length 1.
    """
    if isinstance(n, str):
        # Adding a single vertex with a name
        m = graph.vcount()
        result = GraphBase.add_vertices(graph, 1)
        graph.vs[m]["name"] = n
        if attributes is not None:
            for key, val in attributes.items():
                graph.vs[m][key] = val
    elif hasattr(n, "__iter__"):
        m = graph.vcount()
        if not hasattr(n, "__len__"):
            names = list(n)
        else:
            names = n
        result = GraphBase.add_vertices(graph, len(names))
        if len(names) > 0:
            graph.vs[m:]["name"] = names
            if attributes is not None:
                for key, val in attributes.items():
                    graph.vs[m:][key] = val
    else:
        result = GraphBase.add_vertices(graph, n)
        if (attributes is not None) and (n > 0):
            m = graph.vcount() - n
            for key, val in attributes.items():
                graph.vs[m:][key] = val
    return result


def _delete_edges(graph, *args, **kwds):
    """Deletes some edges from the graph.

    The set of edges to be deleted is determined by the positional and
    keyword arguments. If the function is called without any arguments,
    all edges are deleted. If any keyword argument is present, or the
    first positional argument is callable, an edge sequence is derived by
    calling L{EdgeSeq.select} with the same positional and keyword
    arguments. Edges in the derived edge sequence will be removed.
    Otherwise the first positional argument is considered as follows:

    Deprecation notice: C{delete_edges(None)} has been replaced by
    C{delete_edges()} - with no arguments - since igraph 0.8.3.

      - C{None} - deletes all edges (deprecated since 0.8.3)
      - a single integer - deletes the edge with the given ID
      - a list of integers - deletes the edges denoted by the given IDs
      - a list of 2-tuples - deletes the edges denoted by the given
        source-target vertex pairs. When multiple edges are present
        between a given source-target vertex pair, only one is removed.
    """
    if len(args) == 0 and len(kwds) == 0:
        return GraphBase.delete_edges(graph)

    if len(kwds) > 0 or (callable(args[0]) and not isinstance(args[0], EdgeSeq)):
        edge_seq = graph.es(*args, **kwds)
    else:
        edge_seq = args[0]
    return GraphBase.delete_edges(graph, edge_seq)


def _clear(graph):
    """Clears the graph, deleting all vertices, edges, and attributes.

    @see: L{GraphBase.delete_vertices} and L{Graph.delete_edges}.
    """
    graph.delete_vertices()
    for attr in graph.attributes():
        del graph[attr]


def _as_directed(graph, *args, **kwds):
    """Returns a directed copy of this graph. Arguments are passed on
    to L{GraphBase.to_directed()} that is invoked on the copy.
    """
    copy = graph.copy()
    copy.to_directed(*args, **kwds)
    return copy


def _as_undirected(graph, *args, **kwds):
    """Returns an undirected copy of this graph. Arguments are passed on
    to L{GraphBase.to_undirected()} that is invoked on the copy.
    """
    copy = graph.copy()
    copy.to_undirected(*args, **kwds)
    return copy
