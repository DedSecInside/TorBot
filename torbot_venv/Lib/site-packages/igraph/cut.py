# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Classes representing cuts and flows on graphs."""

from igraph._igraph import (
    GraphBase,
)
from igraph.clustering import VertexClustering


class Cut(VertexClustering):
    """A cut of a given graph.

    This is a simple class used to represent cuts returned by
    L{Graph.mincut()}, L{Graph.all_st_cuts()} and other functions
    that calculate cuts.

    A cut is a special vertex clustering with only two clusters.
    Besides the usual L{VertexClustering} methods, it also has the
    following attributes:

      - C{value} - the value (capacity) of the cut. It is equal to
        the number of edges if there are no capacities on the
        edges.

      - C{partition} - vertex IDs in the parts created
        after removing edges in the cut

      - C{cut} - edge IDs in the cut

      - C{es} - an edge selector restricted to the edges
        in the cut.

    You can use indexing on this object to obtain lists of vertex IDs
    for both sides of the partition.

    This class is usually not instantiated directly, everything
    is taken care of by the functions that return cuts.

    Examples:

      >>> from igraph import Graph
      >>> g = Graph.Ring(20)
      >>> mc = g.mincut()
      >>> print(mc.value)
      2.0
      >>> print(min(len(x) for x in mc))
      1
      >>> mc.es["color"] = "red"
    """

    def __init__(self, graph, value=None, cut=None, partition=None, partition2=None):
        """Initializes the cut.

        This should not be called directly, everything is taken care of by
        the functions that return cuts.
        """
        # Input validation
        if partition is None or cut is None:
            raise ValueError("partition and cut must be given")

        # Set up a membership vector, initialize parent class
        membership = [1] * graph.vcount()
        for vid in partition:
            membership[vid] = 0
        super().__init__(graph, membership)

        if value is None:
            # Value of the cut not given, count the number of edges
            value = len(cut)
        self._value = float(value)

        self._partition = sorted(partition)
        self._cut = cut

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self._graph,
            self._value,
            self._cut,
            self._partition,
        )

    def __str__(self):
        return "Graph cut (%d edges, %d vs %d vertices, value=%.4f)" % (
            len(self._cut),
            len(self._partition),
            self._graph.vcount() - len(self._partition),
            self._value,
        )

    @property
    def es(self):
        """Returns an edge selector restricted to the cut"""
        return self._graph.es.select(self.cut)

    @property
    def partition(self):
        """Returns the vertex IDs partitioned according to the cut"""
        return list(self)

    @property
    def cut(self):
        """Returns the edge IDs in the cut"""
        return self._cut

    @property
    def value(self):
        """Returns the sum of edge capacities in the cut"""
        return self._value


class Flow(Cut):
    """A flow of a given graph.

    This is a simple class used to represent flows returned by
    L{Graph.maxflow}. It has the following attributes:

      - C{graph} - the graph on which this flow is defined

      - C{value} - the value (capacity) of the flow

      - C{flow} - the flow values on each edge. For directed graphs,
        this is simply a list where element M{i} corresponds to the
        flow on edge M{i}. For undirected graphs, the direction of
        the flow is not constrained (since the edges are undirected),
        hence positive flow always means a flow from the smaller vertex
        ID to the larger, while negative flow means a flow from the
        larger vertex ID to the smaller.

      - C{cut} - edge IDs in the minimal cut corresponding to
        the flow.

      - C{partition} - vertex IDs in the parts created
        after removing edges in the cut

      - C{es} - an edge selector restricted to the edges
        in the cut.

    This class is usually not instantiated directly, everything
    is taken care of by L{Graph.maxflow}.

    Examples:

      >>> from igraph import Graph
      >>> g = Graph.Ring(20)
      >>> mf = g.maxflow(0, 10)
      >>> print(mf.value)
      2.0
      >>> mf.es["color"] = "red"
    """

    def __init__(self, graph, value, flow, cut, partition):
        """Initializes the flow.

        This should not be called directly, everything is
        taken care of by L{Graph.maxflow}.
        """
        super().__init__(graph, value, cut, partition)
        self._flow = flow

    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r)" % (
            self.__class__.__name__,
            self._graph,
            self._value,
            self._flow,
            self._cut,
            self._partition,
        )

    def __str__(self):
        return "Graph flow (%d edges, %d vs %d vertices, value=%.4f)" % (
            len(self._cut),
            len(self._partition),
            self._graph.vcount() - len(self._partition),
            self._value,
        )

    @property
    def flow(self):
        """Returns the flow values for each edge.

        For directed graphs, this is simply a list where element M{i}
        corresponds to the flow on edge M{i}. For undirected graphs, the
        direction of the flow is not constrained (since the edges are
        undirected), hence positive flow always means a flow from the smaller
        vertex ID to the larger, while negative flow means a flow from the
        larger vertex ID to the smaller.
        """
        return self._flow


def _all_st_cuts(graph, source, target):
    """\
    Returns all the cuts between the source and target vertices in a
    directed graph.

    This function lists all edge-cuts between a source and a target vertex.
    Every cut is listed exactly once.

    @param source: the source vertex ID
    @param target: the target vertex ID
    @return: a list of L{Cut} objects.

    @newfield ref: Reference
    @ref: JS Provan and DR Shier: A paradigm for listing (s,t)-cuts in
      graphs. Algorithmica 15, 351--372, 1996.
    """
    return [
        Cut(graph, cut=cut, partition=part)
        for cut, part in zip(*GraphBase.all_st_cuts(graph, source, target))
    ]


def _all_st_mincuts(graph, source, target, capacity=None):
    """\
    Returns all the mincuts between the source and target vertices in a
    directed graph.

    This function lists all minimum edge-cuts between a source and a target
    vertex.

    @param source: the source vertex ID
    @param target: the target vertex ID
    @param capacity: the edge capacities (weights). If C{None}, all
      edges have equal weight. May also be an attribute name.
    @return: a list of L{Cut} objects.

    @newfield ref: Reference
    @ref: JS Provan and DR Shier: A paradigm for listing (s,t)-cuts in
      graphs. Algorithmica 15, 351--372, 1996.
    """
    value, cuts, parts = GraphBase.all_st_mincuts(graph, source, target, capacity)
    return [
        Cut(graph, value, cut=cut, partition=part) for cut, part in zip(cuts, parts)
    ]


def _gomory_hu_tree(graph, capacity=None, flow="flow"):
    """Calculates the Gomory-Hu tree of an undirected graph with optional
    edge capacities.

    The Gomory-Hu tree is a concise representation of the value of all the
    maximum flows (or minimum cuts) in a graph. The vertices of the tree
    correspond exactly to the vertices of the original graph in the same order.
    Edges of the Gomory-Hu tree are annotated by flow values.  The value of
    the maximum flow (or minimum cut) between an arbitrary (u,v) vertex
    pair in the original graph is then given by the minimum flow value (i.e.
    edge annotation) along the shortest path between u and v in the
    Gomory-Hu tree.

    @param capacity: the edge capacities (weights). If C{None}, all
      edges have equal weight. May also be an attribute name.
    @param flow: the name of the edge attribute in the returned graph
      in which the flow values will be stored.
    @return: the Gomory-Hu tree as a L{Graph} object.
    """
    graph, flow_values = GraphBase.gomory_hu_tree(graph, capacity)
    graph.es[flow] = flow_values
    return graph


def _maxflow(graph, source, target, capacity=None):
    """Returns a maximum flow between the given source and target vertices
    in a graph.

    A maximum flow from I{source} to I{target} is an assignment of
    non-negative real numbers to the edges of the graph, satisfying
    two properties:

        1. For each edge, the flow (i.e. the assigned number) is not
           more than the capacity of the edge (see the I{capacity}
           argument)

        2. For every vertex except the source and the target, the
           incoming flow is the same as the outgoing flow.

    The value of the flow is the incoming flow of the target or the
    outgoing flow of the source (which are equal). The maximum flow
    is the maximum possible such value.

    @param capacity: the edge capacities (weights). If C{None}, all
      edges have equal weight. May also be an attribute name.
    @return: a L{Flow} object describing the maximum flow
    """
    return Flow(graph, *GraphBase.maxflow(graph, source, target, capacity))


def _mincut(graph, source=None, target=None, capacity=None):
    """Calculates the minimum cut between the given source and target vertices
    or within the whole graph.

    The minimum cut is the minimum set of edges that needs to be removed to
    separate the source and the target (if they are given) or to disconnect the
    graph (if neither the source nor the target are given). The minimum is
    calculated using the weights (capacities) of the edges, so the cut with
    the minimum total capacity is calculated.

    For undirected graphs and no source and target, the method uses the
    Stoer-Wagner algorithm. For a given source and target, the method uses the
    push-relabel algorithm; see the references below.

    @param source: the source vertex ID. If C{None}, the target must also be
      C{None} and the calculation will be done for the entire graph (i.e.
      all possible vertex pairs).
    @param target: the target vertex ID. If C{None}, the source must also be
      C{None} and the calculation will be done for the entire graph (i.e.
      all possible vertex pairs).
    @param capacity: the edge capacities (weights). If C{None}, all
      edges have equal weight. May also be an attribute name.
    @return: a L{Cut} object describing the minimum cut
    """
    return Cut(graph, *GraphBase.mincut(graph, source, target, capacity))


def _st_mincut(graph, source, target, capacity=None):
    """Calculates the minimum cut between the source and target vertices in a
    graph.

    @param source: the source vertex ID
    @param target: the target vertex ID
    @param capacity: the capacity of the edges. It must be a list or a valid
      attribute name or C{None}. In the latter case, every edge will have the
      same capacity.
    @return: the value of the minimum cut, the IDs of vertices in the
      first and second partition, and the IDs of edges in the cut,
      packed in a 4-tuple
    """
    return Cut(graph, *GraphBase.st_mincut(graph, source, target, capacity))
