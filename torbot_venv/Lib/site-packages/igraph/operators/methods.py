from igraph._igraph import (
    GraphBase,
    Vertex,
    Edge,
)
from igraph.seq import VertexSeq, EdgeSeq
from igraph.operators.functions import (
    disjoint_union,
    union,
    intersection,
)


__all__ = (
    "__iadd__",
    "__add__",
    "__and__",
    "__isub__",
    "__sub__",
    "__mul__",
    "__or__",
    "_disjoint_union",
    "_union",
    "_intersection",
)


def _disjoint_union(graph, other):
    """Creates the disjoint union of two (or more) graphs.

    @param other: graph or list of graphs to be united with the current one.
    @return: the disjoint union graph
    """
    if isinstance(other, GraphBase):
        other = [other]
    return disjoint_union([graph] + other)


def _union(graph, other, byname="auto"):
    """Creates the union of two (or more) graphs.

    @param other: graph or list of graphs to be united with the current one.
    @param byname: whether to use vertex names instead of ids. See
      L{igraph.operators.union} for details.
    @return: the union graph
    """
    if isinstance(other, GraphBase):
        other = [other]
    return union([graph] + other, byname=byname)


def _intersection(graph, other, byname="auto"):
    """Creates the intersection of two (or more) graphs.

    @param other: graph or list of graphs to be intersected with
      the current one.
    @param byname: whether to use vertex names instead of ids. See
      L{igraph.operators.intersection} for details.
    @return: the intersection graph
    """
    if isinstance(other, GraphBase):
        other = [other]
    return intersection([graph] + other, byname=byname)


def __iadd__(graph, other):
    """In-place addition (disjoint union).

    @see: L{__add__}
    """
    if isinstance(other, (int, str)):
        graph.add_vertices(other)
        return graph
    elif isinstance(other, tuple) and len(other) == 2:
        graph.add_edges([other])
        return graph
    elif isinstance(other, list):
        if not other:
            return graph
        if isinstance(other[0], tuple):
            graph.add_edges(other)
            return graph
        if isinstance(other[0], str):
            graph.add_vertices(other)
            return graph
    return NotImplemented


def __add__(graph, other):
    """Copies the graph and extends the copy depending on the type of
    the other object given.

    @param other: if it is an integer, the copy is extended by the given
      number of vertices. If it is a string, the copy is extended by a
      single vertex whose C{name} attribute will be equal to the given
      string. If it is a tuple with two elements, the copy
      is extended by a single edge. If it is a list of tuples, the copy
      is extended by multiple edges. If it is a L{Graph}, a disjoint
      union is performed.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, (int, str)):
        g = graph.copy()
        g.add_vertices(other)
    elif isinstance(other, tuple) and len(other) == 2:
        g = graph.copy()
        g.add_edges([other])
    elif isinstance(other, list):
        if len(other) > 0:
            if isinstance(other[0], tuple):
                g = graph.copy()
                g.add_edges(other)
            elif isinstance(other[0], str):
                g = graph.copy()
                g.add_vertices(other)
            elif isinstance(other[0], Graph):
                return graph.disjoint_union(other)
            else:
                return NotImplemented
        else:
            return graph.copy()

    elif isinstance(other, Graph):
        return graph.disjoint_union(other)
    else:
        return NotImplemented

    return g


def __and__(graph, other):
    """Graph intersection operator.

    @param other: the other graph to take the intersection with.
    @return: the intersected graph.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, Graph):
        return graph.intersection(other)
    else:
        return NotImplemented


def __isub__(graph, other):
    """In-place subtraction (difference).

    @see: L{__sub__}"""
    if isinstance(other, int):
        graph.delete_vertices([other])
    elif isinstance(other, tuple) and len(other) == 2:
        graph.delete_edges([other])
    elif isinstance(other, list):
        if len(other) > 0:
            if isinstance(other[0], tuple):
                graph.delete_edges(other)
            elif isinstance(other[0], (int, str)):
                graph.delete_vertices(other)
            else:
                return NotImplemented
    elif isinstance(other, Vertex):
        graph.delete_vertices(other)
    elif isinstance(other, VertexSeq):
        graph.delete_vertices(other)
    elif isinstance(other, Edge):
        graph.delete_edges(other)
    elif isinstance(other, EdgeSeq):
        graph.delete_edges(other)
    else:
        return NotImplemented
    return graph


def __sub__(graph, other):
    """Removes the given object(s) from the graph

    @param other: if it is an integer, removes the vertex with the given
      ID from the graph (note that the remaining vertices will get
      re-indexed!). If it is a tuple, removes the given edge. If it is
      a graph, takes the difference of the two graphs. Accepts
      lists of integers or lists of tuples as well, but they can't be
      mixed! Also accepts L{Edge} and L{EdgeSeq} objects.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, Graph):
        return graph.difference(other)

    result = graph.copy()
    if isinstance(other, (int, str)):
        result.delete_vertices([other])
    elif isinstance(other, tuple) and len(other) == 2:
        result.delete_edges([other])
    elif isinstance(other, list):
        if len(other) > 0:
            if isinstance(other[0], tuple):
                result.delete_edges(other)
            elif isinstance(other[0], (int, str)):
                result.delete_vertices(other)
            else:
                return NotImplemented
        else:
            return result
    elif isinstance(other, Vertex):
        result.delete_vertices(other)
    elif isinstance(other, VertexSeq):
        result.delete_vertices(other)
    elif isinstance(other, Edge):
        result.delete_edges(other)
    elif isinstance(other, EdgeSeq):
        result.delete_edges(other)
    else:
        return NotImplemented

    return result


def __mul__(graph, other):
    """Copies exact replicas of the original graph an arbitrary number of
    times.

    @param other: if it is an integer, multiplies the graph by creating the
      given number of identical copies and taking the disjoint union of
      them.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, int):
        if other == 0:
            return Graph()
        elif other == 1:
            return graph
        elif other > 1:
            return graph.disjoint_union([graph] * (other - 1))
        else:
            return NotImplemented

    return NotImplemented


def __or__(graph, other):
    """Graph union operator.

    @param other: the other graph to take the union with.
    @return: the union graph.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    if isinstance(other, Graph):
        return graph.union(other)
    else:
        return NotImplemented
