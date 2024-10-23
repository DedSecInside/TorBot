def _construct_bipartite_graph_from_adjacency(
    cls,
    matrix,
    directed=False,
    mode="out",
    multiple=False,
    weighted=None,
    *args,
    **kwds
):
    """Creates a bipartite graph from a bipartite adjacency matrix.

    Example:

    >>> g = Graph.Biadjacency([[0, 1, 1], [1, 1, 0]])

    @param matrix: the bipartite adjacency matrix.
    @param directed: whether to create a directed graph.
    @param mode: defines the direction of edges in the graph. If
      C{"out"}, then edges go from vertices of the first kind
      (corresponding to rows of the matrix) to vertices of the
      second kind (the columns of the matrix). If C{"in"}, the
      opposite direction is used. C{"all"} creates mutual edges.
      Ignored for undirected graphs.
    @param multiple: defines what to do with non-zero entries in the
      matrix. If C{False}, non-zero entries will create an edge no matter
      what the value is. If C{True}, non-zero entries are rounded up to
      the nearest integer and this will be the number of multiple edges
      created.
    @param weighted: defines whether to create a weighted graph from the
      adjacency matrix. If it is c{None} then an unweighted graph is created
      and the multiple argument is used to determine the edges of the graph.
      If it is a string then for every non-zero matrix entry, an edge is created
      and the value of the entry is added as an edge attribute named by the
      weighted argument. If it is C{True} then a weighted graph is created and
      the name of the edge attribute will be C{"weight"}.

    @raise ValueError: if the weighted and multiple are passed together.

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    is_weighted = True if weighted or weighted == "" else False
    if is_weighted and multiple:
        raise ValueError("arguments weighted and multiple can not co-exist")
    result, types = cls._Biadjacency(matrix, directed, mode, multiple, *args, **kwds)
    result.vs["type"] = types
    if is_weighted:
        weight_attr = "weight" if weighted is True else weighted
        _, rows, _ = result.get_biadjacency()
        num_vertices_of_first_kind = len(rows)
        for edge in result.es:
            source, target = edge.tuple
            if source in rows:
                edge[weight_attr] = matrix[source][target - num_vertices_of_first_kind]
            else:
                edge[weight_attr] = matrix[target][source - num_vertices_of_first_kind]
    return result


def _construct_bipartite_graph(cls, types, edges, directed=False, *args, **kwds):
    """Creates a bipartite graph with the given vertex types and edges.
    This is similar to the default constructor of the graph, the
    only difference is that it checks whether all the edges go
    between the two vertex classes and it assigns the type vector
    to a C{type} attribute afterwards.

    Examples:

    >>> g = Graph.Bipartite([0, 1, 0, 1], [(0, 1), (2, 3), (0, 3)])
    >>> g.is_bipartite()
    True
    >>> g.vs["type"]
    [False, True, False, True]

    @param types: the vertex types as a boolean list. Anything that
      evaluates to C{False} will denote a vertex of the first kind,
      anything that evaluates to C{True} will denote a vertex of the
      second kind.
    @param edges: the edges as a list of tuples.
    @param directed: whether to create a directed graph. Bipartite
      networks are usually undirected, so the default is C{False}

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    result = cls._Bipartite(types, edges, directed, *args, **kwds)
    result.vs["type"] = [bool(x) for x in types]
    return result


def _construct_full_bipartite_graph(
    cls, n1, n2, directed=False, mode="all", *args, **kwds
):
    """Generates a full bipartite graph (directed or undirected, with or
    without loops).

    >>> g = Graph.Full_Bipartite(2, 3)
    >>> g.is_bipartite()
    True
    >>> g.vs["type"]
    [False, False, True, True, True]

    @param n1: the number of vertices of the first kind.
    @param n2: the number of vertices of the second kind.
    @param directed: whether tp generate a directed graph.
    @param mode: if C{"out"}, then all vertices of the first kind are
      connected to the others; C{"in"} specifies the opposite direction,
      C{"all"} creates mutual edges. Ignored for undirected graphs.

    @return: the graph with a binary vertex attribute named C{"type"} that
      stores the vertex classes.
    """
    result, types = cls._Full_Bipartite(n1, n2, directed, mode, *args, **kwds)
    result.vs["type"] = types
    return result


def _construct_random_bipartite_graph(
    cls, n1, n2, p=None, m=None, directed=False, neimode="all", *args, **kwds
):
    """Generates a random bipartite graph with the given number of vertices and
    edges (if m is given), or with the given number of vertices and the given
    connection probability (if p is given).

    If m is given but p is not, the generated graph will have n1 vertices of
    type 1, n2 vertices of type 2 and m randomly selected edges between them. If
    p is given but m is not, the generated graph will have n1 vertices of type 1
    and n2 vertices of type 2, and each edge will exist between them with
    probability p.

    @param n1: the number of vertices of type 1.
    @param n2: the number of vertices of type 2.
    @param p: the probability of edges. If given, C{m} must be missing.
    @param m: the number of edges. If given, C{p} must be missing.
    @param directed: whether to generate a directed graph.
    @param neimode: if the graph is directed, specifies how the edges will be
      generated. If it is C{"all"}, edges will be generated in both directions
      (from type 1 to type 2 and vice versa) independently. If it is C{"out"}
      edges will always point from type 1 to type 2. If it is C{"in"}, edges
      will always point from type 2 to type 1. This argument is ignored for
      undirected graphs.
    """
    if p is None:
        p = -1
    if m is None:
        m = -1
    result, types = cls._Random_Bipartite(
        n1, n2, p, m, directed, neimode, *args, **kwds
    )
    result.vs["type"] = types
    return result
