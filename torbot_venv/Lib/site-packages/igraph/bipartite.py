from igraph._igraph import GraphBase
from igraph.matching import Matching


def _maximum_bipartite_matching(graph, types="type", weights=None, eps=None):
    """Finds a maximum matching in a bipartite graph.

    A maximum matching is a set of edges such that each vertex is incident on
    at most one matched edge and the number (or weight) of such edges in the
    set is as large as possible.

    @param types: vertex types in a list or the name of a vertex attribute
      holding vertex types. Types should be denoted by zeros and ones (or
      C{False} and C{True}) for the two sides of the bipartite graph.
      If omitted, it defaults to C{type}, which is the default vertex type
      attribute for bipartite graphs.
    @param weights: edge weights to be used. Can be a sequence or iterable or
      even an edge attribute name.
    @param eps: a small real number used in equality tests in the weighted
      bipartite matching algorithm. Two real numbers are considered equal in
      the algorithm if their difference is smaller than this value. This
      is required to avoid the accumulation of numerical errors. If you
      pass C{None} here, igraph will try to determine an appropriate value
      automatically.
    @return: an instance of L{Matching}."""
    if eps is None:
        eps = -1

    matches = GraphBase._maximum_bipartite_matching(graph, types, weights, eps)
    return Matching(graph, matches, types=types)


def _bipartite_projection(
    graph, types="type", multiplicity=True, probe1=-1, which="both"
):
    """Projects a bipartite graph into two one-mode graphs. Edge directions
    are ignored while projecting.

    Examples:

    >>> g = Graph.Full_Bipartite(10, 5)
    >>> g1, g2 = g.bipartite_projection()
    >>> g1.isomorphic(Graph.Full(10))
    True
    >>> g2.isomorphic(Graph.Full(5))
    True

    @param types: an igraph vector containing the vertex types, or an
      attribute name. Anything that evalulates to C{False} corresponds to
      vertices of the first kind, everything else to the second kind.
    @param multiplicity: if C{True}, then igraph keeps the multiplicity of
      the edges in the projection in an edge attribute called C{"weight"}.
      E.g., if there is an A-C-B and an A-D-B triplet in the bipartite
      graph and there is no other X (apart from X=B and X=D) for which an
      A-X-B triplet would exist in the bipartite graph, the multiplicity
      of the A-B edge in the projection will be 2.
    @param probe1: this argument can be used to specify the order of the
      projections in the resulting list. If given and non-negative, then
      it is considered as a vertex ID; the projection containing the
      vertex will be the first one in the result.
    @param which: this argument can be used to specify which of the two
      projections should be returned if only one of them is needed. Passing
      0 here means that only the first projection is returned, while 1 means
      that only the second projection is returned. (Note that we use 0 and 1
      because Python indexing is zero-based). C{False} is equivalent to 0 and
      C{True} is equivalent to 1. Any other value means that both projections
      will be returned in a tuple.
    @return: a tuple containing the two projected one-mode graphs if C{which}
      is not 1 or 2, or the projected one-mode graph specified by the
      C{which} argument if its value is 0, 1, C{False} or C{True}.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    superclass_meth = super(Graph, graph).bipartite_projection

    if which is False:
        which = 0
    elif which is True:
        which = 1
    if which != 0 and which != 1:
        which = -1

    if multiplicity:
        if which == 0:
            g1, w1 = superclass_meth(types, True, probe1, which)
            g2, w2 = None, None
        elif which == 1:
            g1, w1 = None, None
            g2, w2 = superclass_meth(types, True, probe1, which)
        else:
            g1, g2, w1, w2 = superclass_meth(types, True, probe1, which)

        if g1 is not None:
            g1.es["weight"] = w1
            if g2 is not None:
                g2.es["weight"] = w2
                return g1, g2
            else:
                return g1
        else:
            g2.es["weight"] = w2
            return g2
    else:
        return superclass_meth(types, False, probe1, which)


def _bipartite_projection_size(graph, types="type", *args, **kwds):
    """Calculates the number of vertices and edges in the bipartite
    projections of this graph according to the specified vertex types.
    This is useful if you have a bipartite graph and you want to estimate
    the amount of memory you would need to calculate the projections
    themselves.

    @param types: an igraph vector containing the vertex types, or an
      attribute name. Anything that evalulates to C{False} corresponds to
      vertices of the first kind, everything else to the second kind.
    @return: a 4-tuple containing the number of vertices and edges in the
      first projection, followed by the number of vertices and edges in the
      second projection.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    return super(Graph, graph).bipartite_projection_size(types, *args, **kwds)
