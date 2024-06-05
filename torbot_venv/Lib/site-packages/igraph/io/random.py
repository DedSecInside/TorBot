def _construct_random_geometric_graph(cls, n, radius, torus=False):
    """Generates a random geometric graph.

    The algorithm drops the vertices randomly on the 2D unit square and
    connects them if they are closer to each other than the given radius.
    The coordinates of the vertices are stored in the vertex attributes C{x}
    and C{y}.

    @param n: The number of vertices in the graph
    @param radius: The given radius
    @param torus: This should be C{True} if we want to use a torus instead of a
      square.
    """
    result, xs, ys = cls._GRG(n, radius, torus)
    result.vs["x"] = xs
    result.vs["y"] = ys
    return result
