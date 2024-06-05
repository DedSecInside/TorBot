from igraph._igraph import (
    GET_ADJACENCY_BOTH,
    GET_ADJACENCY_LOWER,
    GET_ADJACENCY_UPPER,
    GraphBase,
)
from igraph.datatypes import Matrix


__all__ = (
    "_get_adjacency",
    "_get_adjacency_sparse",
    "_get_adjlist",
    "_get_biadjacency",
    "_get_inclist",
)


def _get_adjacency(
    self, type=GET_ADJACENCY_BOTH, attribute=None, default=0, eids=False
):
    """Returns the adjacency matrix of a graph.

    @param type: either C{GET_ADJACENCY_LOWER} (uses the lower
      triangle of the matrix) or C{GET_ADJACENCY_UPPER}
      (uses the upper triangle) or C{GET_ADJACENCY_BOTH}
      (uses both parts). Ignored for directed graphs.
    @param attribute: if C{None}, returns the ordinary adjacency
      matrix. When the name of a valid edge attribute is given
      here, the matrix returned will contain the default value
      at the places where there is no edge or the value of the
      given attribute where there is an edge. Multiple edges are
      not supported, the value written in the matrix in this case
      will be unpredictable. This parameter is ignored if
      I{eids} is C{True}
    @param default: the default value written to the cells in the
      case of adjacency matrices with attributes.
    @param eids: specifies whether the edge IDs should be returned
      in the adjacency matrix. Since zero is a valid edge ID, the
      cells in the matrix that correspond to unconnected vertex
      pairs will contain -1 instead of 0 if I{eids} is C{True}.
      If I{eids} is C{False}, the number of edges will be returned
      in the matrix for each vertex pair.
    @return: the adjacency matrix as a L{Matrix}.
    """
    if (
        type != GET_ADJACENCY_LOWER
        and type != GET_ADJACENCY_UPPER
        and type != GET_ADJACENCY_BOTH
    ):
        # Maybe it was called with the first argument as the attribute name
        type, attribute = attribute, type
        if type is None:
            type = GET_ADJACENCY_BOTH

    if eids:
        result = Matrix(GraphBase.get_adjacency(self, type, eids))
        result -= 1
        return result

    if attribute is None:
        return Matrix(GraphBase.get_adjacency(self, type))

    if attribute not in self.es.attribute_names():
        raise ValueError("Attribute does not exist")

    data = [[default] * self.vcount() for _ in range(self.vcount())]

    if self.is_directed():
        for edge in self.es:
            data[edge.source][edge.target] = edge[attribute]
        return Matrix(data)

    if type == GET_ADJACENCY_BOTH:
        for edge in self.es:
            source, target = edge.tuple
            data[source][target] = edge[attribute]
            data[target][source] = edge[attribute]
    elif type == GET_ADJACENCY_UPPER:
        for edge in self.es:
            data[min(edge.tuple)][max(edge.tuple)] = edge[attribute]
    else:
        for edge in self.es:
            data[max(edge.tuple)][min(edge.tuple)] = edge[attribute]

    return Matrix(data)


def _get_adjacency_sparse(self, attribute=None):
    """Returns the adjacency matrix of a graph as a SciPy CSR matrix.

    @param attribute: if C{None}, returns the ordinary adjacency
      matrix. When the name of a valid edge attribute is given
      here, the matrix returned will contain the default value
      at the places where there is no edge or the value of the
      given attribute where there is an edge.
    @return: the adjacency matrix as a C{scipy.sparse.csr_matrix}.
    """
    try:
        from scipy import sparse
    except ImportError:
        raise ImportError("You should install scipy in order to use this function")

    edges = self.get_edgelist()
    if attribute is None:
        weights = [1] * len(edges)
    else:
        if attribute not in self.es.attribute_names():
            raise ValueError("Attribute does not exist")

        weights = self.es[attribute]

    N = self.vcount()
    mtx = sparse.csr_matrix((weights, list(zip(*edges))), shape=(N, N))

    if not self.is_directed():
        mtx = mtx + sparse.triu(mtx, 1).T + sparse.tril(mtx, -1).T
    return mtx


def _get_adjlist(self, mode="out"):
    """Returns the adjacency list representation of the graph.

    The adjacency list representation is a list of lists. Each item of the
    outer list belongs to a single vertex of the graph. The inner list
    contains the neighbors of the given vertex.

    @param mode: if C{\"out\"}, returns the successors of the vertex. If
      C{\"in\"}, returns the predecessors of the vertex. If C{\"all"\"}, both
      the predecessors and the successors will be returned. Ignored
      for undirected graphs.
    """
    return [self.neighbors(idx, mode) for idx in range(self.vcount())]


def _get_biadjacency(graph, types="type", *args, **kwds):
    """Returns the bipartite adjacency matrix of a bipartite graph. The
    bipartite adjacency matrix is an M{n} times M{m} matrix, where M{n} and
    M{m} are the number of vertices in the two vertex classes.

    @param types: an igraph vector containing the vertex types, or an
      attribute name. Anything that evalulates to C{False} corresponds to
      vertices of the first kind, everything else to the second kind.
    @return: the bipartite adjacency matrix and two lists in a triplet. The
      first list defines the mapping between row indices of the matrix and the
      original vertex IDs. The second list is the same for the column indices.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    return super(Graph, graph).get_biadjacency(types, *args, **kwds)


def _get_inclist(graph, mode="out"):
    """Returns the incidence list representation of the graph.

    The incidence list representation is a list of lists. Each
    item of the outer list belongs to a single vertex of the graph.
    The inner list contains the IDs of the incident edges of the
    given vertex.

    @param mode: if C{\"out\"}, returns the successors of the vertex. If
      C{\"in\"}, returns the predecessors of the vertex. If C{\"all\"}, both
      the predecessors and the successors will be returned. Ignored
      for undirected graphs.
    """
    return [graph.incident(idx, mode) for idx in range(graph.vcount())]
