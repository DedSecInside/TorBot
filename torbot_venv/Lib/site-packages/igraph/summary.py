# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Summary representation of a graph."""

import sys

from igraph.statistics import median
from itertools import islice
from math import ceil
from texttable import Texttable
from textwrap import TextWrapper

__all__ = ("GraphSummary", "summary")


class FakeWrapper:
    """Object whose interface is compatible with C{textwrap.TextWrapper}
    but does no wrapping."""

    def __init__(self, *args, **kwds):
        pass

    def fill(self, text):
        return [text]

    def wrap(self, text):
        return [text]


def _get_wrapper_for_width(width, *args, **kwds):
    """Returns a text wrapper that wraps text for the given width.

    @param width: the maximal width of each line that the text wrapper
      produces. C{None} means that no wrapping will be performed.
    """
    if width is None:
        return FakeWrapper(*args, **kwds)
    return TextWrapper(width=width, *args, **kwds)


class GraphSummary:
    """Summary representation of a graph.

    The summary representation includes a header line and the list of
    edges. The header line consists of C{IGRAPH}, followed by a
    four-character long code, the number of vertices, the number of
    edges, two dashes (C{--}) and the name of the graph (i.e.
    the contents of the C{name} attribute, if any). For instance,
    a header line may look like this::

        IGRAPH U--- 4 5 --

    The four-character code describes some basic properties of the
    graph. The first character is C{U} if the graph is undirected,
    C{D} if it is directed. The second letter is C{N} if the graph
    has a vertex attribute called C{name}, or a dash otherwise. The
    third letter is C{W} if the graph is weighted (i.e. it has an
    edge attribute called C{weight}), or a dash otherwise. The
    fourth letter is C{B} if the graph has a vertex attribute called
    C{type}; this is usually used for bipartite graphs.

    Edges may be presented as an ordinary edge list or an adjacency
    list. By default, this depends on the number of edges; however,
    you can control it with the appropriate constructor arguments.
    """

    def __init__(
        self,
        graph,
        verbosity=0,
        width=78,
        edge_list_format="auto",
        max_rows=99999,
        print_graph_attributes=False,
        print_vertex_attributes=False,
        print_edge_attributes=False,
        full=False,
    ):
        """Constructs a summary representation of a graph.

        @param verbosity: the verbosity of the summary. If zero, only
          the header line will be returned. If one, the header line
          and the list of edges will both be returned.
        @param width: the maximal width of each line in the summary.
          C{None} means that no limit will be enforced.
        @param max_rows: the maximal number of rows to print in a single
          table (e.g., vertex attribute table or edge attribute table)
        @param edge_list_format: format of the edge list in the summary.
          Supported formats are: C{compressed}, C{adjlist}, C{edgelist},
          C{auto}, which selects automatically from the other three based
          on some simple criteria.
        @param print_graph_attributes: whether to print graph attributes
          if there are any.
        @param print_vertex_attributes: whether to print vertex attributes
          if there are any.
        @param print_edge_attributes: whether to print edge attributes
          if there are any.
        @param full: False has no effect; True turns on the attribute
          printing for graph, vertex and edge attributes with verbosity 1.
        """
        if full:
            print_graph_attributes = True
            print_vertex_attributes = True
            print_edge_attributes = True
            verbosity = max(verbosity, 1)

        self._graph = graph
        self.edge_list_format = edge_list_format.lower()
        self.max_rows = int(max_rows)
        self.print_graph_attributes = print_graph_attributes
        self.print_vertex_attributes = print_vertex_attributes
        self.print_edge_attributes = print_edge_attributes
        self.verbosity = verbosity
        self.width = width
        self.wrapper = _get_wrapper_for_width(self.width, break_on_hyphens=False)

        if self._graph.is_named():
            self._edges_header = "+ edges (vertex names):"
        else:
            self._edges_header = "+ edges:"
        self._arrow = ["--", "->"][self._graph.is_directed()]
        self._arrow_format = "%%s%s%%s" % self._arrow

    def _construct_edgelist_adjlist(self):
        """Constructs the part in the summary that prints the edge list in an
        adjacency list format."""
        result = [self._edges_header]

        if self._graph.vcount() == 0:
            return

        if self._graph.is_named():
            names = self._graph.vs["name"]
            maxlen = max(len(str(name)) for name in names)
            format_str = "%%%ds %s %%s" % (maxlen, self._arrow)
            for v1, name in enumerate(names):
                neis = self._graph.successors(v1)
                neis = ", ".join(str(names[v2]) for v2 in neis)
                result.append(format_str % (name, neis))
        else:
            maxlen = len(str(self._graph.vcount()))
            num_format = "%%%dd" % maxlen
            format_str = "%s %s %%s" % (num_format, self._arrow)
            for v1 in range(self._graph.vcount()):
                neis = self._graph.successors(v1)
                neis = " ".join(num_format % v2 for v2 in neis)
                result.append(format_str % (v1, neis))

        # Try to wrap into multiple columns if that works with the given width
        if self.width is not None:
            maxlen = max(len(line) for line in result[1:])
            colcount = int(self.width + 3) / int(maxlen + 3)
            if colcount > 1:
                # Rewrap to multiple columns
                nrows = len(result) - 1
                colheight = int(ceil(nrows / float(colcount)))
                newrows = [[] for _ in range(colheight)]
                for i, row in enumerate(result[1:]):
                    newrows[i % colheight].append(row.ljust(maxlen))
                result[1:] = ["   ".join(row) for row in newrows]

        return result

    def _construct_edgelist_compressed(self):
        """Constructs the part in the summary that prints the edge list in a
        compressed format suitable for graphs with mostly small degrees."""
        result = [self._edges_header]
        arrow = self._arrow_format

        if self._graph.is_named():
            names = self._graph.vs["name"]
            edges = ", ".join(
                arrow % (names[edge.source], names[edge.target])
                for edge in self._graph.es
            )
        else:
            edges = " ".join(arrow % edge.tuple for edge in self._graph.es)

        result.append(edges)
        return result

    def _construct_edgelist_edgelist(self):
        """Constructs the part in the summary that prints the edge list in a
        full edge list format."""
        attrs = sorted(self._graph.edge_attributes())

        table = self._new_table(headers=["", "edge"] + attrs)
        table.add_rows(
            islice(self._edge_attribute_iterator(attrs), 0, self.max_rows), header=False
        )
        table.set_cols_align(
            ["l", "l"] + self._infer_column_alignment(edge_attrs=attrs)
        )

        result = [self._edges_header]
        result.extend(table.draw().split("\n"))

        return result

    def _construct_graph_attributes(self):
        """Constructs the part in the summary that lists the graph attributes."""
        attrs = self._graph.attributes()
        if not attrs:
            return []

        result = ["+ graph attributes:"]
        attrs.sort()
        for attr in attrs:
            result.append("[[%s]]" % (attr,))
            result.append(str(self._graph[attr]))
        return result

    def _construct_vertex_attributes(self):
        """Constructs the part in the summary that lists the vertex attributes."""
        attrs = sorted(self._graph.vertex_attributes())
        if not attrs or (len(attrs) == 1 and "name" in attrs):
            return []

        table = self._new_table(headers=[""] + attrs)
        table.add_rows(
            islice(self._vertex_attribute_iterator(attrs), 0, self.max_rows),
            header=False,
        )
        table.set_cols_align(["l"] + self._infer_column_alignment(vertex_attrs=attrs))

        result = ["+ vertex attributes:"]
        result.extend(table.draw().split("\n"))

        return result

    def _construct_header(self):
        """Constructs the header part of the summary."""
        graph = self._graph
        params = dict(
            directed="UD"[graph.is_directed()],
            named="-N"[graph.is_named()],
            weighted="-W"[graph.is_weighted()],
            typed="-T"["type" in graph.vertex_attributes()],
            vcount=graph.vcount(),
            ecount=graph.ecount(),
        )
        if "name" in graph.attributes():
            params["name"] = graph["name"]
        else:
            params["name"] = ""
        result = [
            "IGRAPH %(directed)s%(named)s%(weighted)s%(typed)s "
            "%(vcount)d %(ecount)d -- %(name)s" % params
        ]

        attrs = ["%s (g)" % (name,) for name in sorted(graph.attributes())]
        attrs.extend("%s (v)" % (name,) for name in sorted(graph.vertex_attributes()))
        attrs.extend("%s (e)" % (name,) for name in sorted(graph.edge_attributes()))
        if attrs:
            result.append("+ attr: %s" % ", ".join(attrs))
            if self.wrapper is not None:
                self.wrapper.subsequent_indent = "  "
                result[-1:] = self.wrapper.wrap(result[-1])
                self.wrapper.subsequent_indent = ""

        return result

    def _edge_attribute_iterator(self, attribute_order):
        """Returns an iterator that yields the rows of the edge attribute table
        in the summary. C{attribute_order} must be a list containing the names of
        the attributes to be presented in this table."""
        arrow = self._arrow_format

        if self._graph.is_named():
            names = self._graph.vs["name"]
            for edge in self._graph.es:
                formatted_edge = arrow % (names[edge.source], names[edge.target])
                yield ["[%d]" % edge.index, formatted_edge] + [
                    edge[attr] for attr in attribute_order
                ]
        else:
            for edge in self._graph.es:
                formatted_edge = arrow % edge.tuple
                yield ["[%d]" % edge.index, formatted_edge] + [
                    edge[attr] for attr in attribute_order
                ]

    def _infer_column_alignment(self, vertex_attrs=None, edge_attrs=None):
        """Infers the preferred alignment for the given vertex and edge attributes
        in the tables by peeking into the attribute values of the first 100 vertices
        or edges. Numeric attributes will be aligned right, everything else will be
        aligned left."""
        values = []
        if vertex_attrs is not None:
            vs = self._graph.vs[:100]
            values.extend(vs[attr] for attr in vertex_attrs)
        if edge_attrs is not None:
            es = self._graph.es[:100]
            values.extend(es[attr] for attr in edge_attrs)

        result = []
        for vs in values:
            is_numeric = True
            try:
                [float(x) for x in vs]
            except ValueError:
                is_numeric = False
            if is_numeric:
                result.append("r")
            else:
                result.append("l")

        return result

    def _new_table(self, headers=None):
        """Constructs a new table to pretty-print vertex and edge attributes"""
        table = Texttable(max_width=0)
        table.set_deco(0)
        if headers is not None:
            table.header(headers)
        return table

    def _vertex_attribute_iterator(self, attribute_order):
        """Returns an iterator that yields the rows of the vertex attribute table
        in the summary. C{attribute_order} must be a list containing the names of
        the attributes to be presented in this table."""
        for vertex in self._graph.vs:
            yield ["[%d]" % vertex.index] + [vertex[attr] for attr in attribute_order]

    def __str__(self):
        """Returns the summary representation as a string."""
        output = self._construct_header()

        if self.print_graph_attributes:
            output.extend(self._construct_graph_attributes())
        if self.print_vertex_attributes:
            output.extend(self._construct_vertex_attributes())

        if self.verbosity <= 0:
            return "\n".join(output)

        if self._graph.ecount() > 0:
            # Add the edge list
            if self.edge_list_format == "auto":
                if self.print_edge_attributes and self._graph.edge_attributes():
                    format = "edgelist"
                elif median(self._graph.degree(mode="out")) < 3:
                    format = "compressed"
                else:
                    format = "adjlist"
            else:
                format = self.edge_list_format

            method_name = "_construct_edgelist_%s" % format
            if hasattr(self, method_name):
                output.extend(getattr(self, method_name)())

        if self.wrapper is not None:
            return "\n".join("\n".join(self.wrapper.wrap(line)) for line in output)

        return "\n".join(output)


def summary(obj, stream=None, *args, **kwds):
    """Prints a summary of object o to a given stream

    Positional and keyword arguments not explicitly mentioned here are passed
    on to the underlying C{summary()} method of the object if it has any.

    @param obj: the object about which a human-readable summary is requested.
    @param stream: the stream to be used. If C{None}, the standard output
      will be used.
    """
    if stream is None:
        stream = sys.stdout
    if hasattr(obj, "summary"):
        stream.write(obj.summary(*args, **kwds))
    else:
        stream.write(str(obj))
    stream.write("\n")
