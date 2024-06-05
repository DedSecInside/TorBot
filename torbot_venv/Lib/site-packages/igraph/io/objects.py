from typing import Union, Sequence
from collections import defaultdict
from itertools import repeat
from warnings import warn

from igraph.datatypes import UniqueIdGenerator


def _construct_graph_from_dict_list(
    cls,
    vertices,
    edges,
    directed: bool = False,
    vertex_name_attr: str = "name",
    edge_foreign_keys=("source", "target"),
    iterative: bool = False,
):
    """Constructs a graph from a list-of-dictionaries representation.

    This function is useful when you have two lists of dictionaries, one for
    vertices and one for edges, each containing their attributes (e.g. name,
    weight). Of course, the edge dictionary must also contain two special keys
    that indicate the source and target vertices connected by that edge.
    Non-list iterables should work as long as they yield dictionaries or
    dict-like objects (they should have the 'items' and '__getitem__' methods).
    For instance, a database query result is likely to be fit as long as it's
    iterable and yields dict-like objects with every iteration.

    @param vertices: the list of dictionaries for the vertices or C{None} if
      there are no special attributes assigned to vertices and we
      should simply use the edge list of dicts to infer vertex names.
    @param edges: the list of dictionaries for the edges. Each dict must have
      at least the two keys specified by edge_foreign_keys to label the source
      and target vertices, while additional items will be treated as edge
      attributes.
    @param directed: whether the constructed graph will be directed
    @param vertex_name_attr: the name of the distinguished key in the
      dicts in the vertex data source that contains the vertex names.
      Ignored if C{vertices} is C{None}.
    @param edge_foreign_keys: tuple specifying the attributes in each edge
      dictionary that contain the source (1st) and target (2nd) vertex names.
      These items of each dictionary are also added as edge_attributes.
    @param iterative: whether to add the edges to the graph one by one,
      iteratively, or to build a large edge list first and use that to
      construct the graph. The latter approach is faster but it may
      not be suitable if your dataset is large. The default is to
      add the edges in a batch from an edge list.
    @return: the graph that was constructed

    Example:

    >>> vertices = [{'name': 'apple'}, {'name': 'pear'}, {'name': 'peach'}]
    >>> edges = [{'source': 'apple', 'target': 'pear', 'weight': 1.2},
    ...          {'source': 'apple', 'target': 'peach', 'weight': 0.9}]
    >>> g = Graph.DictList(vertices, edges)

    The graph has three vertices with names and two edges with weights.
    """

    def create_list_from_indices(indices, n):
        result = [None] * n
        for i, v in indices:
            result[i] = v
        return result

    # Construct the vertices
    vertex_attrs = {}
    n = 0
    if vertices:
        for idx, vertex_data in enumerate(vertices):
            for k, v in vertex_data.items():
                try:
                    vertex_attrs[k].append((idx, v))
                except KeyError:
                    vertex_attrs[k] = [(idx, v)]
            n += 1
        for k, v in vertex_attrs.items():
            vertex_attrs[k] = create_list_from_indices(v, n)
    else:
        vertex_attrs[vertex_name_attr] = []

    if vertex_name_attr not in vertex_attrs:
        raise AttributeError(
            f"{vertex_name_attr} is not a key of your vertex dictionaries",
        )
    vertex_names = vertex_attrs[vertex_name_attr]

    # Check for duplicates in vertex_names
    if len(vertex_names) != len(set(vertex_names)):
        raise ValueError("vertex names are not unique")
    # Create a reverse mapping from vertex names to indices
    vertex_name_map = UniqueIdGenerator(initial=vertex_names)

    # Construct the edges
    efk_src, efk_dest = edge_foreign_keys
    if iterative:
        g = cls(n, [], directed, {}, vertex_attrs)
        for idx, edge_data in enumerate(edges):
            src_name = edge_data[efk_src]
            dst_name = edge_data[efk_dest]
            v1 = vertex_name_map[src_name]
            if v1 == n:
                g.add_vertices(1)
                g.vs[n][vertex_name_attr] = src_name
                n += 1
            v2 = vertex_name_map[dst_name]
            if v2 == n:
                g.add_vertices(1)
                g.vs[n][vertex_name_attr] = dst_name
                n += 1
            g.add_edge(v1, v2)
            for k, v in edge_data.items():
                g.es[idx][k] = v

        return g
    else:
        edge_list = []
        edge_attrs = {}
        m = 0
        for idx, edge_data in enumerate(edges):
            v1 = vertex_name_map[edge_data[efk_src]]
            v2 = vertex_name_map[edge_data[efk_dest]]

            edge_list.append((v1, v2))
            for k, v in edge_data.items():
                try:
                    edge_attrs[k].append((idx, v))
                except KeyError:
                    edge_attrs[k] = [(idx, v)]
            m += 1
        for k, v in edge_attrs.items():
            edge_attrs[k] = create_list_from_indices(v, m)

        # It may have happened that some vertices were added during
        # the process
        if len(vertex_name_map) > n:
            diff = len(vertex_name_map) - n
            more = [None] * diff
            for k, v in vertex_attrs.items():
                v.extend(more)
            vertex_attrs[vertex_name_attr] = list(vertex_name_map.values())
            n = len(vertex_name_map)

        # Create the graph
        return cls(n, edge_list, directed, {}, vertex_attrs, edge_attrs)


def _construct_graph_from_tuple_list(
    cls,
    edges,
    directed: bool = False,
    vertex_name_attr: str = "name",
    edge_attrs=None,
    weights=False,
):
    """Constructs a graph from a list-of-tuples representation.

    This representation assumes that the edges of the graph are encoded
    in a list of tuples (or lists). Each item in the list must have at least
    two elements, which specify the source and the target vertices of the edge.
    The remaining elements (if any) specify the edge attributes of that edge,
    where the names of the edge attributes originate from the C{edge_attrs}
    list. The names of the vertices will be stored in the vertex attribute
    given by C{vertex_name_attr}.

    The default parameters of this function are suitable for creating
    unweighted graphs from lists where each item contains the source vertex
    and the target vertex. If you have a weighted graph, you can use items
    where the third item contains the weight of the edge by setting
    C{edge_attrs} to C{"weight"} or C{["weight"]}. If you have even more
    edge attributes, add them to the end of each item in the C{edges}
    list and also specify the corresponding edge attribute names in
    C{edge_attrs} as a list.

    @param edges: the data source for the edges. This must be a list
      where each item is a tuple (or list) containing at least two
      items: the name of the source and the target vertex. Note that
      names will be assigned to the C{name} vertex attribute (or another
      vertex attribute if C{vertex_name_attr} is specified), even if
      all the vertex names in the list are in fact numbers.
    @param directed: whether the constructed graph will be directed
    @param vertex_name_attr: the name of the vertex attribute that will
      contain the vertex names.
    @param edge_attrs: the names of the edge attributes that are filled
      with the extra items in the edge list (starting from index 2, since
      the first two items are the source and target vertices). If C{None}
      or an empty sequence, only the source and target vertices will be
      extracted and additional tuple items will be ignored. If a string, it is
      interpreted as a single edge attribute.
    @param weights: alternative way to specify that the graph is
      weighted. If you set C{weights} to C{true} and C{edge_attrs} is
      not given, it will be assumed that C{edge_attrs} is C{["weight"]}
      and igraph will parse the third element from each item into an
      edge weight. If you set C{weights} to a string, it will be assumed
      that C{edge_attrs} contains that string only, and igraph will
      store the edge weights in that attribute.
    @return: the graph that was constructed
    """
    if edge_attrs is None:
        if not weights:
            edge_attrs = ()
        else:
            if not isinstance(weights, str):
                weights = "weight"
            edge_attrs = [weights]
    else:
        if weights:
            raise ValueError("`weights` must be False if `edge_attrs` is " "not None")

    if isinstance(edge_attrs, str):
        edge_attrs = [edge_attrs]

    # Set up a vertex ID generator
    idgen = UniqueIdGenerator()

    # Construct the edges and the edge attributes
    edge_list = []
    edge_attributes = {}
    for name in edge_attrs:
        edge_attributes[name] = []

    for item in edges:
        edge_list.append((idgen[item[0]], idgen[item[1]]))
        for index, name in enumerate(edge_attrs, 2):
            try:
                edge_attributes[name].append(item[index])
            except IndexError:
                edge_attributes[name].append(None)

    # Set up the name vertex attribute
    vertex_attributes = {}
    vertex_attributes[vertex_name_attr] = list(idgen.values())
    n = len(idgen)

    # Construct the graph
    return cls(n, edge_list, directed, {}, vertex_attributes, edge_attributes)


def _construct_graph_from_list_dict(
    cls,
    edges,
    directed: bool = False,
    vertex_name_attr: str = "name",
):
    """Constructs a graph from a dict-of-lists representation.

    This function is used to construct a graph from a dictionary of
    lists. Other, non-list sequences (e.g. tuples) and lazy iterators are
    are accepted. For each key x, its corresponding value must be a sequence of
    multiple values y: the edge (x,y) will be created in the graph. x and y
    must be either one of:

      - two integers: the vertices with those ids will be connected
      - two strings: the vertices with those names will be connected

    If names are used, the order of vertices is not guaranteed, and each
    vertex will be given the vertex_name_attr attribute.

    @param edges: the dict of sequences describing the edges
    @param directed: whether to create a directed graph
    @param vertex_name_attr: vertex attribute that will store the names

    @returns: a Graph object

    Example:

    >>> mydict = {'apple': ['pear', 'peach'], 'pear': ['peach']}
    >>> g = Graph.ListDict(mydict)

    # The graph has three vertices with names and three edges connecting
    # each pair.
    """
    first_item = next(iter(edges), 0)

    if not isinstance(first_item, (int, str)):
        raise ValueError("Keys must be integers or strings")

    vertex_attributes = {}
    if isinstance(first_item, str):
        name_map = UniqueIdGenerator()
        edge_list = []
        for source, sequence in edges.items():
            source_id = name_map[source]
            edge_list.extend((source_id, name_map[target]) for target in sequence)
        vertex_attributes[vertex_name_attr] = name_map.values()
        n = len(name_map)

    else:
        edge_list = []
        n = -1
        for source, sequence in edges.items():
            n = max(n, source, *sequence)
            edge_list.extend(zip(repeat(source), sequence))
        n += 1

    # Construct the graph
    return cls(n, edge_list, directed, {}, vertex_attributes, {})


def _construct_graph_from_dict_dict(
    cls,
    edges,
    directed: bool = False,
    vertex_name_attr: str = "name",
):
    """Constructs a graph from a dict-of-dicts representation.

    Each key can be an integer or a string and represent a vertex. Each value
    is a dict representing edges (outgoing if the graph is directed) from that
    vertex. Each dict key is an integer/string for a target vertex, such that
    an edge will be created between those two vertices. Integers are
    interpreted as vertex_ids from 0 (as used in igraph), strings are
    interpreted as vertex names, in which case vertices are given separate
    numeric ids. Each value is a dictionary of edge attributes for that edge.

    Example:

      >>> {'Alice': {'Bob': {'weight': 1.5}, 'David': {'weight': 2}}}

    creates a graph with three vertices (Alice, Bob, and David) and two edges:

      - Alice - Bob (with weight 1.5)
      - Alice - David (with weight 2)

    @param edges: the dict of dict of dicts specifying the edges and their
      attributes
    @param directed: whether to create a directed graph
    @param vertex_name_attr: vertex attribute that will store the names

    @returns: a Graph object
    """
    first_item = next(iter(edges), 0)

    if not isinstance(first_item, (int, str)):
        raise ValueError("Keys must be integers or strings")

    vertex_attributes = {}
    edge_attribute_list = []
    if isinstance(first_item, str):
        name_map = UniqueIdGenerator()
        edge_list = []
        for source, target_dict in edges.items():
            source_id = name_map[source]
            for target, edge_attrs in target_dict.items():
                edge_list.append((source_id, name_map[target]))
                edge_attribute_list.append(edge_attrs)
        vertex_attributes[vertex_name_attr] = name_map.values()
        n = len(name_map)

    else:
        edge_list = []
        n = -1
        for source, target_dict in edges.items():
            n = max(n, source, *target_dict)
            for target, edge_attrs in target_dict.items():
                edge_list.append((source, target))
                edge_attribute_list.append(edge_attrs)
        n += 1

    # Construct graph without edge attributes
    graph = cls(n, edge_list, directed, {}, vertex_attributes, {})

    # Add edge attributes
    for edge, edge_attrs in zip(graph.es, edge_attribute_list):
        for key, val in edge_attrs.items():
            edge[key] = val

    return graph


def _construct_graph_from_dataframe(
    cls,
    edges,
    directed: bool = True,
    vertices=None,
    use_vids: bool = True,
):
    """Generates a graph from one or two dataframes.

    @param edges: pandas DataFrame containing edges and metadata. The first
      two columns of this DataFrame contain the source and target vertices
      for each edge. These indicate the vertex IDs as nonnegative integers
      rather than vertex names unless C{use_vids} is False. Further columns
      may contain edge attributes.
    @param directed: whether the graph is directed
    @param vertices: None (default) or pandas DataFrame containing vertex
      metadata. The DataFrame's index must contain the vertex IDs as a
      sequence of intergers from 0 to C{len(vertices) - 1}. If C{use_vids}
      is C{False}, the first column must contain the unique vertex names.
      Vertex names should be strings for full compatibility, but many functions
      will work if you set the name with any hashable object. All other columns
      will be added as vertex attributes by column name.
    @param use_vids: whether to interpret the first two columns of the C{edges}
      argument as vertex ids (0-based integers) instead of vertex names.
      If this argument is set to True and the first two columns of C{edges}
      are not integers, an error is thrown.

    @return: the graph

    Vertex names in either the C{edges} or C{vertices} arguments that are set
    to NaN (not a number) will be set to the string "NA". That might lead
    to unexpected behaviour: fill your NaNs with values before calling this
    function to mitigate.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("You should install pandas in order to use this function")
    try:
        import numpy as np
    except ImportError:
        raise ImportError("You should install numpy in order to use this function")

    if edges.shape[1] < 2:
        raise ValueError("The 'edges' DataFrame must contain at least two columns")
    if vertices is not None and vertices.shape[1] < 1:
        raise ValueError("The 'vertices' DataFrame must contain at least one column")

    if use_vids:
        if (
            str(edges.dtypes[0]).startswith(("int", "Int"))
            and str(edges.dtypes[1]).startswith(("int", "Int"))
        ):
            # Check pandas nullable integer data type:
            # https://pandas.pydata.org/docs/user_guide/integer_na.html
            if (edges.iloc[:, :2].isna()).any(axis=None):
                 raise ValueError("Source and target IDs must not be null")

            if (edges.iloc[:, :2] < 0).any(axis=None):
                 raise ValueError("Source and target IDs must not be negative")
        else:
            raise TypeError(
                f"Source and target IDs must be 0-based integers, found types {edges.dtypes.tolist()[:2]}"
            )

        if vertices is not None:
            vertices = vertices.sort_index()
            if not vertices.index.equals(
                pd.RangeIndex.from_range(range(vertices.shape[0]))
            ):
                if not str(vertices.index.dtype).startswith("int"):
                    raise TypeError(
                        f"Vertex IDs must be 0-based integers, found type {vertices.index.dtype}"
                    )
                elif (vertices.index < 0).any(axis=None):
                    raise ValueError("Vertex IDs must not be negative")
                else:
                    raise ValueError(
                        f"Vertex IDs must be an integer sequence from 0 to {vertices.shape[0] - 1}"
                    )
    else:
        # Handle if some source and target names in 'edges' are 'NA'
        if edges.iloc[:, :2].isna().any(axis=None):
            warn(
                "In the first two columns of 'edges' NA elements were replaced with string \"NA\""
            )
            edges = edges.copy()
            edges.iloc[:, :2].fillna("NA", inplace=True)

        # Bring DataFrame(s) into same format as with 'use_vids=True'
        if vertices is None:
            vertices = pd.DataFrame({"name": pd.unique(edges.values[:, :2].ravel())})

        if vertices.iloc[:, 0].isna().any():
            warn(
                "In the first column of 'vertices' NA elements were replaced with string \"NA\""
            )
            vertices = vertices.copy()
            vertices.iloc[:, 0].fillna("NA", inplace=True)

        if vertices.iloc[:, 0].duplicated().any():
            raise ValueError("Vertex names must be unique")

        if vertices.shape[1] > 1 and "name" in vertices.columns[1:]:
            raise ValueError(
                "Vertex attribute conflict: DataFrame already contains column 'name'"
            )

        vertices = vertices.rename({vertices.columns[0]: "name"}, axis=1).reset_index(
            drop=True
        )

        # Map source and target names in 'edges' to IDs
        vid_map = pd.Series(vertices.index, index=vertices.iloc[:, 0])
        edges = edges.copy()
        edges[edges.columns[0]] = edges.iloc[:, 0].map(vid_map)
        edges[edges.columns[1]] = edges.iloc[:, 1].map(vid_map)

    # Create graph
    if vertices is None:
        nv = edges.iloc[:, :2].max().max() + 1
        g = cls(n=nv, directed=directed)
    else:
        if not edges.iloc[:, :2].isin(vertices.index).all(axis=None):
            raise ValueError(
                "Some vertices in the edge DataFrame are missing from vertices DataFrame"
            )
        nv = vertices.shape[0]
        g = cls(n=nv, directed=directed)
        # Add vertex attributes
        for col in vertices.columns:
            g.vs[col] = vertices[col].tolist()

    # add edges including optional attributes
    e_list = list(edges.iloc[:, :2].itertuples(index=False, name=None))
    e_attr = edges.iloc[:, 2:].to_dict(orient="list") if edges.shape[1] > 2 else None
    g.add_edges(e_list, e_attr)

    return g


def _export_graph_to_dict_list(
    graph,
    use_vids: bool = True,
    skip_none: bool = False,
    vertex_name_attr: str = "name",
):
    """Export graph as two lists of dictionaries, for vertices and edges.

    This function is the reverse of Graph.DictList.

    Example:

      >>> g = Graph([(0, 1), (1, 2)])
      >>> g.vs["name"] = ["apple", "pear", "peach"]
      >>> g.es["name"] = ["first_edge", "second"]

      >>> g.to_dict_list()
      ([{"name": "apple"}, {"name": "pear"}, {"name": "peach"}],
       [{"source": 0, "target": 1, "name": "first_edge"},
        {"source" 0, "target": 2, name": "second"}])

      >>> g.to_dict_list(use_vids=False)
      ([{"name": "apple"}, {"name": "pear"}, {"name": "peach"}],
       [{"source": "apple", "target": "pear", "name": "first_edge"},
        {"source" "apple", "target": "peach", name": "second"}])

    @param use_vids: whether to label vertices in the output data
      structure by their ids or their vertex_name_attr attribute. If
      use_vids=False but vertices lack a vertex_name_attr attribute, an
      AttributeError is raised.
    @param skip_none: whether to skip, for each edge, attributes that
      have a value of None. This is useful if only some edges are expected to
      possess an attribute.
    @param vertex_name_attr: only used with use_vids=False to choose what
      vertex attribute to use to name your vertices in the output data
      structure.

    @return: a tuple with two lists of dictionaries, representing the vertices
      and the edges, respectively, with their attributes.
    """
    # Output data structures
    res_vs, res_es = [], []

    if not use_vids:
        if vertex_name_attr not in graph.vertex_attributes():
            raise AttributeError(f"No vertex attribute {vertex_name_attr}")

        vs_names = graph.vs[vertex_name_attr]

    for vertex in graph.vs:
        if skip_none:
            attrdic = {k: v for k, v in vertex.attributes() if v is not None}
        else:
            attrdic = vertex.attributes()
        res_vs.append(attrdic)

    for edge in graph.es:
        source, target = edge.tuple
        if not use_vids:
            source, target = vs_names[source], vs_names[target]
        if skip_none:
            attrdic = {k: v for k, v in edge.attributes() if v is not None}
        else:
            attrdic = edge.attributes()

        attrdic["source"] = source
        attrdic["target"] = target
        res_es.append(attrdic)

    return (res_vs, res_es)


def _export_graph_to_tuple_list(
    graph,
    use_vids: bool = True,
    edge_attrs: Union[str, Sequence[str]] = None,
    vertex_name_attr: str = "name",
):
    """Export graph to a list of edge tuples

    This function is the reverse of Graph.TupleList.

    Example:

      >>> g = Graph.Full(3)
      >>> g.vs["name"] = ["apple", "pear", "peach"]
      >>> g.es["name"] = ["first_edge", "second", "third"]

      >>> # Get name of the edge
      >>> g.to_tuple_list(edge_attrs=["name"])
      [(0, 1, "first_edge"), (0, 2, "second"), (1, 2, "third")]

      >>> # Use vertex names, no edge attributes
      >>> g.to_tuple_list(use_vids=False)
      [("apple", "pear"), ("apple", "peach"), ("pear", "peach")]

    @param use_vids: whether to label vertices in the output data
      structure by their ids or their vertex_name_attr attribute. If
      use_vids=False but vertices lack a vertex_name_attr attribute, an
      AttributeError is raised.
    @param edge_attrs: list of edge attributes to export
      in addition to source and target vertex, which are always the first two
      elements of each tuple. None (default) is equivalent to an empty list. A
      string is acceptable to signify a single attribute and will be wrapped in
      a list internally.
    @param vertex_name_attr: only used with use_vids=False to choose what
      vertex attribute to use to name your vertices in the output data
      structure.

    @return: a list of tuples, each representing an edge of the graph.
    """
    # Output data structure
    res = []

    if edge_attrs is not None:
        if isinstance(edge_attrs, str):
            edge_attrs = [edge_attrs]
        missing_attrs = list(set(edge_attrs) - set(graph.edge_attributes()))
        if missing_attrs:
            raise AttributeError(f"Missing attributes: {missing_attrs}")
    else:
        edge_attrs = []

    if use_vids is False:
        if vertex_name_attr not in graph.vertex_attributes():
            raise AttributeError(f"No vertex attribute {vertex_name_attr}")

        vs_names = graph.vs[vertex_name_attr]

    for edge in graph.es:
        source, target = edge.tuple
        if not use_vids:
            source, target = vs_names[source], vs_names[target]
        attrlist = [source, target]
        attrlist += [edge[attrname] for attrname in edge_attrs]
        res.append(tuple(attrlist))

    return res


def _export_graph_to_list_dict(
    graph,
    use_vids: bool = True,
    sequence_constructor: callable = list,
    vertex_name_attr: str = "name",
):
    """Export graph to a dictionary of lists (or other sequences).

    This function is the reverse of Graph.ListDict.

    Example:

      >>> g = Graph.Full(3)
      >>> g.to_sequence_dict() -> {0: [1, 2], 1: [2]}
      >>> g.to_sequence_dict(sequence_constructor=tuple) -> {0: (1, 2), 1: (2,)}
      >>> g.vs['name'] = ['apple', 'pear', 'peach']
      >>> g.to_sequence_dict(use_vids=False)
      {'apple': ['pear', 'peach'], 'pear': ['peach']}

    @param use_vids: whether to label vertices in the output data
      structure by their ids or their vertex_name_attr attribute. If
      use_vids=False but vertices lack a vertex_name_attr attribute, an
      AttributeError is raised.
    @param sequence_constructor: constructor for the data structure
      to be used as values of the dictionary. The default (list) makes a dict
      of lists, with each list representing the neighbors of the vertex
      specified in the respective dictionary key.
    @param vertex_name_attr: only used with use_vids=False to choose what
      vertex attribute to use to name your vertices in the output data
      structure.

    @return: dictionary of sequences, keyed by vertices, with each value
      containing the neighbors of that vertex.
    """
    if not use_vids:
        if vertex_name_attr not in graph.vertex_attributes():
            raise AttributeError(f"Vertices do not have a {vertex_name_attr} attribute")
        vs_names = graph.vs[vertex_name_attr]

    # Temporary output data structure
    res = defaultdict(list)

    for edge in graph.es:
        source, target = edge.tuple

        if not use_vids:
            source = vs_names[source]
            target = vs_names[target]

        res[source].append(target)

    res = {key: sequence_constructor(val) for key, val in res.items()}
    return res


def _export_graph_to_dict_dict(
    graph,
    use_vids: bool = True,
    edge_attrs: Union[str, Sequence[str]] = None,
    skip_none: bool = False,
    vertex_name_attr: str = "name",
):
    """Export graph to dictionary of dicts of edge attributes

    This function is the reverse of Graph.DictDict.

    Example:

      >>> g = Graph.Full(3)
      >>> g.es['name'] = ['first_edge', 'second', 'third']
      >>> g.to_dict_dict()
      {0: {1: {'name': 'first_edge'}, 2: {'name': 'second'}}, 1: {2: {'name': 'third'}}}

    @param use_vids: whether to label vertices in the output data
      structure by their ids or their vertex_name_attr attribute. If
      use_vids=False but vertices lack a vertex_name_attr attribute, an
      AttributeError is raised.
    @param edge_attrs: list of edge attributes to export.
      None (default) signified all attributes (unlike Graph.to_tuple_list). A
      string is acceptable to signify a single attribute and will be wrapped
      in a list internally.
    @param skip_none: whether to skip, for each edge, attributes that
      have a value of None. This is useful if only some edges are expected to
      possess an attribute.
    @param vertex_name_attr: only used with use_vids=False to choose what
      vertex attribute to use to name your vertices in the output data
      structure.

    @return: dictionary of dictionaries of dictionaries, with the outer keys
      vertex ids/names, the middle keys ids/names of their neighbors, and the
      innermost dictionary representing attributes of that edge.
    """
    if edge_attrs is not None:
        if isinstance(edge_attrs, str):
            edge_attrs = [edge_attrs]
        missing_attrs = list(set(edge_attrs) - set(graph.edge_attributes()))
        if missing_attrs:
            raise AttributeError(f"Missing attributes: {missing_attrs}")

    if not use_vids:
        if vertex_name_attr not in graph.vertex_attributes():
            raise AttributeError(f"Vertices do not have a {vertex_name_attr} attribute")
        vs_names = graph.vs[vertex_name_attr]

    # Temporary output data structure
    res = defaultdict(lambda: defaultdict(dict))

    for edge in graph.es:
        source, target = edge.tuple

        if not use_vids:
            source = vs_names[source]
            target = vs_names[target]

        attrdic = edge.attributes()
        if edge_attrs is not None:
            attrdic = {k: attrdic[k] for k in edge_attrs}
        if skip_none:
            attrdic = {k: v for k, v in attrdic.items() if v is not None}

        res[source][target] = attrdic

    res = {key: dict(val) for key, val in res.items()}
    return res


def _export_vertex_dataframe(graph):
    """Export vertices with attributes to pandas.DataFrame

    If you want to use vertex names as index, you can do:

    >>> from string import ascii_letters
    >>> graph = Graph.GRG(25, 0.4)
    >>> graph.vs["name"] = ascii_letters[:graph.vcount()]
    >>> df = graph.get_vertex_dataframe()
    >>> df.set_index('name', inplace=True)

    @return: a pandas.DataFrame representing vertices and their attributes.
      The index uses vertex IDs, from 0 to N - 1 where N is the number of
      vertices.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("You should install pandas in order to use this function")

    df = pd.DataFrame(
        {attr: graph.vs[attr] for attr in graph.vertex_attributes()},
        index=list(range(graph.vcount())),
    )
    df.index.name = "vertex ID"

    return df


def _export_edge_dataframe(graph):
    """Export edges with attributes to pandas.DataFrame

    If you want to use source and target vertex IDs as index, you can do:

    >>> from string import ascii_letters
    >>> graph = Graph.GRG(25, 0.4)
    >>> graph.vs["name"] = ascii_letters[:graph.vcount()]
    >>> df = graph.get_edge_dataframe()
    >>> df.set_index(['source', 'target'], inplace=True)

    The index will be a pandas.MultiIndex. You can use the C{drop=False}
    option to keep the C{source} and C{target} columns.

    If you want to use vertex names in the source and target columns:

    >>> df = graph.get_edge_dataframe()
    >>> df_vert = graph.get_vertex_dataframe()
    >>> df['source'].replace(df_vert['name'], inplace=True)
    >>> df['target'].replace(df_vert['name'], inplace=True)
    >>> df_vert.set_index('name', inplace=True)  # Optional

    @return: a pandas.DataFrame representing edges and their attributes.
      The index uses edge IDs, from 0 to M - 1 where M is the number of
      edges. The first two columns of the dataframe represent the IDs of
      source and target vertices for each edge. These columns have names
      "source" and "target". If your edges have attributes with the same
      names, they will be present in the dataframe, but not in the first
      two columns.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("You should install pandas in order to use this function")

    df = pd.DataFrame(
        {attr: graph.es[attr] for attr in graph.edge_attributes()},
        index=list(range(graph.ecount())),
    )
    df.index.name = "edge ID"

    df.insert(0, "source", [e.source for e in graph.es], allow_duplicates=True)
    df.insert(1, "target", [e.target for e in graph.es], allow_duplicates=True)

    return df
