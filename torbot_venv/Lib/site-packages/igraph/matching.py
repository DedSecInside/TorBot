# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Classes representing matchings on graphs."""

from igraph._igraph import Vertex


class Matching:
    """A matching of vertices in a graph.

    A matching of an undirected graph is a set of edges such that each
    vertex is incident on at most one matched edge. When each vertex is
    incident on I{exactly} one matched edge, the matching called
    I{perfect}. This class is used in C{igraph} to represent non-perfect
    and perfect matchings in undirected graphs.

    This class is usually not instantiated directly, everything
    is taken care of by the functions that return matchings.

    Examples:

      >>> from igraph import Graph
      >>> g = Graph.Famous("noperfectmatching")
      >>> matching = g.maximum_matching()
    """

    def __init__(self, graph, matching, types=None):
        """Initializes the matching.

        @param graph: the graph the matching belongs to
        @param matching: a numeric vector where element I{i} corresponds to
          vertex I{i} of the graph. Element I{i} is -1 or if the corresponding
          vertex is unmatched, otherwise it contains the index of the vertex to
          which vertex I{i} is matched.
        @param types: the types of the vertices if the graph is bipartite.
          It must either be the name of a vertex attribute (which will be
          retrieved for all vertices) or a list. Elements in the list will be
          converted to boolean values C{True} or C{False}, and this will
          determine which part of the bipartite graph a given vertex belongs to.
        @raise ValueError: if the matching vector supplied does not describe
          a valid matching of the graph.
        """
        self._graph = graph
        self._matching = None
        self._num_matched = 0
        self._types = None

        if isinstance(types, str):
            types = graph.vs[types]

        self.types = types
        self.matching = matching

    def __len__(self):
        return self._num_matched

    def __repr__(self):
        if self._types is not None:
            return "%s(%r,%r,types=%r)" % (
                self.__class__.__name__,
                self._graph,
                self._matching,
                self._types,
            )
        else:
            return "%s(%r,%r)" % (self.__class__.__name__, self._graph, self._matching)

    def __str__(self):
        if self._types is not None:
            return "Bipartite graph matching (%d matched vertex pairs)" % len(self)
        else:
            return "Graph matching (%d matched vertex pairs)" % len(self)

    def edges(self):
        """Returns an edge sequence that contains the edges in the matching.

        If there are multiple edges between a pair of matched vertices, only one
        of them will be returned.
        """
        get_eid = self._graph.get_eid
        eidxs = [
            get_eid(u, v, directed=False)
            for u, v in enumerate(self._matching)
            if v != -1 and u <= v
        ]
        return self._graph.es[eidxs]

    @property
    def graph(self):
        """Returns the graph corresponding to the matching."""
        return self._graph

    def is_maximal(self):
        """Returns whether the matching is maximal.

        A matching is maximal when it is not possible to extend it any more
        with extra edges; in other words, unmatched vertices in the graph
        must be adjacent to matched vertices only.
        """
        return self._graph._is_maximal_matching(self._matching, types=self._types)

    def is_matched(self, vertex):
        """Returns whether the given vertex is matched to another one."""
        if isinstance(vertex, Vertex):
            vertex = vertex.index
        return self._matching[vertex] >= 0

    def match_of(self, vertex):
        """Returns the vertex a given vertex is matched to.

        @param vertex: the vertex we are interested in; either an integer index
          or an instance of L{Vertex}.
        @return: the index of the vertex matched to the given vertex, either as
          an integer index (if I{vertex} was integer) or as an instance of
          L{Vertex}. When the vertex is unmatched, returns C{None}.
        """
        if isinstance(vertex, Vertex):
            matched = self._matching[vertex.index]
            if matched < 0:
                return None
            return self._graph.vs[matched]

        matched = self._matching[vertex]
        if matched < 0:
            return None
        return matched

    @property
    def matching(self):
        """Returns the matching vector where element I{i} contains the ID of
        the vertex that vertex I{i} is matched to.

        The matching vector will contain C{-1} for unmatched vertices.
        """
        return self._matching

    @matching.setter
    def matching(self, value):
        """Sets the matching vector.

        @param value: the matching vector which must contain the ID of the
          vertex matching vertex I{i} at the I{i}th position, or C{-1} if
          the vertex is unmatched.
        @raise ValueError: if the matching vector supplied does not describe
          a valid matching of the graph.
        """
        if not self.graph._is_matching(value, types=self._types):
            raise ValueError("not a valid matching")
        self._matching = list(value)
        self._num_matched = sum(1 for i in self._matching if i >= 0) // 2

    @property
    def types(self):
        """Returns the type vector if the graph is bipartite.

        Element I{i} of the type vector will be C{False} or C{True} depending
        on which side of the bipartite graph vertex I{i} belongs to.

        For non-bipartite graphs, this property returns C{None}.
        """
        return self._types

    @types.setter
    def types(self, value):
        types = [bool(x) for x in value]
        if len(types) < self._graph.vcount():
            raise ValueError("type vector too short")
        self._types = types
