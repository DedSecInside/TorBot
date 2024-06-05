from igraph._igraph import GraphBase
from igraph.clustering import VertexDendrogram, VertexClustering
from igraph.utils import deprecated, safemax

from typing import List, Sequence, Tuple


def _community_fastgreedy(graph, weights=None):
    """Community structure based on the greedy optimization of modularity.

    This algorithm merges individual nodes into communities in a way that
    greedily maximizes the modularity score of the graph. It can be proven
    that if no merge can increase the current modularity score, the
    algorithm can be stopped since no further increase can be achieved.

    This algorithm is said to run almost in linear time on sparse graphs.

    @param weights: edge attribute name or a list containing edge
      weights
    @return: an appropriate L{VertexDendrogram} object.

    @newfield ref: Reference
    @ref: A Clauset, MEJ Newman and C Moore: Finding community structure
      in very large networks. Phys Rev E 70, 066111 (2004).
    """
    merges, qs = GraphBase.community_fastgreedy(graph, weights)
    optimal_count = _optimal_cluster_count_from_merges_and_modularity(graph, merges, qs)
    return VertexDendrogram(
        graph, merges, optimal_count, modularity_params=dict(weights=weights)
    )


def _community_infomap(graph, edge_weights=None, vertex_weights=None, trials=10):
    """Finds the community structure of the network according to the Infomap
    method of Martin Rosvall and Carl T. Bergstrom.

    @param edge_weights: name of an edge attribute or a list containing
      edge weights.
    @param vertex_weights: name of an vertex attribute or a list containing
      vertex weights.
    @param trials: the number of attempts to partition the network.
    @return: an appropriate L{VertexClustering} object with an extra attribute
      called C{codelength} that stores the code length determined by the
      algorithm.

    @newfield ref: Reference
    @ref: M. Rosvall and C. T. Bergstrom: Maps of information flow reveal
      community structure in complex networks, PNAS 105, 1118 (2008).
      U{http://dx.doi.org/10.1073/pnas.0706851105},
      U{http://arxiv.org/abs/0707.0609}.
    @ref: M. Rosvall, D. Axelsson, and C. T. Bergstrom: The map equation,
      Eur. Phys. J. Special Topics 178, 13 (2009).
      U{http://dx.doi.org/10.1140/epjst/e2010-01179-1},
      U{http://arxiv.org/abs/0906.1405}.
    """
    membership, codelength = GraphBase.community_infomap(
        graph, edge_weights, vertex_weights, trials
    )
    return VertexClustering(
        graph,
        membership,
        params={"codelength": codelength},
        modularity_params={"weights": edge_weights},
    )


def _community_leading_eigenvector(
    graph, clusters=None, weights=None, arpack_options=None
):
    """Newman's leading eigenvector method for detecting community structure.

    This is the proper implementation of the recursive, divisive algorithm:
    each split is done by maximizing the modularity regarding the
    original network.

    @param clusters: the desired number of communities. If C{None}, the
      algorithm tries to do as many splits as possible. Note that the
      algorithm won't split a community further if the signs of the leading
      eigenvector are all the same, so the actual number of discovered
      communities can be less than the desired one.
    @param weights: name of an edge attribute or a list containing
      edge weights.
    @param arpack_options: an L{ARPACKOptions} object used to fine-tune
      the ARPACK eigenvector calculation. If omitted, the module-level
      variable called C{arpack_options} is used.
    @return: an appropriate L{VertexClustering} object.

    @newfield ref: Reference
    @ref: MEJ Newman: Finding community structure in networks using the
    eigenvectors of matrices, arXiv:physics/0605087"""
    if clusters is None:
        clusters = -1

    kwds = dict(weights=weights)
    if arpack_options is not None:
        kwds["arpack_options"] = arpack_options

    membership, _, q = GraphBase.community_leading_eigenvector(graph, clusters, **kwds)
    return VertexClustering(graph, membership, modularity=q)


def _community_label_propagation(graph, weights=None, initial=None, fixed=None):
    """Finds the community structure of the graph according to the label
    propagation method of Raghavan et al.

    Initially, each vertex is assigned a different label. After that,
    each vertex chooses the dominant label in its neighbourhood in each
    iteration. Ties are broken randomly and the order in which the
    vertices are updated is randomized before every iteration. The
    algorithm ends when vertices reach a consensus.

    Note that since ties are broken randomly, there is no guarantee that
    the algorithm returns the same community structure after each run.
    In fact, they frequently differ. See the paper of Raghavan et al
    on how to come up with an aggregated community structure.

    Also note that the community _labels_ (numbers) have no semantic meaning
    and igraph is free to re-number communities. If you use fixed labels,
    igraph may still re-number the communities, but co-community membership
    constraints will be respected: if you had two vertices with fixed labels
    that belonged to the same community, they will still be in the same
    community at the end. Similarly, if you had two vertices with fixed
    labels that belonged to different communities, they will still be in
    different communities at the end.

    @param weights: name of an edge attribute or a list containing
      edge weights
    @param initial: name of a vertex attribute or a list containing
      the initial vertex labels. Labels are identified by integers from
      zero to M{n-1} where M{n} is the number of vertices. Negative
      numbers may also be present in this vector, they represent unlabeled
      vertices.
    @param fixed: a list of booleans for each vertex. C{True} corresponds
      to vertices whose labeling should not change during the algorithm.
      It only makes sense if initial labels are also given. Unlabeled
      vertices cannot be fixed. It may also be the name of a vertex
      attribute; each attribute value will be interpreted as a Boolean.
    @return: an appropriate L{VertexClustering} object.

    @newfield ref: Reference
    @ref: Raghavan, U.N. and Albert, R. and Kumara, S. Near linear
      time algorithm to detect community structures in large-scale
      networks. Phys Rev E 76:036106, 2007.
      U{http://arxiv.org/abs/0709.2938}.
    """
    if isinstance(fixed, str):
        fixed = [bool(o) for o in graph.vs[fixed]]
    cl = GraphBase.community_label_propagation(graph, weights, initial, fixed)
    return VertexClustering(graph, cl, modularity_params=dict(weights=weights))


def _community_multilevel(graph, weights=None, return_levels=False, resolution=1):
    """Community structure based on the multilevel algorithm of
    Blondel et al.

    This is a bottom-up algorithm: initially every vertex belongs to a
    separate community, and vertices are moved between communities
    iteratively in a way that maximizes the vertices' local contribution
    to the overall modularity score. When a consensus is reached (i.e. no
    single move would increase the modularity score), every community in
    the original graph is shrank to a single vertex (while keeping the
    total weight of the incident edges) and the process continues on the
    next level. The algorithm stops when it is not possible to increase
    the modularity any more after shrinking the communities to vertices.

    This algorithm is said to run almost in linear time on sparse graphs.

    @param weights: edge attribute name or a list containing edge
      weights
    @param return_levels: if C{True}, the communities at each level are
      returned in a list. If C{False}, only the community structure with
      the best modularity is returned.
    @param resolution: the resolution parameter to use in the modularity
      measure. Smaller values result in a smaller number of larger clusters,
      while higher values yield a large number of small clusters. The classical
      modularity measure assumes a resolution parameter of 1.
    @return: a list of L{VertexClustering} objects, one corresponding to
      each level (if C{return_levels} is C{True}), or a L{VertexClustering}
      corresponding to the best modularity.

    @newfield ref: Reference
    @ref: VD Blondel, J-L Guillaume, R Lambiotte and E Lefebvre: Fast
      unfolding of community hierarchies in large networks, J Stat Mech
      P10008 (2008), http://arxiv.org/abs/0803.0476
    """
    if graph.is_directed():
        raise ValueError("input graph must be undirected")

    modularity_params = dict(weights=weights, resolution=resolution)
    if return_levels:
        levels, qs = GraphBase.community_multilevel(
            graph, weights, return_levels=True, resolution=resolution
        )
        result = []
        for level, q in zip(levels, qs):
            result.append(
                VertexClustering(
                    graph, level, q, modularity_params=modularity_params
                )
            )
    else:
        membership = GraphBase.community_multilevel(
            graph, weights, return_levels=False, resolution=resolution
        )
        result = VertexClustering(
            graph, membership, modularity_params=modularity_params
        )

    return result


def _community_optimal_modularity(graph, *args, **kwds):
    """Calculates the optimal modularity score of the graph and the
    corresponding community structure.

    This function uses the GNU Linear Programming Kit to solve a large
    integer optimization problem in order to find the optimal modularity
    score and the corresponding community structure, therefore it is
    unlikely to work for graphs larger than a few (less than a hundred)
    vertices. Consider using one of the heuristic approaches instead if
    you have such a large graph.

    @return: the calculated membership vector and the corresponding
      modularity in a tuple."""
    membership, modularity = GraphBase.community_optimal_modularity(
        graph, *args, **kwds
    )
    return VertexClustering(graph, membership, modularity)


def _community_edge_betweenness(graph, clusters=None, directed=True, weights=None):
    """Community structure based on the betweenness of the edges in the
    network.

    The idea is that the betweenness of the edges connecting two
    communities is typically high, as many of the shortest paths between
    nodes in separate communities go through them. So we gradually remove
    the edge with the highest betweenness and recalculate the betweennesses
    after every removal. This way sooner or later the network falls of to
    separate components. The result of the clustering will be represented
    by a dendrogram.

    @param clusters: the number of clusters we would like to see. This
      practically defines the "level" where we "cut" the dendrogram to
      get the membership vector of the vertices. If C{None}, the dendrogram
      is cut at the level that maximizes the modularity when the graph is
      unweighted; otherwise the dendrogram is cut at at a single cluster
      (because cluster count selection based on modularities does not make
      sense for this method if not all the weights are equal).
    @param directed: whether the directionality of the edges should be
      taken into account or not.
    @param weights: name of an edge attribute or a list containing
      edge weights.
    @return: a L{VertexDendrogram} object, initally cut at the maximum
      modularity or at the desired number of clusters.
    """
    merges, qs = GraphBase.community_edge_betweenness(graph, directed, weights)
    if clusters is None:
        if qs is not None:
            clusters = _optimal_cluster_count_from_merges_and_modularity(graph, merges, qs)
        else:
            clusters = 1

    return VertexDendrogram(
        graph, merges, clusters, modularity_params=dict(weights=weights)
    )


def _community_spinglass(graph, *args, **kwds):
    """Finds the community structure of the graph according to the
    spinglass community detection method of Reichardt & Bornholdt.

    @keyword weights: edge weights to be used. Can be a sequence or
      iterable or even an edge attribute name.
    @keyword spins: integer, the number of spins to use. This is the
      upper limit for the number of communities. It is not a problem
      to supply a (reasonably) big number here, in which case some
      spin states will be unpopulated.
    @keyword parupdate: whether to update the spins of the vertices in
      parallel (synchronously) or not
    @keyword start_temp: the starting temperature
    @keyword stop_temp: the stop temperature
    @keyword cool_fact: cooling factor for the simulated annealing
    @keyword update_rule: specifies the null model of the simulation.
      Possible values are C{"config"} (a random graph with the same
      vertex degrees as the input graph) or C{"simple"} (a random
      graph with the same number of edges)
    @keyword gamma: the gamma argument of the algorithm, specifying the
      balance between the importance of present and missing edges
      within a community. The default value of 1.0 assigns equal
      importance to both of them.
    @keyword implementation: currently igraph contains two implementations
      of the spinglass community detection algorithm. The faster
      original implementation is the default. The other implementation
      is able to take into account negative weights, this can be
      chosen by setting C{implementation} to C{"neg"}
    @keyword lambda_: the lambda argument of the algorithm, which
      specifies the balance between the importance of present and missing
      negatively weighted edges within a community. Smaller values of
      lambda lead to communities with less negative intra-connectivity.
      If the argument is zero, the algorithm reduces to a graph coloring
      algorithm, using the number of spins as colors. This argument is
      ignored if the original implementation is used. Note the underscore
      at the end of the argument name; this is due to the fact that
      lambda is a reserved keyword in Python.
    @return: an appropriate L{VertexClustering} object.

    @newfield ref: Reference
    @ref: Reichardt J and Bornholdt S: Statistical mechanics of
      community detection. Phys Rev E 74:016110 (2006).
      U{http://arxiv.org/abs/cond-mat/0603718}.
    @ref: Traag VA and Bruggeman J: Community detection in networks
      with positive and negative links. Phys Rev E 80:036115 (2009).
      U{http://arxiv.org/abs/0811.2329}.
    """
    membership = GraphBase.community_spinglass(graph, *args, **kwds)
    if "weights" in kwds:
        modularity_params = dict(weights=kwds["weights"])
    else:
        modularity_params = {}
    return VertexClustering(graph, membership, modularity_params=modularity_params)


def _community_walktrap(graph, weights=None, steps=4):
    """Community detection algorithm of Latapy & Pons, based on random
    walks.

    The basic idea of the algorithm is that short random walks tend to stay
    in the same community. The result of the clustering will be represented
    as a dendrogram.

    @param weights: name of an edge attribute or a list containing
      edge weights
    @param steps: length of random walks to perform

    @return: a L{VertexDendrogram} object, initially cut at the maximum
      modularity.

    @newfield ref: Reference
    @ref: Pascal Pons, Matthieu Latapy: Computing communities in large
      networks using random walks, U{http://arxiv.org/abs/physics/0512106}.
    """
    merges, qs = GraphBase.community_walktrap(graph, weights, steps)
    optimal_count = _optimal_cluster_count_from_merges_and_modularity(graph, merges, qs)
    return VertexDendrogram(
        graph, merges, optimal_count, modularity_params=dict(weights=weights)
    )


def _k_core(graph, *args):
    """Returns some k-cores of the graph.

    The method accepts an arbitrary number of arguments representing
    the desired indices of the M{k}-cores to be returned. The arguments
    can also be lists or tuples. The result is a single L{Graph} object
    if an only integer argument was given, otherwise the result is a
    list of L{Graph} objects representing the desired k-cores in the
    order the arguments were specified. If no argument is given, returns
    all M{k}-cores in increasing order of M{k}.
    """
    if len(args) == 0:
        indices = range(graph.vcount())
        return_single = False
    else:
        return_single = True
        indices = []
        for arg in args:
            try:
                indices.extend(arg)
            except Exception:
                indices.append(arg)

    if len(indices) > 1 or hasattr(args[0], "__iter__"):
        return_single = False

    corenesses = graph.coreness()
    result = []
    vidxs = range(graph.vcount())
    for idx in indices:
        core_idxs = [vidx for vidx in vidxs if corenesses[vidx] >= idx]
        result.append(graph.subgraph(core_idxs))

    if return_single:
        return result[0]
    return result


def _community_leiden(
    graph,
    objective_function="CPM",
    weights=None,
    resolution=1.0,
    beta=0.01,
    initial_membership=None,
    n_iterations=2,
    node_weights=None,
    **kwds
):
    """Finds the community structure of the graph using the Leiden
    algorithm of Traag, van Eck & Waltman.

    @param objective_function: whether to use the Constant Potts
      Model (CPM) or modularity. Must be either C{"CPM"} or C{"modularity"}.
    @param weights: edge weights to be used. Can be a sequence or
      iterable or even an edge attribute name.
    @param resolution: the resolution parameter to use. Higher resolutions
      lead to more smaller communities, while lower resolutions lead to fewer
      larger communities.
    @param beta: parameter affecting the randomness in the Leiden
      algorithm. This affects only the refinement step of the algorithm.
    @param initial_membership: if provided, the Leiden algorithm
      will try to improve this provided membership. If no argument is
      provided, the aglorithm simply starts from the singleton partition.
    @param n_iterations: the number of iterations to iterate the Leiden
      algorithm. Each iteration may improve the partition further. Using
      a negative number of iterations will run until a stable iteration is
      encountered (i.e. the quality was not increased during that
      iteration).
    @param node_weights: the node weights used in the Leiden algorithm.
      If this is not provided, it will be automatically determined on the
      basis of whether you want to use CPM or modularity. If you do provide
      this, please make sure that you understand what you are doing.
    @return: an appropriate L{VertexClustering} object with an extra attribute
      called C{quality} that stores the value of the internal quality function
      optimized by the algorithm.

    @newfield ref: Reference
    @ref: Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain
      to Leiden: guaranteeing well-connected communities. Scientific
      reports, 9(1), 5233. doi: 10.1038/s41598-019-41695-z
    """
    if objective_function.lower() not in ("cpm", "modularity"):
        raise ValueError('objective_function must be "CPM" or "modularity".')

    if "resolution_parameter" in kwds:
        deprecated(
            "resolution_parameter keyword argument is deprecated, use "
            "resolution=... instead"
        )
        resolution = kwds.pop("resolution_parameter")

    if kwds:
        raise TypeError('unexpected keyword argument')

    membership, quality = GraphBase.community_leiden(
        graph,
        edge_weights=weights,
        node_weights=node_weights,
        resolution=resolution,
        normalize_resolution=(objective_function == "modularity"),
        beta=beta,
        initial_membership=initial_membership,
        n_iterations=n_iterations,
    )

    params = {"quality": quality}

    modularity_params = {"resolution": resolution}
    if weights is not None:
        modularity_params["weights"] = weights

    return VertexClustering(
        graph, membership, params=params, modularity_params=modularity_params
    )


def _modularity(self, membership, weights=None, resolution=1, directed=True):
    """Calculates the modularity score of the graph with respect to a given
    clustering.

    The modularity of a graph w.r.t. some division measures how good the
    division is, or how separated are the different vertex types from each
    other. It's defined as M{Q=1/(2m)*sum(Aij-gamma*ki*kj/(2m)delta(ci,cj),i,j)}.
    M{m} is the number of edges, M{Aij} is the element of the M{A}
    adjacency matrix in row M{i} and column M{j}, M{ki} is the degree of
    node M{i}, M{kj} is the degree of node M{j}, and M{Ci} and C{cj} are
    the types of the two vertices (M{i} and M{j}), and M{gamma} is a resolution
    parameter that defaults to 1 for the classical definition of modularity.
    M{delta(x,y)} is one iff M{x=y}, 0 otherwise.

    If edge weights are given, the definition of modularity is modified as
    follows: M{Aij} becomes the weight of the corresponding edge, M{ki}
    is the total weight of edges adjacent to vertex M{i}, M{kj} is the
    total weight of edges adjacent to vertex M{j} and M{m} is the total
    edge weight in the graph.

    @param membership: a membership list or a L{VertexClustering} object
    @param weights: optional edge weights or C{None} if all edges are
      weighed equally. Attribute names are also allowed.
    @param resolution: the resolution parameter I{gamma} in the formula above.
      The classical definition of modularity is retrieved when the resolution
      parameter is set to 1.
    @param directed: whether to consider edge directions if the graph is directed.
      C{True} will use the directed variant of the modularity measure where the
      in- and out-degrees of nodes are treated separately; C{False} will treat
      directed graphs as undirected.
    @return: the modularity score

    @newfield ref: Reference
    @ref: MEJ Newman and M Girvan: Finding and evaluating community
      structure in networks. Phys Rev E 69 026113, 2004.
    """
    if isinstance(membership, VertexClustering):
        if membership.graph != self:
            raise ValueError("clustering object belongs to another graph")
        return GraphBase.modularity(
            self, membership.membership, weights, resolution, directed
        )
    else:
        return GraphBase.modularity(self, membership, weights, resolution, directed)


def _optimal_cluster_count_from_merges_and_modularity(
    graph, merges: Sequence[Tuple[int, int]], qs: List[float]
) -> float:
    """Helper function to find the optimal cluster count for a hierarchical
    clustering of a graph, given the merge matrix and the list of modularity
    values after each merge.

    Reverses the modularity vector as a side effect.
    """
    no_of_comps = graph.vcount() - len(merges)
    qs.reverse()
    return qs.index(max(qs)) + no_of_comps
