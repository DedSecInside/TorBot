# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of Python-level sparse matrix operations."""

from __future__ import with_statement

__all__ = ()
__docformat__ = "restructuredtext en"

from operator import add
from igraph._igraph import (
    ADJ_DIRECTED,
    ADJ_UNDIRECTED,
    ADJ_MAX,
    ADJ_MIN,
    ADJ_PLUS,
    ADJ_UPPER,
    ADJ_LOWER,
)


_SUPPORTED_MODES = ("directed", "undirected", "max", "min", "plus", "lower", "upper")


def _convert_mode_argument(mode):
    # resolve mode constants, convert to lowercase
    mode = (
        {
            ADJ_DIRECTED: "directed",
            ADJ_UNDIRECTED: "undirected",
            ADJ_MAX: "max",
            ADJ_MIN: "min",
            ADJ_PLUS: "plus",
            ADJ_UPPER: "upper",
            ADJ_LOWER: "lower",
        }
        .get(mode, mode)
        .lower()
    )

    if mode not in _SUPPORTED_MODES:
        raise ValueError("mode should be one of " + (" ".join(_SUPPORTED_MODES)))

    if mode == "undirected":
        mode = "max"

    return mode


def _maybe_halve_diagonal(m, condition):
    """Halves all items in the diagonal of the given SciPy sparse matrix in
    coo mode *if* and *only if* the given condition is True.

    Returns the row, column and data arrays.
    """
    data_array = m.data
    if condition:
        # We can't do data_array[m.row == m.col] /= 2 here because we would be
        # modifying the array in-place and the end user wouldn't like if we
        # messed with their matrix. So we make a copy.
        data_array = data_array.copy()
        idxs, = (m.row == m.col).nonzero()
        for i in idxs:
            data_array[i] /= 2

    return m.row, m.col, data_array


# Logic to get graph from scipy sparse matrix. This would be simple if there
# weren't so many modes.
def _graph_from_sparse_matrix(klass, matrix, mode="directed", loops="once"):
    """Construct graph from sparse matrix, unweighted.

    @param loops: specifies how the diagonal of the matrix should be handled:

      - C{"ignore"} - ignore loop edges in the diagonal
      - C{"once"} - treat the diagonal entries as loop edge counts
      - C{"twice"} - treat the diagonal entries as I{twice} the number
        of loop edges
    """
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    nvert = max(matrix.shape)
    if min(matrix.shape) != nvert:
        raise ValueError("Matrix must be square")

    # Shorthand notation
    m = matrix

    mode = _convert_mode_argument(mode)

    keep_loops = (loops == "twice" or loops == "once" or loops is True)
    m_row, m_col, m_data = _maybe_halve_diagonal(m, loops == "twice")

    if mode == "directed":
        edges = []
        for i, j, n in zip(m_row, m_col, m_data):
            if i != j or keep_loops:
                edges.extend([(i, j)] * n)

    elif mode in ("max", "plus"):
        fun = max if mode == "max" else add
        nedges = {}
        for i, j, n in zip(m_row, m_col, m_data):
            if i == j and not keep_loops:
                continue
            pair = (i, j) if i < j else (j, i)
            nedges[pair] = fun(nedges.get(pair, 0), n)

        edges = sum(
            ([e] * n for e, n in nedges.items()),
            [],
        )

    elif mode == "min":
        tmp = {(i, j): n for i, j, n in zip(m_row, m_col, m_data)}

        nedges = {}
        for pair, weight in tmp.items():
            i, j = pair
            if i == j and keep_loops:
                nedges[pair] = weight
            elif i < j:
                nedges[pair] = min(weight, tmp.get((j, i), 0))

        edges = sum(
            ([e] * n for e, n in nedges.items()),
            [],
        )

    elif mode == "upper":
        edges = []
        for i, j, n in zip(m_row, m_col, m_data):
            if j > i or (keep_loops and j == i):
                edges.extend([(i, j)] * n)

    elif mode == "lower":
        edges = []
        for i, j, n in zip(m_row, m_col, m_data):
            if j < i or (keep_loops and j == i):
                edges.extend([(i, j)] * n)

    else:
        raise ValueError(f"invalid mode: {mode!r}")

    return klass(nvert, edges=edges, directed=(mode == "directed"))


def _graph_from_weighted_sparse_matrix(
    klass, matrix, mode=ADJ_DIRECTED, attr="weight", loops="once"
):
    """Construct graph from sparse matrix, weighted

    NOTE: Of course, you cannot emcompass a fully general weighted multigraph
    with a single adjacency matrix, so we don't try to do it here either.

    @param loops: specifies how to handle loop edges. When C{False} or
        C{"ignore"}, the diagonal of the adjacency matrix will be ignored. When
        C{True} or C{"once"}, the diagonal is assumed to contain the weight of the
        corresponding loop edge. When C{"twice"}, the diagonal is assumed to
        contain I{twice} the weight of the corresponding loop edge.
    """
    # This function assumes there is scipy and the matrix is a scipy sparse
    # matrix. The caller should make sure those conditions are met.
    from scipy import sparse

    if not isinstance(matrix, sparse.coo_matrix):
        matrix = matrix.tocoo()

    nvert = max(matrix.shape)
    if min(matrix.shape) != nvert:
        raise ValueError("Matrix must be square")

    # Shorthand notation
    m = matrix

    mode = _convert_mode_argument(mode)

    keep_loops = (loops == "twice" or loops == "once" or loops is True)
    m_row, m_col, m_data = _maybe_halve_diagonal(m, loops == "twice")

    if mode == "directed":
        if not keep_loops:
            edges, weights = [], []
            for i, j, n in zip(m_row, m_col, m_data):
                if i != j:
                    edges.append((i, j))
                    weights.append(n)
        else:   # loops == "once" or True
            edges = list(zip(m_row, m_col))
            weights = list(m_data)

    elif mode in ("max", "plus"):
        fun = max if mode == "max" else add
        nedges = {}
        for i, j, n in zip(m_row, m_col, m_data):
            if i == j and not keep_loops:
                continue

            pair = (i, j) if i < j else (j, i)
            nedges[pair] = fun(nedges.get(pair, 0), n)

        edges, weights = zip(*nedges.items())

    elif mode == "min":
        tmp = {(i, j): n for i, j, n in zip(m_row, m_col, m_data)}

        nedges = {}
        for pair, weight in tmp.items():
            i, j = pair
            if i == j and keep_loops:
                nedges[pair] = weight
            elif i < j:
                nedges[pair] = min(weight, tmp.get((j, i), 0))

        edges, weights = [], []
        for pair in sorted(nedges.keys()):
            weight = nedges[pair]
            if weight != 0:
                edges.append(pair)
                weights.append(nedges[pair])

    elif mode == "upper":
        edges, weights = [], []
        for i, j, n in zip(m_row, m_col, m_data):
            if j > i or (keep_loops and j == i):
                edges.append((i, j))
                weights.append(n)

    elif mode == "lower":
        edges, weights = [], []
        for i, j, n in zip(m_row, m_col, m_data):
            if j < i or (keep_loops and j == i):
                edges.append((i, j))
                weights.append(n)

    else:
        raise ValueError(f"invalid mode: {mode!r}")

    return klass(
        nvert, edges=edges, directed=(mode == "directed"), edge_attrs={attr: weights}
    )
