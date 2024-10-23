# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of union, disjoint union and intersection operators."""

__all__ = ("disjoint_union", "union", "intersection")
__docformat__ = "google en"

from igraph._igraph import GraphBase, _union, _intersection, _disjoint_union

from warnings import warn

def name_set(names):
    """Converts a list of names to a set of names while checking for duplicates.

    Parameters:
        names: the list of names to convert

    Returns:
        the set of unique names appearing in the list

    Raises:
        RuntimeError: if the input name list has duplicates
    """
    nameset = set(names)
    if (len(nameset) != len(names)):
        raise AttributeError("Graph contains duplicate vertex names")
    return nameset


def disjoint_union(graphs):
    """Graph disjoint union.

    The disjoint union of two or more graphs is created.

    This function keeps the attributes of all graphs. All graph, vertex and
    edge attributes are copied to the result. If an attribute is present in
    multiple graphs and would result a name clash, then this attribute is
    renamed by adding suffixes: _1, _2, etc.

    An error is generated if some input graphs are directed and others are
    undirected.

    Parameters:
        graphs: list of graphs. A lazy sequence is not acceptable.

    Returns:
        the disjoint union graph
    """
    if any(not isinstance(g, GraphBase) for g in graphs):
        raise TypeError("Not all elements are graphs")

    ngr = len(graphs)
    # Trivial cases
    if ngr == 0:
        raise ValueError("disjoint_union() needs at least one graph")
    if ngr == 1:
        return graphs[0].copy()
    # Now there are at least two graphs

    graph_union = _disjoint_union(graphs)

    # Graph attributes
    # NOTE: a_first_graph tracks which graph has the 1st occurrence of an
    # attribute, while a_conflict track attributes with naming conflicts
    a_first_graph = {}
    a_conflict = set()
    for ig, g in enumerate(graphs, 1):
        # NOTE: a_name is the name of the attribute, a_value its value
        for a_name in g.attributes():
            a_value = g[a_name]
            # No conflicts
            if a_name not in graph_union.attributes():
                a_first_graph[a_name] = ig
                graph_union[a_name] = a_value
                continue
            if graph_union[a_name] == a_value:
                continue
            if a_name not in a_conflict:
                # New conflict
                a_conflict.add(a_name)
                igf = a_first_graph[a_name]
                graph_union["{:}_{:}".format(a_name, igf)] = graph_union[a_name]
                del graph_union[a_name]
            graph_union["{:}_{:}".format(a_name, ig)] = a_value

    # Vertex attributes
    i = 0
    for g in graphs:
        nv = g.vcount()
        for attr in g.vertex_attributes():
            graph_union.vs[i : i + nv][attr] = g.vs[attr]
        i += nv

    # Edge attributes
    i = 0
    for g in graphs:
        ne = g.ecount()
        for attr in g.edge_attributes():
            graph_union.es[i : i + ne][attr] = g.es[attr]
        i += ne

    return graph_union


def union(graphs, byname="auto"):
    """Graph union.

    The union of two or more graphs is created. The graphs may have identical
    or overlapping vertex sets. Edges which are included in at least one graph
    will be part of the new graph.

    This function keeps the attributes of all graphs. All graph, vertex and
    edge attributes are copied to the result. If an attribute is present in
    multiple graphs and would result a name clash, then this attribute is
    renamed by adding suffixes: _1, _2, etc.

    The ``name`` vertex attribute is treated specially if the operation is
    performed based on symbolic vertex names. In this case ``name`` must be
    present in all graphs, and it is not renamed in the result graph.

    An error is generated if some input graphs are directed and others are
    undirected.

    Parameters:
        graphs: list of graphs. A lazy sequence is not acceptable.
        byname: bool or 'auto' specifying the function behaviour with
            respect to names vertices (i.e. vertices with the 'name' attribute). If
            False, ignore vertex names. If True, merge vertices based on names. If
            'auto', use True if all graphs have named vertices and False otherwise
            (in the latter case, a warning is generated too).

    Returns:
        the union graph

    Raises:
        RuntimeError: if 'byname' is set to True and some graphs are not named or
            the set of names is not unique in one of the graphs
    """

    if any(not isinstance(g, GraphBase) for g in graphs):
        raise TypeError("Not all elements are graphs")

    if byname not in (True, False, "auto"):
        raise ValueError('"byname" should be a bool or "auto"')

    ngr = len(graphs)
    n_named = sum(g.is_named() for g in graphs)
    if byname == "auto":
        byname = n_named == ngr
        if n_named not in (0, ngr):
            warn(
                f"Some, but not all graphs are named (got {n_named} named, "
                f"{ngr-n_named} unnamed), not using vertex names"
            )
    elif byname and (n_named != ngr):
        raise RuntimeError(
            f"Some graphs are not named (got {n_named} named, {ngr-n_named} unnamed)"
        )
    # Now we know that byname is only used is all graphs are named

    # Trivial cases
    if ngr == 0:
        raise ValueError("union() needs at least one graph")
    if ngr == 1:
        return graphs[0].copy()
    # Now there are at least two graphs

    if byname:
        allnames = [g.vs["name"] for g in graphs]
        uninames = list(set.union(*(name_set(vns) for vns in allnames)))
        permutation_map = {x: i for i, x in enumerate(uninames)}
        nve = len(uninames)
        newgraphs = []
        for g, vertex_names in zip(graphs, allnames):
            # Make a copy
            ng = g.copy()

            # Add the missing vertices
            v_missing = list(set(uninames) - set(vertex_names))
            ng.add_vertices(v_missing)

            # Reorder vertices to match uninames
            # vertex k -> p[k]
            permutation = [permutation_map[x] for x in ng.vs["name"]]
            ng = ng.permute_vertices(permutation)

            newgraphs.append(ng)
    else:
        newgraphs = graphs

    # If any graph has any edge attributes, we need edgemaps
    edgemaps = any(len(g.edge_attributes()) for g in graphs)
    res = _union(newgraphs, edgemaps)
    if edgemaps:
        graph_union = res["graph"]
        edgemaps = res["edgemaps"]
    else:
        graph_union = res

    # Graph attributes
    a_first_graph = {}
    a_conflict = set()
    for ig, g in enumerate(newgraphs, 1):
        # NOTE: a_name is the name of the attribute, a_value its value
        for a_name in g.attributes():
            a_value = g[a_name]
            # No conflicts
            if a_name not in graph_union.attributes():
                a_first_graph[a_name] = ig
                graph_union[a_name] = a_value
                continue
            if graph_union[a_name] == a_value:
                continue
            if a_name not in a_conflict:
                # New conflict
                a_conflict.add(a_name)
                igf = a_first_graph[a_name]
                # Delete the previous attribute and set attribute with
                # a record about the graph of origin
                graph_union["{:}_{:}".format(a_name, igf)] = graph_union[a_name]
                del graph_union[a_name]
            graph_union["{:}_{:}".format(a_name, ig)] = a_value

    # Vertex attributes
    if byname:
        graph_union.vs["name"] = uninames
    attrs = set.union(*(set(g.vertex_attributes()) for g in newgraphs)) - set(["name"])
    nve = graph_union.vcount()
    for a_name in attrs:
        # Check for conflicts at at least one vertex
        conflict = False
        vals = [None for i in range(nve)]
        for g in newgraphs:
            if a_name in g.vertex_attributes():
                for i, a_value in enumerate(g.vs[a_name]):
                    if a_value is None:
                        continue
                    if vals[i] is None:
                        vals[i] = a_value
                        continue
                    if vals[i] != a_value:
                        conflict = True
                        break
            if conflict:
                break

        if not conflict:
            graph_union.vs[a_name] = vals
            continue

        # There is a conflict, name after the graph number
        for ig, g in enumerate(newgraphs, 1):
            if a_name in g.vertex_attributes():
                graph_union.vs["{:}_{:}".format(a_name, ig)] = g.vs[a_name]

    # Edge attributes
    if edgemaps:
        attrs = set.union(*(set(g.edge_attributes()) for g in newgraphs))
        ne = graph_union.ecount()
        for a_name in attrs:
            # Check for conflicts at at least one edge
            conflict = False
            vals = [None for i in range(ne)]
            for g, emap in zip(newgraphs, edgemaps):
                if a_name not in g.edge_attributes():
                    continue
                for iu, a_value in zip(emap, g.es[a_name]):
                    if a_value is None:
                        continue
                    if vals[iu] is None:
                        vals[iu] = a_value
                        continue
                    if vals[iu] != a_value:
                        print(g, g.vs["name"], emap, a_value, iu, vals[iu])
                        conflict = True
                        break
                if conflict:
                    break

            if not conflict:
                graph_union.es[a_name] = vals
                continue

            # There is a conflict, name after the graph number
            for ig, (g, emap) in enumerate(zip(newgraphs, edgemaps), 1):
                if a_name not in g.edge_attributes():
                    continue
                # Pass through map
                vals = [None for i in range(ne)]
                for iu, a_value in zip(emap, g.es[a_name]):
                    vals[iu] = a_value
                graph_union.es["{:}_{:}".format(a_name, ig)] = vals

    return graph_union


def intersection(graphs, byname="auto", keep_all_vertices=True):
    """Graph intersection.

    The intersection of two or more graphs is created. The graphs may have
    identical or overlapping vertex sets. Edges which are included in all
    graphs will be part of the new graph.

    This function keeps the attributes of all graphs. All graph, vertex and
    edge attributes are copied to the result. If an attribute is present in
    multiple graphs and would result a name clash, then this attribute is
    renamed by adding suffixes: _1, _2, etc.

    The ``name`` vertex attribute is treated specially if the operation is
    performed based on symbolic vertex names. In this case ``name`` must be
    present in all graphs, and it is not renamed in the result graph.

    An error is generated if some input graphs are directed and others are
    undirected.

    Parameters:
        graphs: list of graphs. A lazy sequence is not acceptable.
        byname: bool or 'auto' specifying the function behaviour with
            respect to names vertices (i.e. vertices with the 'name' attribute). If
            False, ignore vertex names. If True, merge vertices based on names. If
            'auto', use True if all graphs have named vertices and False otherwise
            (in the latter case, a warning is generated too).
        keep_all_vertices: bool specifying if vertices that are not present
            in all graphs should be kept in the intersection.

    Returns:
        the intersection graph

    Raises:
        RuntimeError: if 'byname' is set to True and some graphs are not named or
            the set of names is not unique in one of the graphs
    """

    if any(not isinstance(g, GraphBase) for g in graphs):
        raise TypeError("Not all elements are graphs")

    if byname not in (True, False, "auto"):
        raise ValueError('"byname" should be a bool or "auto"')

    ngr = len(graphs)
    n_named = sum(g.is_named() for g in graphs)
    if byname == "auto":
        byname = n_named == ngr
        if n_named not in (0, ngr):
            warn(
                f"Some, but not all graphs are named (got {n_named} named, "
                f"{ngr-n_named} unnamed), not using vertex names"
            )
    elif byname and (n_named != ngr):
        raise RuntimeError(
            f"Some graphs are not named (got {n_named} named, {ngr-n_named} unnamed)"
        )
    # Now we know that byname is only used is all graphs are named

    # Trivial cases
    if ngr == 0:
        raise ValueError("intersection() needs at least one graph")
    if ngr == 1:
        return graphs[0].copy()
    # Now there are at least two graphs

    if byname:
        allnames = [g.vs["name"] for g in graphs]

        if keep_all_vertices:
            uninames = list(set.union(*(name_set(vns) for vns in allnames)))
        else:
            uninames = list(set.intersection(*(name_set(vns) for vns in allnames)))
        permutation_map = {x: i for i, x in enumerate(uninames)}

        nv = len(uninames)
        newgraphs = []
        for g, vertex_names in zip(graphs, allnames):
            # Make a copy
            ng = g.copy()

            if keep_all_vertices:
                # Add the missing vertices
                v_missing = list(set(uninames) - set(vertex_names))
                ng.add_vertices(v_missing)
            else:
                # Delete the private vertices
                v_private = list(set(vertex_names) - set(uninames))
                ng.delete_vertices(v_private)

            # Reorder vertices to match uninames
            # vertex k -> p[k]
            permutation = [permutation_map[x] for x in ng.vs["name"]]
            ng = ng.permute_vertices(permutation)

            newgraphs.append(ng)
    else:
        newgraphs = graphs

    # If any graph has any edge attributes, we need edgemaps
    edgemaps = any(len(g.edge_attributes()) for g in graphs)
    res = _intersection(newgraphs, edgemaps)
    if edgemaps:
        graph_intsec = res["graph"]
        edgemaps = res["edgemaps"]
    else:
        graph_intsec = res

    # Graph attributes
    a_first_graph = {}
    a_conflict = set()
    for ig, g in enumerate(newgraphs, 1):
        # NOTE: a_name is the name of the attribute, a_value its value
        for a_name in g.attributes():
            a_value = g[a_name]
            # No conflicts
            if a_name not in graph_intsec.attributes():
                a_first_graph[a_name] = ig
                graph_intsec[a_name] = a_value
                continue
            if graph_intsec[a_name] == a_value:
                continue
            if a_name not in a_conflict:
                # New conflict
                a_conflict.add(a_name)
                igf = a_first_graph[a_name]
                graph_intsec["{:}_{:}".format(a_name, igf)] = graph_intsec[a_name]
                del graph_intsec[a_name]
            graph_intsec["{:}_{:}".format(a_name, ig)] = a_value

    # Vertex attributes
    if byname:
        graph_intsec.vs["name"] = uninames
    attrs = set.union(*(set(g.vertex_attributes()) for g in newgraphs)) - set(["name"])
    nv = graph_intsec.vcount()
    for a_name in attrs:
        # Check for conflicts at at least one vertex
        conflict = False
        vals = [None for i in range(nv)]
        for g in newgraphs:
            if a_name not in g.vertex_attributes():
                continue
            for i, a_value in enumerate(g.vs[a_name]):
                if a_value is None:
                    continue
                if vals[i] is None:
                    vals[i] = a_value
                    continue
                if vals[i] != a_value:
                    conflict = True
                    break
            if conflict:
                break

        if not conflict:
            graph_intsec.vs[a_name] = vals
            continue

        # There is a conflict, name after the graph number
        for ig, g in enumerate(newgraphs, 1):
            if a_name in g.vertex_attributes():
                graph_intsec.vs["{:}_{:}".format(a_name, ig)] = g.vs[a_name]

    # Edge attributes
    if edgemaps:
        attrs = set.union(*(set(g.edge_attributes()) for g in newgraphs))
        ne = graph_intsec.ecount()
        for a_name in attrs:
            # Check for conflicts at at least one edge
            conflict = False
            vals = [None for i in range(ne)]
            for g, emap in zip(newgraphs, edgemaps):
                if a_name not in g.edge_attributes():
                    continue
                for iu, a_value in zip(emap, g.es[a_name]):
                    if iu == -1:
                        continue
                    if a_value is None:
                        continue
                    if vals[iu] is None:
                        vals[iu] = a_value
                        continue
                    if vals[iu] != a_value:
                        conflict = True
                        break
                if conflict:
                    break

            if not conflict:
                graph_intsec.es[a_name] = vals
                continue

            # There is a conflict, name after the graph number
            for ig, (g, emap) in enumerate(zip(newgraphs, edgemaps), 1):
                if a_name not in g.edge_attributes():
                    continue
                # Pass through map
                vals = [None for i in range(ne)]
                for iu, a_value in zip(emap, g.es[a_name]):
                    if iu == -1:
                        continue
                    vals[iu] = a_value
                graph_intsec.es["{:}_{:}".format(a_name, ig)] = vals

    return graph_intsec
