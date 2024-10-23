__all__ = (
    "_count_automorphisms_vf2",
    "_get_automorphisms_vf2",
)


def _count_automorphisms_vf2(
    graph, color=None, edge_color=None, node_compat_fn=None, edge_compat_fn=None
):
    """Returns the number of automorphisms of the graph.

    This function simply calls C{count_isomorphisms_vf2} with the graph
    itgraph. See C{count_isomorphisms_vf2} for an explanation of the
    parameters.

    @return: the number of automorphisms of the graph
    @see: Graph.count_isomorphisms_vf2
    """
    return graph.count_isomorphisms_vf2(
        graph,
        color1=color,
        color2=color,
        edge_color1=edge_color,
        edge_color2=edge_color,
        node_compat_fn=node_compat_fn,
        edge_compat_fn=edge_compat_fn,
    )


def _get_automorphisms_vf2(
    graph, color=None, edge_color=None, node_compat_fn=None, edge_compat_fn=None
):
    """Returns all the automorphisms of the graph

    This function simply calls C{get_isomorphisms_vf2} with the graph
    itgraph. See C{get_isomorphisms_vf2} for an explanation of the
    parameters.

    @return: a list of lists, each item containing a possible mapping
      of the graph vertices to itgraph according to the automorphism
    @see: Graph.get_isomorphisms_vf2
    """
    return graph.get_isomorphisms_vf2(
        graph,
        color1=color,
        color2=color,
        edge_color1=edge_color,
        edge_color2=edge_color,
        node_compat_fn=node_compat_fn,
        edge_compat_fn=edge_compat_fn,
    )
