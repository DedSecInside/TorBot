"""
igraph library.
"""


__license__ = """
Copyright (C) 2006- The igraph development team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc.,  51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 USA
"""

from igraph._igraph import (
    ADJ_DIRECTED,
    ADJ_LOWER,
    ADJ_MAX,
    ADJ_MIN,
    ADJ_PLUS,
    ADJ_UNDIRECTED,
    ADJ_UPPER,
    ALL,
    ARPACKOptions,
    BFSIter,
    BLISS_F,
    BLISS_FL,
    BLISS_FLM,
    BLISS_FM,
    BLISS_FS,
    BLISS_FSM,
    DFSIter,
    Edge,
    GET_ADJACENCY_BOTH,
    GET_ADJACENCY_LOWER,
    GET_ADJACENCY_UPPER,
    GraphBase,
    IN,
    InternalError,
    OUT,
    REWIRING_SIMPLE,
    REWIRING_SIMPLE_LOOPS,
    STAR_IN,
    STAR_MUTUAL,
    STAR_OUT,
    STAR_UNDIRECTED,
    STRONG,
    TRANSITIVITY_NAN,
    TRANSITIVITY_ZERO,
    TREE_IN,
    TREE_OUT,
    TREE_UNDIRECTED,
    Vertex,
    WEAK,
    arpack_options as default_arpack_options,
    community_to_membership,
    convex_hull,
    is_degree_sequence,
    is_graphical,
    is_graphical_degree_sequence,
    set_progress_handler,
    set_random_number_generator,
    set_status_handler,
    umap_compute_weights,
    __igraph_version__,
)
from igraph.adjacency import (
    _get_adjacency,
    _get_adjacency_sparse,
    _get_adjlist,
    _get_biadjacency,
    _get_inclist,
)
from igraph.automorphisms import (
    _count_automorphisms_vf2,
    _get_automorphisms_vf2,
)
from igraph.basic import (
    _add_edge,
    _add_edges,
    _add_vertex,
    _add_vertices,
    _delete_edges,
    _clear,
    _as_directed,
    _as_undirected,
)
from igraph.bipartite import (
    _maximum_bipartite_matching,
    _bipartite_projection,
    _bipartite_projection_size,
)
from igraph.community import (
    _community_fastgreedy,
    _community_infomap,
    _community_leading_eigenvector,
    _community_label_propagation,
    _community_multilevel,
    _community_optimal_modularity,
    _community_edge_betweenness,
    _community_spinglass,
    _community_walktrap,
    _k_core,
    _community_leiden,
    _modularity,
)
from igraph.clustering import (
    Clustering,
    VertexClustering,
    Dendrogram,
    VertexDendrogram,
    Cover,
    VertexCover,
    CohesiveBlocks,
    compare_communities,
    split_join_distance,
    _biconnected_components,
    _cohesive_blocks,
    _connected_components,
    _clusters,
)
from igraph.cut import (
    Cut,
    Flow,
    _all_st_cuts,
    _all_st_mincuts,
    _gomory_hu_tree,
    _maxflow,
    _mincut,
    _st_mincut,
)
from igraph.configuration import Configuration, init as init_configuration
from igraph.drawing import (
    BoundingBox,
    CairoGraphDrawer,
    DefaultGraphDrawer,
    MatplotlibGraphDrawer,
    Plot,
    Point,
    Rectangle,
    plot,
)
from igraph.drawing.colors import (
    Palette,
    GradientPalette,
    AdvancedGradientPalette,
    RainbowPalette,
    PrecalculatedPalette,
    ClusterColoringPalette,
    color_name_to_rgb,
    color_name_to_rgba,
    hsv_to_rgb,
    hsva_to_rgba,
    hsl_to_rgb,
    hsla_to_rgba,
    rgb_to_hsv,
    rgba_to_hsva,
    rgb_to_hsl,
    rgba_to_hsla,
    palettes,
    known_colors,
)
from igraph.drawing.graph import __plot__ as _graph_plot
from igraph.drawing.utils import autocurve
from igraph.datatypes import Matrix, DyadCensus, TriadCensus, UniqueIdGenerator
from igraph.formula import construct_graph_from_formula
from igraph.io import _format_mapping
from igraph.io.files import (
    _construct_graph_from_graphmlz_file,
    _construct_graph_from_dimacs_file,
    _construct_graph_from_pickle_file,
    _construct_graph_from_picklez_file,
    _construct_graph_from_adjacency_file,
    _construct_graph_from_file,
    _write_graph_to_adjacency_file,
    _write_graph_to_dimacs_file,
    _write_graph_to_graphmlz_file,
    _write_graph_to_pickle_file,
    _write_graph_to_picklez_file,
    _write_graph_to_file,
)
from igraph.io.objects import (
    _construct_graph_from_dict_list,
    _export_graph_to_dict_list,
    _construct_graph_from_tuple_list,
    _export_graph_to_tuple_list,
    _construct_graph_from_list_dict,
    _export_graph_to_list_dict,
    _construct_graph_from_dict_dict,
    _export_graph_to_dict_dict,
    _construct_graph_from_dataframe,
    _export_vertex_dataframe,
    _export_edge_dataframe,
)
from igraph.io.adjacency import (
    _construct_graph_from_adjacency,
    _construct_graph_from_weighted_adjacency,
)
from igraph.io.libraries import (
    _construct_graph_from_networkx,
    _export_graph_to_networkx,
    _construct_graph_from_graph_tool,
    _export_graph_to_graph_tool,
)
from igraph.io.random import (
    _construct_random_geometric_graph,
)
from igraph.io.bipartite import (
    _construct_bipartite_graph,
    _construct_bipartite_graph_from_adjacency,
    _construct_full_bipartite_graph,
    _construct_random_bipartite_graph,
)
from igraph.io.images import _write_graph_to_svg
from igraph.layout import (
    Layout,
    _layout,
    _layout_auto,
    _layout_sugiyama,
    _layout_method_wrapper,
    _3d_version_for,
    _layout_mapping,
)
from igraph.matching import Matching
from igraph.operators import (
    disjoint_union,
    union,
    intersection,
    operator_method_registry as _operator_method_registry,
)
from igraph.seq import EdgeSeq, VertexSeq, _add_proxy_methods
from igraph.statistics import (
    FittedPowerLaw,
    Histogram,
    RunningMean,
    mean,
    median,
    percentile,
    quantile,
    power_law_fit,
)
from igraph.structural import (
    _indegree,
    _outdegree,
    _degree_distribution,
    _pagerank,
    _shortest_paths
)
from igraph.summary import GraphSummary, summary
from igraph.utils import (
    deprecated,
    numpy_to_contiguous_memoryview,
    rescale,
)
from igraph.version import __version__, __version_info__

import os
import sys


class Graph(GraphBase):
    """Generic graph.

    This class is built on top of L{GraphBase}, so the order of the
    methods in the generated API documentation is a little bit obscure:
    inherited methods come after the ones implemented directly in the
    subclass. L{Graph} provides many functions that L{GraphBase} does not,
    mostly because these functions are not speed critical and they were
    easier to implement in Python than in pure C. An example is the
    attribute handling in the constructor: the constructor of L{Graph}
    accepts three dictionaries corresponding to the graph, vertex and edge
    attributes while the constructor of L{GraphBase} does not. This extension
    was needed to make L{Graph} serializable through the C{pickle} module.
    L{Graph} also overrides some functions from L{GraphBase} to provide a
    more convenient interface; e.g., layout functions return a L{Layout}
    instance from L{Graph} instead of a list of coordinate pairs.

    Graphs can also be indexed by strings or pairs of vertex indices or vertex
    names.  When a graph is indexed by a string, the operation translates to
    the retrieval, creation, modification or deletion of a graph attribute:

      >>> g = Graph.Full(3)
      >>> g["name"] = "Triangle graph"
      >>> g["name"]
      'Triangle graph'
      >>> del g["name"]

    When a graph is indexed by a pair of vertex indices or names, the graph
    itself is treated as an adjacency matrix and the corresponding cell of
    the matrix is returned:

      >>> g = Graph.Full(3)
      >>> g.vs["name"] = ["A", "B", "C"]
      >>> g[1, 2]
      1
      >>> g["A", "B"]
      1
      >>> g["A", "B"] = 0
      >>> g.ecount()
      2

    Assigning values different from zero or one to the adjacency matrix will
    be translated to one, unless the graph is weighted, in which case the
    numbers will be treated as weights:

      >>> g.is_weighted()
      False
      >>> g["A", "B"] = 2
      >>> g["A", "B"]
      1
      >>> g.es["weight"] = 1.0
      >>> g.is_weighted()
      True
      >>> g["A", "B"] = 2
      >>> g["A", "B"]
      2
      >>> g.es["weight"]
      [1.0, 1.0, 2]
    """

    # Some useful aliases
    omega = GraphBase.clique_number
    alpha = GraphBase.independence_number
    shell_index = GraphBase.coreness
    cut_vertices = GraphBase.articulation_points
    blocks = GraphBase.biconnected_components
    evcent = GraphBase.eigenvector_centrality
    vertex_disjoint_paths = GraphBase.vertex_connectivity
    edge_disjoint_paths = GraphBase.edge_connectivity
    cohesion = GraphBase.vertex_connectivity
    adhesion = GraphBase.edge_connectivity

    # Compatibility aliases
    shortest_paths = _shortest_paths
    shortest_paths_dijkstra = shortest_paths
    subgraph = GraphBase.induced_subgraph

    def __init__(self, *args, **kwds):
        """__init__(n=0, edges=None, directed=False, graph_attrs=None,
        vertex_attrs=None, edge_attrs=None)

        Constructs a graph from scratch.

        @keyword n: the number of vertices. Can be omitted, the default is
          zero. Note that if the edge list contains vertices with indexes
          larger than or equal to M{m}, then the number of vertices will
          be adjusted accordingly.
        @keyword edges: the edge list where every list item is a pair of
          integers. If any of the integers is larger than M{n-1}, the number
          of vertices is adjusted accordingly. C{None} means no edges.
        @keyword directed: whether the graph should be directed
        @keyword graph_attrs: the attributes of the graph as a dictionary.
        @keyword vertex_attrs: the attributes of the vertices as a dictionary.
          The keys of the dictionary must be the names of the attributes; the
          values must be iterables with exactly M{n} items where M{n} is the
          number of vertices.
        @keyword edge_attrs: the attributes of the edges as a dictionary. The
          keys of the dictionary must be the names of the attributes; the values
          must be iterables with exactly M{m} items where M{m} is the number of
          edges.
        """
        # Pop the special __ptr keyword argument
        ptr = kwds.pop("__ptr", None)

        # Set up default values for the parameters. This should match the order
        # in *args
        kwd_order = (
            "n",
            "edges",
            "directed",
            "graph_attrs",
            "vertex_attrs",
            "edge_attrs",
        )
        params = [0, [], False, {}, {}, {}]

        # Is there any keyword argument in kwds that we don't know? If so,
        # freak out.
        unknown_kwds = set(kwds.keys())
        unknown_kwds.difference_update(kwd_order)
        if unknown_kwds:
            raise TypeError(
                "{0}.__init__ got an unexpected keyword argument {1!r}".format(
                    self.__class__.__name__, unknown_kwds.pop()
                )
            )

        # If the first argument is a list or any other iterable, assume that
        # the number of vertices were omitted
        args = list(args)
        if len(args) > 0 and hasattr(args[0], "__iter__"):
            args.insert(0, params[0])

        # Override default parameters from args
        params[: len(args)] = args

        # Override default parameters from keywords
        for idx, k in enumerate(kwd_order):
            if k in kwds:
                params[idx] = kwds[k]

        # Now, translate the params list to argument names
        nverts, edges, directed, graph_attrs, vertex_attrs, edge_attrs = params

        # When the number of vertices is None, assume that the user meant zero
        if nverts is None:
            nverts = 0

        # When 'edges' is None, assume that the user meant an empty list
        if edges is None:
            edges = []

        # When 'edges' is a NumPy array or matrix, convert it into a memoryview
        # as the lower-level C API works with memoryviews only
        try:
            from numpy import ndarray, matrix

            if isinstance(edges, (ndarray, matrix)):
                edges = numpy_to_contiguous_memoryview(edges)
        except ImportError:
            pass

        # Initialize the graph
        if ptr:
            super().__init__(__ptr=ptr)
        else:
            super().__init__(nverts, edges, directed)

        # Set the graph attributes
        for key, value in graph_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self[key] = value
        # Set the vertex attributes
        for key, value in vertex_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self.vs[key] = value
        # Set the edge attributes
        for key, value in edge_attrs.items():
            if isinstance(key, int):
                key = str(key)
            self.es[key] = value

    #############################################
    # Auxiliary I/O functions
    # Graph libraries
    from_networkx = classmethod(_construct_graph_from_networkx)
    to_networkx = _export_graph_to_networkx

    from_graph_tool = classmethod(_construct_graph_from_graph_tool)
    to_graph_tool = _export_graph_to_graph_tool

    # Files
    Read_DIMACS = classmethod(_construct_graph_from_dimacs_file)
    write_dimacs = _write_graph_to_dimacs_file

    Read_GraphMLz = classmethod(_construct_graph_from_graphmlz_file)
    write_graphmlz = _write_graph_to_graphmlz_file

    Read_Pickle = classmethod(_construct_graph_from_pickle_file)
    write_pickle = _write_graph_to_pickle_file

    Read_Picklez = classmethod(_construct_graph_from_picklez_file)
    write_picklez = _write_graph_to_picklez_file

    Read_Adjacency = classmethod(_construct_graph_from_adjacency_file)
    write_adjacency = _write_graph_to_adjacency_file

    write_svg = _write_graph_to_svg

    Read = classmethod(_construct_graph_from_file)
    Load = Read
    write = _write_graph_to_file
    save = write

    # Various objects
    # list of dict representation of graphs
    DictList = classmethod(_construct_graph_from_dict_list)
    to_dict_list = _export_graph_to_dict_list

    # tuple-like representation of graphs
    TupleList = classmethod(_construct_graph_from_tuple_list)
    to_tuple_list = _export_graph_to_tuple_list

    # dict of sequence representation of graphs
    ListDict = classmethod(_construct_graph_from_list_dict)
    to_list_dict = _export_graph_to_list_dict

    # dict of dicts representation of graphs
    DictDict = classmethod(_construct_graph_from_dict_dict)
    to_dict_dict = _export_graph_to_dict_dict

    # adjacency matrix
    Adjacency = classmethod(_construct_graph_from_adjacency)
    Weighted_Adjacency = classmethod(_construct_graph_from_weighted_adjacency)

    # pandas dataframe(s)
    DataFrame = classmethod(_construct_graph_from_dataframe)
    get_vertex_dataframe = _export_vertex_dataframe
    get_edge_dataframe = _export_edge_dataframe

    # Bipartite graphs
    Bipartite = classmethod(_construct_bipartite_graph)
    Biadjacency = classmethod(_construct_bipartite_graph_from_adjacency)
    Full_Bipartite = classmethod(_construct_full_bipartite_graph)
    Random_Bipartite = classmethod(_construct_random_bipartite_graph)

    # Other constructors
    GRG = classmethod(_construct_random_geometric_graph)

    # Graph formulae
    Formula = classmethod(construct_graph_from_formula)

    #############################################
    # Summary/string representation
    def __str__(self):
        """Returns a string representation of the graph.

        Behind the scenes, this method constructs a L{GraphSummary}
        instance and invokes its C{__str__} method with a verbosity of 1
        and attribute printing turned off.

        See the documentation of L{GraphSummary} for more details about the
        output.
        """
        params = dict(
            verbosity=1,
            width=78,
            print_graph_attributes=False,
            print_vertex_attributes=False,
            print_edge_attributes=False,
        )
        return self.summary(**params)

    def summary(self, verbosity=0, width=None, *args, **kwds):
        """Returns the summary of the graph.

        The output of this method is similar to the output of the
        C{__str__} method. If I{verbosity} is zero, only the header line
        is returned (see C{__str__} for more details), otherwise the
        header line and the edge list is printed.

        Behind the scenes, this method constructs a L{GraphSummary}
        object and invokes its C{__str__} method.

        @param verbosity: if zero, only the header line is returned
          (see C{__str__} for more details), otherwise the header line
          and the full edge list is printed.
        @param width: the number of characters to use in one line.
          If C{None}, no limit will be enforced on the line lengths.
        @return: the summary of the graph.
        """
        return str(GraphSummary(self, verbosity, width, *args, **kwds))

    #############################################
    # Commonly used attributes
    def is_named(self):
        """Returns whether the graph is named.

        A graph is named if and only if it has a C{"name"} vertex attribute.
        """
        return "name" in self.vertex_attributes()

    def is_weighted(self):
        """Returns whether the graph is weighted.

        A graph is weighted if and only if it has a C{"weight"} edge attribute.
        """
        return "weight" in self.edge_attributes()

    #############################################
    # Vertex and edge sequence
    @property
    def vs(self):
        """The vertex sequence of the graph"""
        return VertexSeq(self)

    @property
    def es(self):
        """The edge sequence of the graph"""
        return EdgeSeq(self)

    #############################################
    # Basic operations
    add_edge = _add_edge
    add_edges = _add_edges
    add_vertex = _add_vertex
    add_vertices = _add_vertices
    delete_edges = _delete_edges
    clear = _clear
    as_directed = _as_directed
    as_undirected = _as_undirected

    ###################
    # Graph operators
    __iadd__ = _operator_method_registry["__iadd__"]
    __add__ = _operator_method_registry["__add__"]
    __and__ = _operator_method_registry["__and__"]
    __isub__ = _operator_method_registry["__isub__"]
    __sub__ = _operator_method_registry["__sub__"]
    __mul__ = _operator_method_registry["__mul__"]
    __or__ = _operator_method_registry["__or__"]
    disjoint_union = _operator_method_registry["disjoint_union"]
    union = _operator_method_registry["union"]
    intersection = _operator_method_registry["intersection"]

    #############################################
    # Adjacency/incidence
    get_adjacency = _get_adjacency
    get_adjacency_sparse = _get_adjacency_sparse
    get_adjlist = _get_adjlist
    get_biadjacency = _get_biadjacency
    get_inclist = _get_inclist

    #############################################
    # Structural properties
    indegree = _indegree
    outdegree = _outdegree
    degree_distribution = _degree_distribution
    pagerank = _pagerank

    #############################################
    # Flow
    all_st_cuts = _all_st_cuts
    all_st_mincuts = _all_st_mincuts
    gomory_hu_tree = _gomory_hu_tree
    maxflow = _maxflow
    mincut = _mincut
    st_mincut = _st_mincut

    #############################################
    # Connected components
    biconnected_components = _biconnected_components
    clusters = _clusters
    cohesive_blocks = _cohesive_blocks
    connected_components = _connected_components
    blocks = _biconnected_components
    components = _connected_components

    #############################################
    # Community detection/clustering
    community_fastgreedy = _community_fastgreedy
    community_infomap = _community_infomap
    community_leading_eigenvector = _community_leading_eigenvector
    community_label_propagation = _community_label_propagation
    community_multilevel = _community_multilevel
    community_optimal_modularity = _community_optimal_modularity
    community_edge_betweenness = _community_edge_betweenness
    community_spinglass = _community_spinglass
    community_walktrap = _community_walktrap
    k_core = _k_core
    community_leiden = _community_leiden
    modularity = _modularity

    #############################################
    # Layout
    layout = _layout
    layout_auto = _layout_auto
    layout_sugiyama = _layout_sugiyama

    #############################################
    # Plotting
    __plot__ = _graph_plot

    #############################################
    # Bipartite
    maximum_bipartite_matching = _maximum_bipartite_matching
    bipartite_projection = _bipartite_projection
    bipartite_projection_size = _bipartite_projection_size

    #############################################
    # Automorphisms
    count_automorphisms_vf2 = _count_automorphisms_vf2
    get_automorphisms_vf2 = _get_automorphisms_vf2

    ###########################
    # Paths/traversals
    def get_all_simple_paths(self, v, to=None, cutoff=-1, mode="out"):
        """Calculates all the simple paths from a given node to some other nodes
        (or all of them) in a graph.

        A path is simple if its vertices are unique, i.e. no vertex is visited
        more than once.

        Note that potentially there are exponentially many paths between two
        vertices of a graph, especially if your graph is lattice-like. In this
        case, you may run out of memory when using this function.

        @param v: the source for the calculated paths
        @param to: a vertex selector describing the destination for the calculated
          paths. This can be a single vertex ID, a list of vertex IDs, a single
          vertex name, a list of vertex names or a L{VertexSeq} object. C{None}
          means all the vertices.
        @param cutoff: maximum length of path that is considered. If negative,
          paths of all lengths are considered.
        @param mode: the directionality of the paths. C{\"in\"} means to calculate
          incoming paths, C{\"out\"} means to calculate outgoing paths, C{\"all\"} means
          to calculate both ones.
        @return: all of the simple paths from the given node to every other
          reachable node in the graph in a list. Note that in case of mode=C{\"in\"},
          the vertices in a path are returned in reversed order!
        """
        paths = self._get_all_simple_paths(v, to, cutoff, mode)
        prev = 0
        result = []
        for index, item in enumerate(paths):
            if item < 0:
                result.append(paths[prev:index])
                prev = index + 1
        return result

    def path_length_hist(self, directed=True):
        """Returns the path length histogram of the graph

        @param directed: whether to consider directed paths. Ignored for
          undirected graphs.
        @return: a L{Histogram} object. The object will also have an
          C{unconnected} attribute that stores the number of unconnected
          vertex pairs (where the second vertex can not be reached from
          the first one). The latter one will be of type long (and not
          a simple integer), since this can be I{very} large.
        """
        data, unconn = GraphBase.path_length_hist(self, directed)
        hist = Histogram(bin_width=1)
        for i, length in enumerate(data):
            hist.add(i + 1, length)
        hist.unconnected = int(unconn)
        return hist

    # DFS (C version will come soon)
    def dfs(self, vid, mode=OUT):
        """Conducts a depth first search (DFS) on the graph.

        @param vid: the root vertex ID
        @param mode: either C{\"in\"} or C{\"out\"} or C{\"all\"}, ignored
          for undirected graphs.
        @return: a tuple with the following items:
           - The vertex IDs visited (in order)
           - The parent of every vertex in the DFS
        """
        nv = self.vcount()
        added = [False for v in range(nv)]
        stack = []

        # prepare output
        vids = []
        parents = []

        # ok start from vid
        stack.append((vid, self.neighbors(vid, mode=mode)))
        vids.append(vid)
        parents.append(-1)
        added[vid] = True

        # go down the rabbit hole
        while stack:
            vid, neighbors = stack[-1]
            if neighbors:
                # Get next neighbor to visit
                neighbor = neighbors.pop()
                if not added[neighbor]:
                    # Add hanging subtree neighbor
                    stack.append((neighbor, self.neighbors(neighbor, mode=mode)))
                    vids.append(neighbor)
                    parents.append(vid)
                    added[neighbor] = True
            else:
                # No neighbor found, end of subtree
                stack.pop()

        return (vids, parents)

    def spanning_tree(self, weights=None, return_tree=True):
        """Calculates a minimum spanning tree for a graph.

        @param weights: a vector containing weights for every edge in
          the graph. C{None} means that the graph is unweighted.
        @param return_tree: whether to return the minimum spanning tree (when
          C{return_tree} is C{True}) or to return the IDs of the edges in
          the minimum spanning tree instead (when C{return_tree} is C{False}).
          The default is C{True} for historical reasons as this argument was
          introduced in igraph 0.6.
        @return: the spanning tree as a L{Graph} object if C{return_tree}
          is C{True} or the IDs of the edges that constitute the spanning
          tree if C{return_tree} is C{False}.

        @newfield ref: Reference
        @ref: Prim, R.C.: I{Shortest connection networks and some
          generalizations}. Bell System Technical Journal 36:1389-1401, 1957.
        """
        result = GraphBase._spanning_tree(self, weights)
        if return_tree:
            return self.subgraph_edges(result, delete_vertices=False)
        return result

    ###########################
    # Dyad/triad census
    def dyad_census(self, *args, **kwds):
        """Calculates the dyad census of the graph.

        Dyad census means classifying each pair of vertices of a directed
        graph into three categories: mutual (there is an edge from I{a} to
        I{b} and also from I{b} to I{a}), asymmetric (there is an edge
        from I{a} to I{b} or from I{b} to I{a} but not the other way round)
        and null (there is no connection between I{a} and I{b}).

        @return: a L{DyadCensus} object.
        @newfield ref: Reference
        @ref: Holland, P.W. and Leinhardt, S.  (1970).  A Method for Detecting
          Structure in Sociometric Data.  American Journal of Sociology, 70,
          492-513.
        """
        return DyadCensus(GraphBase.dyad_census(self, *args, **kwds))

    def triad_census(self, *args, **kwds):
        """Calculates the triad census of the graph.

        @return: a L{TriadCensus} object.
        @newfield ref: Reference
        @ref: Davis, J.A. and Leinhardt, S.  (1972).  The Structure of
          Positive Interpersonal Relations in Small Groups.  In:
          J. Berger (Ed.), Sociological Theories in Progress, Volume 2,
          218-251. Boston: Houghton Mifflin.
        """
        return TriadCensus(GraphBase.triad_census(self, *args, **kwds))

    ###########################
    # Other functions
    def transitivity_avglocal_undirected(self, mode="nan", weights=None):
        """Calculates the average of the vertex transitivities of the graph.

        In the unweighted case, the transitivity measures the probability that
        two neighbors of a vertex are connected. In case of the average local
        transitivity, this probability is calculated for each vertex and then
        the average is taken. Vertices with less than two neighbors require
        special treatment, they will either be left out from the calculation
        or they will be considered as having zero transitivity, depending on
        the I{mode} parameter. The calculation is slightly more involved for
        weighted graphs; in this case, weights are taken into account according
        to the formula of Barrat et al (see the references).

        Note that this measure is different from the global transitivity
        measure (see L{transitivity_undirected()}) as it simply takes the
        average local transitivity across the whole network.

        @param mode: defines how to treat vertices with degree less than two.
          If C{TRANSITIVITY_ZERO} or C{"zero"}, these vertices will have zero
          transitivity. If C{TRANSITIVITY_NAN} or C{"nan"}, these vertices
          will be excluded from the average.
        @param weights: edge weights to be used. Can be a sequence or iterable
          or even an edge attribute name.

        @see: L{transitivity_undirected()}, L{transitivity_local_undirected()}
        @newfield ref: Reference
        @ref: Watts DJ and Strogatz S: I{Collective dynamics of small-world
          networks}. Nature 393(6884):440-442, 1998.
        @ref: Barrat A, Barthelemy M, Pastor-Satorras R and Vespignani A:
          I{The architecture of complex weighted networks}. PNAS 101, 3747 (2004).
          U{http://arxiv.org/abs/cond-mat/0311416}.
        """
        if weights is None:
            return GraphBase.transitivity_avglocal_undirected(self, mode)

        xs = self.transitivity_local_undirected(mode=mode, weights=weights)
        return sum(xs) / float(len(xs))

    ###########################
    # ctypes support
    @property
    def _as_parameter_(self):
        return self._raw_pointer()

    # Other type functions
    def __bool__(self):
        """Returns True if the graph has at least one vertex, False otherwise."""
        return self.vcount() > 0

    def __coerce__(self, other):
        """Coercion rules.

        This method is needed to allow the graph to react to additions
        with lists, tuples, integers, strings, vertices, edges and so on.
        """
        if isinstance(other, (int, tuple, list, str)):
            return self, other
        if isinstance(other, Vertex):
            return self, other
        if isinstance(other, VertexSeq):
            return self, other
        if isinstance(other, Edge):
            return self, other
        if isinstance(other, EdgeSeq):
            return self, other
        return NotImplemented

    @classmethod
    def _reconstruct(cls, attrs, *args, **kwds):
        """Reconstructs a Graph object from Python's pickled format.

        This method is for internal use only, it should not be called
        directly."""
        result = cls(*args, **kwds)
        result.__dict__.update(attrs)
        return result

    def __reduce__(self):
        """Support for pickling."""
        constructor = self.__class__
        gattrs, vattrs, eattrs = {}, {}, {}
        for attr in self.attributes():
            gattrs[attr] = self[attr]
        for attr in self.vs.attribute_names():
            vattrs[attr] = self.vs[attr]
        for attr in self.es.attribute_names():
            eattrs[attr] = self.es[attr]
        parameters = (
            self.vcount(),
            self.get_edgelist(),
            self.is_directed(),
            gattrs,
            vattrs,
            eattrs,
        )
        return (constructor, parameters, self.__dict__)

    __iter__ = None  # needed for PyPy
    __hash__ = None  # needed for PyPy

    ###########################
    # Deprecated functions

    @classmethod
    def Incidence(cls, *args, **kwds):
        """Deprecated alias to L{Graph.Biadjacency()}."""
        deprecated("Graph.Incidence() is deprecated; use Graph.Biadjacency() instead")
        return cls.Biadjacency(*args, **kwds)

    def get_incidence(self, *args, **kwds):
        """Deprecated alias to L{Graph.get_biadjacency()}."""
        deprecated(
            "Graph.get_incidence() is deprecated; use Graph.get_biadjacency() "
            "instead"
        )
        return self.get_biadjacency(*args, **kwds)
    

##############################################################
# I/O format mapping
Graph._format_mapping = _format_mapping


##############################################################
# Additional methods of VertexSeq and EdgeSeq that call Graph methods
_add_proxy_methods()


##############################################################
# Layout mapping
Graph._layout_mapping = _layout_mapping


##############################################################
# Making sure that layout methods always return a Layout
for name in dir(Graph):
    if not name.startswith("layout_"):
        continue
    if name in ("layout_auto", "layout_sugiyama"):
        continue
    setattr(Graph, name, _layout_method_wrapper(getattr(Graph, name)))


##############################################################
# Adding aliases for the 3D versions of the layout methods
Graph.layout_fruchterman_reingold_3d = _3d_version_for(
    Graph.layout_fruchterman_reingold
)
Graph.layout_kamada_kawai_3d = _3d_version_for(Graph.layout_kamada_kawai)
Graph.layout_random_3d = _3d_version_for(Graph.layout_random)
Graph.layout_grid_3d = _3d_version_for(Graph.layout_grid)
Graph.layout_sphere = _3d_version_for(Graph.layout_circle)


##############################################################
# Auxiliary global functions
def get_include():
    """Returns the folder that contains the C API headers of the Python
    interface of igraph."""
    import igraph

    paths = [
        # The following path works if igraph is installed already
        os.path.join(
            sys.prefix,
            "include",
            "python{0}.{1}".format(*sys.version_info),
            "igraph",
        ),
        # Fallback for cases when igraph is not installed but
        # imported directly from the source tree
        os.path.join(os.path.dirname(igraph.__file__), "..", "src", "_igraph"),
    ]
    for path in paths:
        if os.path.exists(os.path.join(path, "igraphmodule_api.h")):
            return os.path.abspath(path)
    raise ValueError("cannot find the header files of the Python interface of igraph")


def read(filename, *args, **kwds):
    """Loads a graph from the given filename.

    This is just a convenience function, calls L{Graph.Read} directly.
    All arguments are passed unchanged to L{Graph.Read}

    @param filename: the name of the file to be loaded
    """
    return Graph.Read(filename, *args, **kwds)


load = read


def write(graph, filename, *args, **kwds):
    """Saves a graph to the given file.

    This is just a convenience function, calls L{Graph.write} directly.
    All arguments are passed unchanged to L{Graph.write}

    @param graph: the graph to be saved
    @param filename: the name of the file to be written
    """
    return graph.write(filename, *args, **kwds)


save = write


##############################################################
# Configuration singleton instance
config = init_configuration()
"""The main configuration object of igraph. Use this object to modify igraph's
behaviour, typically when used in interactive mode.
"""


##############################################################
# Remove modular methods from namespace
del (
    construct_graph_from_formula,
    _construct_graph_from_graphmlz_file,
    _construct_graph_from_dimacs_file,
    _construct_graph_from_pickle_file,
    _construct_graph_from_picklez_file,
    _construct_graph_from_adjacency_file,
    _construct_graph_from_file,
    _format_mapping,
    _construct_graph_from_dict_list,
    _construct_graph_from_tuple_list,
    _construct_graph_from_list_dict,
    _construct_graph_from_dict_dict,
    _construct_graph_from_adjacency,
    _construct_graph_from_weighted_adjacency,
    _construct_graph_from_dataframe,
    _construct_random_geometric_graph,
    _construct_bipartite_graph,
    _construct_bipartite_graph_from_adjacency,
    _construct_full_bipartite_graph,
    _construct_random_bipartite_graph,
    _construct_graph_from_networkx,
    _export_graph_to_networkx,
    _construct_graph_from_graph_tool,
    _export_graph_to_graph_tool,
    _export_graph_to_list_dict,
    _export_graph_to_dict_dict,
    _export_graph_to_dict_list,
    _export_graph_to_tuple_list,
    _community_fastgreedy,
    _community_infomap,
    _community_leading_eigenvector,
    _community_label_propagation,
    _community_multilevel,
    _community_optimal_modularity,
    _community_edge_betweenness,
    _community_spinglass,
    _community_walktrap,
    _k_core,
    _community_leiden,
    _modularity,
    _graph_plot,
    _operator_method_registry,
    _add_edge,
    _add_edges,
    _add_vertex,
    _add_vertices,
    _delete_edges,
    _as_directed,
    _as_undirected,
    _layout,
    _layout_auto,
    _layout_sugiyama,
    _layout_method_wrapper,
    _3d_version_for,
    _layout_mapping,
    _count_automorphisms_vf2,
    _get_automorphisms_vf2,
    _get_adjacency,
    _get_adjacency_sparse,
    _get_adjlist,
    _maximum_bipartite_matching,
    _bipartite_projection,
    _bipartite_projection_size,
    _biconnected_components,
    _cohesive_blocks,
    _connected_components,
    _add_proxy_methods,
)

# Re-export from _igraph for API docs
# Because _igraph starts with an underscore, pydoctor skips the whole docs
# except for the objects mentioned down here.
__all__ = (
    'config',
    'AdvancedGradientPalette',
    'BoundingBox',
    'CairoGraphDrawer',
    'ClusterColoringPalette',
    'Clustering',
    'CohesiveBlocks',
    'Configuration',
    'Cover',
    'Cut',
    'DefaultGraphDrawer',
    'Dendrogram',
    'DyadCensus',
    'Edge',
    'EdgeSeq',
    'FittedPowerLaw',
    'Flow',
    'GradientPalette',
    'Graph',
    'GraphBase',
    'GraphSummary',
    'Histogram',
    'InternalError',
    'Layout',
    'Matching',
    'MatplotlibGraphDrawer',
    'Matrix',
    'Palette',
    'Plot',
    'Point',
    'PrecalculatedPalette',
    'RainbowPalette',
    'Rectangle',
    'RunningMean',
    'TriadCensus',
    'UniqueIdGenerator',
    'Vertex',
    'VertexClustering',
    'VertexCover',
    'VertexDendrogram',
    'VertexSeq',
    'autocurve',
    'color_name_to_rgb',
    'color_name_to_rgba',
    'community_to_membership',
    'compare_communities',
    'convex_hull',
    'default_arpack_options',
    'disjoint_union',
    'get_include',
    'hsla_to_rgba',
    'hsl_to_rgb',
    'hsva_to_rgba',
    'hsv_to_rgb',
    'is_degree_sequence',
    'is_graphical',
    'is_graphical_degree_sequence',
    'intersection',
    'known_colors',
    'load',
    'mean',
    'median',
    'palettes',
    'percentile',
    'plot',
    'power_law_fit',
    'quantile',
    'read',
    'rescale',
    'rgba_to_hsla',
    'rgb_to_hsl',
    'rgba_to_hsva',
    'rgb_to_hsv',
    'save',
    'set_progress_handler',
    'set_random_number_generator',
    'set_status_handler',
    'split_join_distance',
    'summary',
    'union',
    'write',

    # enums and stuff
    'ADJ_DIRECTED',
    'ADJ_LOWER',
    'ADJ_MAX',
    'ADJ_MIN',
    'ADJ_PLUS',
    'ADJ_UNDIRECTED',
    'ADJ_UPPER',
    'ALL',
    'ARPACKOptions',
    'BFSIter',
    'BLISS_F',
    'BLISS_FL',
    'BLISS_FLM',
    'BLISS_FM',
    'BLISS_FS',
    'BLISS_FSM',
    'DFSIter',
    'GET_ADJACENCY_BOTH',
    'GET_ADJACENCY_LOWER',
    'GET_ADJACENCY_UPPER',
    'IN',
    'OUT',
    'REWIRING_SIMPLE',
    'REWIRING_SIMPLE_LOOPS',
    'STAR_IN',
    'STAR_MUTUAL',
    'STAR_OUT',
    'STAR_UNDIRECTED',
    'STRONG',
    'TRANSITIVITY_NAN',
    'TRANSITIVITY_ZERO',
    'TREE_IN',
    'TREE_OUT',
    'TREE_UNDIRECTED',
    'WEAK',

)
