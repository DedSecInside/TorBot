import operator

from igraph._igraph import (
    EdgeSeq as _EdgeSeq,
    VertexSeq as _VertexSeq,
)


class VertexSeq(_VertexSeq):
    """Class representing a sequence of vertices in the graph.

    This class is most easily accessed by the C{vs} field of the
    L{Graph} object, which returns an ordered sequence of all vertices in
    the graph. The vertex sequence can be refined by invoking the
    L{VertexSeq.select()} method. L{VertexSeq.select()} can also be
    accessed by simply calling the L{VertexSeq} object.

    An alternative way to create a vertex sequence referring to a given
    graph is to use the constructor directly:

      >>> g = Graph.Full(3)
      >>> vs = VertexSeq(g)
      >>> restricted_vs = VertexSeq(g, [0, 1])

    The individual vertices can be accessed by indexing the vertex sequence
    object. It can be used as an iterable as well, or even in a list
    comprehension:

      >>> g=Graph.Full(3)
      >>> for v in g.vs:
      ...   v["value"] = v.index ** 2
      ...
      >>> [v["value"] ** 0.5 for v in g.vs]
      [0.0, 1.0, 2.0]

    The vertex set can also be used as a dictionary where the keys are the
    attribute names. The values corresponding to the keys are the values
    of the given attribute for every vertex selected by the sequence.

      >>> g=Graph.Full(3)
      >>> for idx, v in enumerate(g.vs):
      ...   v["weight"] = idx*(idx+1)
      ...
      >>> g.vs["weight"]
      [0, 2, 6]
      >>> g.vs.select(1,2)["weight"] = [10, 20]
      >>> g.vs["weight"]
      [0, 10, 20]

    If you specify a sequence that is shorter than the number of vertices in
    the VertexSeq, the sequence is reused:

      >>> g = Graph.Tree(7, 2)
      >>> g.vs["color"] = ["red", "green"]
      >>> g.vs["color"]
      ['red', 'green', 'red', 'green', 'red', 'green', 'red']

    You can even pass a single string or integer, it will be considered as a
    sequence of length 1:

      >>> g.vs["color"] = "red"
      >>> g.vs["color"]
      ['red', 'red', 'red', 'red', 'red', 'red', 'red']

    Some methods of the vertex sequences are simply proxy methods to the
    corresponding methods in the L{Graph} object. One such example is
    C{VertexSeq.degree()}:

      >>> g=Graph.Tree(7, 2)
      >>> g.vs.degree()
      [2, 3, 3, 1, 1, 1, 1]
      >>> g.vs.degree() == g.degree()
      True
    """

    def attributes(self):
        """Returns the list of all the vertex attributes in the graph
        associated to this vertex sequence."""
        return self.graph.vertex_attributes()

    def find(self, *args, **kwds):
        """Returns the first vertex of the vertex sequence that matches some
        criteria.

        The selection criteria are equal to the ones allowed by L{VertexSeq.select}.
        See L{VertexSeq.select} for more details.

        For instance, to find the first vertex with name C{foo} in graph C{g}:

            >>> g.vs.find(name="foo")            #doctest:+SKIP

        To find an arbitrary isolated vertex:

            >>> g.vs.find(_degree=0)             #doctest:+SKIP
        """
        # Shortcut: if "name" is in kwds, there are no positional arguments,
        # and the specified name is a string, we try that first because that
        # attribute is indexed. Note that we cannot do this if name is an
        # integer, because it would then translate to g.vs.select(name), which
        # searches by _index_ if the argument is an integer
        if not args:
            if "name" in kwds:
                name = kwds.pop("name")
            elif "name_eq" in kwds:
                name = kwds.pop("name_eq")
            else:
                name = None

            if name is not None:
                if isinstance(name, str):
                    args = [name]
                else:
                    # put back what we popped
                    kwds["name"] = name

        if args:
            # Selecting first based on positional arguments, then checking
            # the criteria specified by the (remaining) keyword arguments
            vertex = _VertexSeq.find(self, *args)
            if not kwds:
                return vertex
            vs = self.graph.vs.select(vertex.index)
        else:
            vs = self

        # Selecting based on keyword arguments
        vs = vs.select(**kwds)
        if vs:
            return vs[0]
        raise ValueError("no such vertex")

    def select(self, *args, **kwds):
        """Selects a subset of the vertex sequence based on some criteria

        The selection criteria can be specified by the positional and the keyword
        arguments. Positional arguments are always processed before keyword
        arguments.

          - If the first positional argument is C{None}, an empty sequence is
            returned.

          - If the first positional argument is a callable object, the object
            will be called for every vertex in the sequence. If it returns
            C{True}, the vertex will be included, otherwise it will
            be excluded.

          - If the first positional argument is an iterable, it must return
            integers and they will be considered as indices of the current
            vertex set (NOT the whole vertex set of the graph -- the
            difference matters when one filters a vertex set that has
            already been filtered by a previous invocation of
            L{VertexSeq.select()}. In this case, the indices do not refer
            directly to the vertices of the graph but to the elements of
            the filtered vertex sequence.

          - If the first positional argument is an integer, all remaining
            arguments are expected to be integers. They are considered as
            indices of the current vertex set again.

        Keyword arguments can be used to filter the vertices based on their
        attributes. The name of the keyword specifies the name of the attribute
        and the filtering operator, they should be concatenated by an
        underscore (C{_}) character. Attribute names can also contain
        underscores, but operator names don't, so the operator is always the
        largest trailing substring of the keyword name that does not contain
        an underscore. Possible operators are:

          - C{eq}: equal to

          - C{ne}: not equal to

          - C{lt}: less than

          - C{gt}: greater than

          - C{le}: less than or equal to

          - C{ge}: greater than or equal to

          - C{in}: checks if the value of an attribute is in a given list

          - C{notin}: checks if the value of an attribute is not in a given
            list

        For instance, if you want to filter vertices with a numeric C{age}
        property larger than 200, you have to write:

          >>> g.vs.select(age_gt=200)                   #doctest: +SKIP

        Similarly, to filter vertices whose C{type} is in a list of predefined
        types:

          >>> list_of_types = ["HR", "Finance", "Management"]
          >>> g.vs.select(type_in=list_of_types)        #doctest: +SKIP

        If the operator is omitted, it defaults to C{eq}. For instance, the
        following selector selects vertices whose C{cluster} property equals
        to 2:

          >>> g.vs.select(cluster=2)                    #doctest: +SKIP

        In the case of an unknown operator, it is assumed that the
        recognized operator is part of the attribute name and the actual
        operator is C{eq}.

        Attribute names inferred from keyword arguments are treated specially
        if they start with an underscore (C{_}). These are not real attributes
        but refer to specific properties of the vertices, e.g., its degree.
        The rule is as follows: if an attribute name starts with an underscore,
        the rest of the name is interpreted as a method of the L{Graph} object.
        This method is called with the vertex sequence as its first argument
        (all others left at default values) and vertices are filtered
        according to the value returned by the method. For instance, if you
        want to exclude isolated vertices:

          >>> g = Graph.Famous("zachary")
          >>> non_isolated = g.vs.select(_degree_gt=0)

        For properties that take a long time to be computed (e.g., betweenness
        centrality for large graphs), it is advised to calculate the values
        in advance and store it in a graph attribute. The same applies when
        you are selecting based on the same property more than once in the
        same C{select()} call to avoid calculating it twice unnecessarily.
        For instance, the following would calculate betweenness centralities
        twice:

          >>> edges = g.vs.select(_betweenness_gt=10, _betweenness_lt=30)

        It is advised to use this instead:

          >>> g.vs["bs"] = g.betweenness()
          >>> edges = g.vs.select(bs_gt=10, bs_lt=30)

        @return: the new, filtered vertex sequence"""
        vs = _VertexSeq.select(self, *args)

        operators = {
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
            "eq": operator.eq,
            "ne": operator.ne,
            "in": lambda a, b: a in b,
            "notin": lambda a, b: a not in b,
        }
        for keyword, value in kwds.items():
            if "_" not in keyword or keyword.rindex("_") == 0:
                keyword += "_eq"
            attr, _, op = keyword.rpartition("_")
            try:
                func = operators[op]
            except KeyError:
                # No such operator, assume that it's part of the attribute name
                attr, op, func = keyword, "eq", operators["eq"]

            if attr[0] == "_":
                # Method call, not an attribute
                values = getattr(vs.graph, attr[1:])(vs)
            else:
                values = vs[attr]
            filtered_idxs = [i for i, v in enumerate(values) if func(v, value)]
            vs = vs.select(filtered_idxs)

        return vs

    def __call__(self, *args, **kwds):
        """Shorthand notation to select()

        This method simply passes all its arguments to L{VertexSeq.select()}.
        """
        return self.select(*args, **kwds)


class EdgeSeq(_EdgeSeq):
    """Class representing a sequence of edges in the graph.

    This class is most easily accessed by the C{es} field of the
    L{Graph} object, which returns an ordered sequence of all edges in
    the graph. The edge sequence can be refined by invoking the
    L{EdgeSeq.select()} method. L{EdgeSeq.select()} can also be
    accessed by simply calling the L{EdgeSeq} object.

    An alternative way to create an edge sequence referring to a given
    graph is to use the constructor directly:

      >>> g = Graph.Full(3)
      >>> es = EdgeSeq(g)
      >>> restricted_es = EdgeSeq(g, [0, 1])

    The individual edges can be accessed by indexing the edge sequence
    object. It can be used as an iterable as well, or even in a list
    comprehension:

      >>> g=Graph.Full(3)
      >>> for e in g.es:
      ...   print(e.tuple)
      ...
      (0, 1)
      (0, 2)
      (1, 2)
      >>> [max(e.tuple) for e in g.es]
      [1, 2, 2]

    The edge sequence can also be used as a dictionary where the keys are the
    attribute names. The values corresponding to the keys are the values
    of the given attribute of every edge in the graph:

      >>> g=Graph.Full(3)
      >>> for idx, e in enumerate(g.es):
      ...   e["weight"] = idx*(idx+1)
      ...
      >>> g.es["weight"]
      [0, 2, 6]
      >>> g.es["weight"] = range(3)
      >>> g.es["weight"]
      [0, 1, 2]

    If you specify a sequence that is shorter than the number of edges in
    the EdgeSeq, the sequence is reused:

      >>> g = Graph.Tree(7, 2)
      >>> g.es["color"] = ["red", "green"]
      >>> g.es["color"]
      ['red', 'green', 'red', 'green', 'red', 'green']

    You can even pass a single string or integer, it will be considered as a
    sequence of length 1:

      >>> g.es["color"] = "red"
      >>> g.es["color"]
      ['red', 'red', 'red', 'red', 'red', 'red']

    Some methods of the edge sequences are simply proxy methods to the
    corresponding methods in the L{Graph} object. One such example is
    C{EdgeSeq.is_multiple()}:

      >>> g=Graph(3, [(0,1), (1,0), (1,2)])
      >>> g.es.is_multiple()
      [False, True, False]
      >>> g.es.is_multiple() == g.is_multiple()
      True
    """

    def attributes(self):
        """Returns the list of all the edge attributes in the graph
        associated to this edge sequence."""
        return self.graph.edge_attributes()

    def find(self, *args, **kwds):
        """Returns the first edge of the edge sequence that matches some
        criteria.

        The selection criteria are equal to the ones allowed by L{VertexSeq.select}.
        See L{VertexSeq.select} for more details.

        For instance, to find the first edge with weight larger than 5 in graph C{g}:

            >>> g.es.find(weight_gt=5)           #doctest:+SKIP
        """
        if args:
            # Selecting first based on positional arguments, then checking
            # the criteria specified by the keyword arguments
            edge = _EdgeSeq.find(self, *args)
            if not kwds:
                return edge
            es = self.graph.es.select(edge.index)
        else:
            es = self

        # Selecting based on positional arguments
        es = es.select(**kwds)
        if es:
            return es[0]
        raise ValueError("no such edge")

    def select(self, *args, **kwds):
        """Selects a subset of the edge sequence based on some criteria

        The selection criteria can be specified by the positional and the
        keyword arguments. Positional arguments are always processed before
        keyword arguments.

          - If the first positional argument is C{None}, an empty sequence is
            returned.

          - If the first positional argument is a callable object, the object
            will be called for every edge in the sequence. If it returns
            C{True}, the edge will be included, otherwise it will
            be excluded.

          - If the first positional argument is an iterable, it must return
            integers and they will be considered as indices of the current
            edge set (NOT the whole edge set of the graph -- the
            difference matters when one filters an edge set that has
            already been filtered by a previous invocation of
            L{EdgeSeq.select()}. In this case, the indices do not refer
            directly to the edges of the graph but to the elements of
            the filtered edge sequence.

          - If the first positional argument is an integer, all remaining
            arguments are expected to be integers. They are considered as
            indices of the current edge set again.

        Keyword arguments can be used to filter the edges based on their
        attributes and properties. The name of the keyword specifies the name
        of the attribute and the filtering operator, they should be
        concatenated by an underscore (C{_}) character. Attribute names can
        also contain underscores, but operator names don't, so the operator is
        always the largest trailing substring of the keyword name that does not
        contain an underscore. Possible operators are:

          - C{eq}: equal to

          - C{ne}: not equal to

          - C{lt}: less than

          - C{gt}: greater than

          - C{le}: less than or equal to

          - C{ge}: greater than or equal to

          - C{in}: checks if the value of an attribute is in a given list

          - C{notin}: checks if the value of an attribute is not in a given
            list

        For instance, if you want to filter edges with a numeric C{weight}
        property larger than 50, you have to write:

          >>> g.es.select(weight_gt=50)            #doctest: +SKIP

        Similarly, to filter edges whose C{type} is in a list of predefined
        types:

          >>> list_of_types = ["inhibitory", "excitatory"]
          >>> g.es.select(type_in=list_of_types)   #doctest: +SKIP

        If the operator is omitted, it defaults to C{eq}. For instance, the
        following selector selects edges whose C{type} property is
        C{intracluster}:

          >>> g.es.select(type="intracluster")     #doctest: +SKIP

        In the case of an unknown operator, it is assumed that the
        recognized operator is part of the attribute name and the actual
        operator is C{eq}.

        Keyword arguments are treated specially if they start with an
        underscore (C{_}). These are not real attributes but refer to specific
        properties of the edges, e.g., their centrality.  The rules are as
        follows:

          1. C{_source} or {_from} means the source vertex of an edge. For
             undirected graphs, only the C{eq} operator is supported and it
             is treated as {_incident} (since undirected graphs have no notion
             of edge directionality).

          2. C{_target} or {_to} means the target vertex of an edge. For
             undirected graphs, only the C{eq} operator is supported and it
             is treated as {_incident} (since undirected graphs have no notion
             of edge directionality).

          3. C{_within} ignores the operator and checks whether both endpoints
             of the edge lie within a specified set.

          4. C{_between} ignores the operator and checks whether I{one}
             endpoint of the edge lies within a specified set and the I{other}
             endpoint lies within another specified set. The two sets must be
             given as a tuple.

          5. C{_incident} ignores the operator and checks whether the edge is
             incident on a specific vertex or a set of vertices.

          6. Otherwise, the rest of the name is interpreted as a method of the
             L{Graph} object. This method is called with the edge sequence as
             its first argument (all others left at default values) and edges
             are filtered according to the value returned by the method.

        For instance, if you want to exclude edges with a betweenness
        centrality less than 2:

          >>> g = Graph.Famous("zachary")
          >>> excl = g.es.select(_edge_betweenness_ge = 2)

        To select edges originating from vertices 2 and 4:

          >>> edges = g.es.select(_source_in = [2, 4])

        To select edges lying entirely within the subgraph spanned by vertices
        2, 3, 4 and 7:

          >>> edges = g.es.select(_within = [2, 3, 4, 7])

        To select edges with one endpoint in the vertex set containing vertices
        2, 3, 4 and 7 and the other endpoint in the vertex set containing
        vertices 8 and 9:

          >>> edges = g.es.select(_between = ([2, 3, 4, 7], [8, 9]))

        For properties that take a long time to be computed (e.g., betweenness
        centrality for large graphs), it is advised to calculate the values
        in advance and store it in a graph attribute. The same applies when
        you are selecting based on the same property more than once in the
        same C{select()} call to avoid calculating it twice unnecessarily.
        For instance, the following would calculate betweenness centralities
        twice:

          >>> edges = g.es.select(_edge_betweenness_gt=10,       # doctest:+SKIP
          ...                     _edge_betweenness_lt=30)

        It is advised to use this instead:

          >>> g.es["bs"] = g.edge_betweenness()
          >>> edges = g.es.select(bs_gt=10, bs_lt=30)

        @return: the new, filtered edge sequence
        """
        es = _EdgeSeq.select(self, *args)
        is_directed = self.graph.is_directed()

        def _ensure_set(value):
            if isinstance(value, VertexSeq):
                value = set(v.index for v in value)
            elif not isinstance(value, (set, frozenset)):
                value = set(value)
            return value

        operators = {
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
            "eq": operator.eq,
            "ne": operator.ne,
            "in": lambda a, b: a in b,
            "notin": lambda a, b: a not in b,
        }

        # TODO(ntamas): some keyword arguments should be prioritized over
        # others; for instance, we have optimized code paths for _source and
        # _target in directed and undirected graphs if es.is_all() is True;
        # these should be executed first. This matters only if there are
        # multiple keyword arguments and es.is_all() is True.

        for keyword, value in kwds.items():
            if "_" not in keyword or keyword.rindex("_") == 0:
                keyword += "_eq"
            pos = keyword.rindex("_")
            attr, op = keyword[0:pos], keyword[pos + 1 :]
            try:
                func = operators[op]
            except KeyError:
                # No such operator, assume that it's part of the attribute name
                attr, op, func = keyword, "eq", operators["eq"]

            if attr[0] == "_":
                if attr in ("_source", "_from", "_target", "_to") and not is_directed:
                    if op not in ("eq", "in"):
                        raise RuntimeError("unsupported for undirected graphs")

                    # translate to _incident to avoid confusion
                    attr = "_incident"
                    if func == operators["eq"]:
                        if hasattr(value, "__iter__") and not isinstance(value, str):
                            value = set(value)
                        else:
                            value = set([value])

                if attr in ("_source", "_from"):
                    if es.is_all() and op == "eq":
                        # shortcut here: use .incident() as it is much faster
                        filtered_idxs = sorted(es.graph.incident(value, mode="out"))
                        func = None
                        # TODO(ntamas): there are more possibilities; we could
                        # optimize "ne", "in" and "notin" in similar ways
                    else:
                        values = [e.source for e in es]
                        if op == "in" or op == "notin":
                            value = _ensure_set(value)

                elif attr in ("_target", "_to"):
                    if es.is_all() and op == "eq":
                        # shortcut here: use .incident() as it is much faster
                        filtered_idxs = sorted(es.graph.incident(value, mode="in"))
                        func = None
                        # TODO(ntamas): there are more possibilities; we could
                        # optimize "ne", "in" and "notin" in similar ways
                    else:
                        values = [e.target for e in es]
                        if op == "in" or op == "notin":
                            value = _ensure_set(value)

                elif attr == "_incident":
                    func = None  # ignoring function, filtering here
                    value = _ensure_set(value)

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in value:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those that are in the current edge sequence
                        filtered_idxs = [
                            i for i, e in enumerate(es) if e.index in candidates
                        ]
                    else:
                        # We are done, the filtered indexes are in the candidates set
                        filtered_idxs = sorted(candidates)

                elif attr == "_within":
                    func = None  # ignoring function, filtering here
                    value = _ensure_set(value)

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in value:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those where both endpoints are OK
                        filtered_idxs = [
                            i
                            for i, e in enumerate(es)
                            if e.index in candidates
                            and e.source in value
                            and e.target in value
                        ]
                    else:
                        # Optimized version when the edge sequence contains all
                        # the edges exactly once in increasing order of edge IDs
                        filtered_idxs = [
                            i
                            for i in candidates
                            if es[i].source in value and es[i].target in value
                        ]

                elif attr == "_between":
                    if len(value) != 2:
                        raise ValueError(
                            "_between selector requires two vertex ID lists"
                        )
                    func = None  # ignoring function, filtering here
                    set1 = _ensure_set(value[0])
                    set2 = _ensure_set(value[1])

                    # Fetch all the edges that are incident on at least one of
                    # the vertices specified
                    candidates = set()
                    for v in set1:
                        candidates.update(es.graph.incident(v))
                    for v in set2:
                        candidates.update(es.graph.incident(v))

                    if not es.is_all():
                        # Find those where both endpoints are OK
                        filtered_idxs = [
                            i
                            for i, e in enumerate(es)
                            if (e.source in set1 and e.target in set2)
                            or (e.target in set1 and e.source in set2)
                        ]
                    else:
                        # Optimized version when the edge sequence contains all
                        # the edges exactly once in increasing order of edge IDs
                        filtered_idxs = [
                            i
                            for i in candidates
                            if (es[i].source in set1 and es[i].target in set2)
                            or (es[i].target in set1 and es[i].source in set2)
                        ]

                else:
                    # Method call, not an attribute
                    values = getattr(es.graph, attr[1:])(es)
            else:
                values = es[attr]

            # If we have a function to apply on the values, do that; otherwise
            # we assume that filtered_idxs has already been calculated.
            if func is not None:
                filtered_idxs = [i for i, v in enumerate(values) if func(v, value)]

            es = es.select(filtered_idxs)

        return es

    def __call__(self, *args, **kwds):
        """Shorthand notation to select()

        This method simply passes all its arguments to L{EdgeSeq.select()}.
        """
        return self.select(*args, **kwds)


def _graphmethod(func=None, name=None):
    """Auxiliary decorator

    This decorator allows some methods of L{VertexSeq} and L{EdgeSeq} to
    call their respective counterparts in L{Graph} to avoid code duplication.

    @param func: the function being decorated. This function will be
      called on the results of the original L{Graph} method.
      If C{None}, defaults to the identity function.
    @param name: the name of the corresponding method in L{Graph}. If
      C{None}, it defaults to the name of the decorated function.
    @return: the decorated function
    """
    # Delay import to avoid cycles
    from igraph import Graph

    if name is None:
        name = func.__name__
    method = getattr(Graph, name)

    if hasattr(func, "__call__"):

        def decorated(*args, **kwds):
            self = args[0].graph
            return func(args[0], method(self, *args, **kwds))

    else:

        def decorated(*args, **kwds):
            self = args[0].graph
            return method(self, *args, **kwds)

    decorated.__name__ = name
    decorated.__doc__ = """Proxy method to L{Graph.%(name)s()}

This method calls the C{%(name)s()} method of the L{Graph} class
restricted to this sequence, and returns the result.

@see: Graph.%(name)s() for details.
""" % {
        "name": name
    }

    return decorated


def _add_proxy_methods():

    # Proxy methods for VertexSeq and EdgeSeq that forward their arguments to
    # the corresponding Graph method are constructed here. Proxy methods for
    # Vertex and Edge are added in the C source code. Make sure that you update
    # the C source whenever you add a proxy method here if that makes sense for
    # an individual vertex or edge
    decorated_methods = {}
    decorated_methods[VertexSeq] = [
        "degree",
        "betweenness",
        "bibcoupling",
        "closeness",
        "cocitation",
        "constraint",
        "distances",
        "diversity",
        "eccentricity",
        "get_shortest_paths",
        "maxdegree",
        "pagerank",
        "personalized_pagerank",
        "shortest_paths",
        "similarity_dice",
        "similarity_jaccard",
        "subgraph",
        "indegree",
        "outdegree",
        "isoclass",
        "delete_vertices",
        "is_separator",
        "is_minimal_separator",
    ]
    decorated_methods[EdgeSeq] = [
        "count_multiple",
        "delete_edges",
        "is_loop",
        "is_multiple",
        "is_mutual",
        "subgraph_edges",
    ]

    rename_methods = {}
    rename_methods[VertexSeq] = {"delete_vertices": "delete"}
    rename_methods[EdgeSeq] = {"delete_edges": "delete", "subgraph_edges": "subgraph"}

    for cls, methods in decorated_methods.items():
        for method in methods:
            new_method_name = rename_methods[cls].get(method, method)
            setattr(cls, new_method_name, _graphmethod(None, method))

    setattr(
        EdgeSeq,
        "edge_betweenness",
        _graphmethod(
            lambda self, result: [result[i] for i in self.indices], "edge_betweenness"
        ),
    )
