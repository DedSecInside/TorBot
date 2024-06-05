# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Layout-related code in the igraph library.

This package contains the implementation of the L{Layout} object.
"""


from math import sin, cos, pi

from igraph._igraph import GraphBase
from igraph.drawing.utils import BoundingBox
from igraph.statistics import RunningMean


__all__ = (
    "Layout",
    "_layout",
    "_layout_auto",
    "_layout_sugiyama",
    "_layout_method_wrapper",
    "_3d_version_for",
    "_layout_mapping",
)


class Layout:
    """Represents the layout of a graph.

    A layout is practically a list of coordinates in an n-dimensional
    space. This class is generic in the sense that it can store coordinates
    in any n-dimensional space.

    Layout objects are not associated directly with a graph. This is deliberate:
    there were times when I worked with almost identical copies of the same
    graph, the only difference was that they had different colors assigned to
    the vertices. It was particularly convenient for me to use the same layout
    for all of them, especially when I made figures for a paper. However,
    C{igraph} will of course refuse to draw a graph with a layout that has
    less coordinates than the node count of the graph.

    Layouts behave exactly like lists when they are accessed using the item
    index operator (C{[...]}). They can even be iterated through. Items
    returned by the index operator are only copies of the coordinates,
    but the stored coordinates can be modified by directly assigning to
    an index.

        >>> layout = Layout([(0, 1), (0, 2)])
        >>> coords = layout[1]
        >>> print(coords)
        [0, 2]
        >>> coords = (0, 3)
        >>> print(layout[1])
        [0, 2]
        >>> layout[1] = coords
        >>> print(layout[1])
        [0, 3]
    """

    def __init__(self, coords=None, dim=None):
        """Constructor.

        @param coords: the coordinates to be stored in the layout.
        @param dim: the number of dimensions. If C{None}, the number of
        dimensions is determined automatically from the length of the first
        item of the coordinate list. If there are no entries in the coordinate
        list, the default will be 2.  Generally, this should be given if the
        length of the coordinate list is zero, otherwise it should be left as
        is.
        """
        if coords is not None:
            self._coords = [list(coord) for coord in coords]
        else:
            self._coords = []

        if dim is None:
            if len(self._coords) == 0:
                self._dim = 2
            else:
                self._dim = len(self._coords[0])
        else:
            self._dim = int(dim)
            for row in self._coords:
                if len(row) != self._dim:
                    raise ValueError(
                        "all items in the coordinate list "
                        + "must have a length of %d" % self._dim
                    )

    def __len__(self):
        return len(self._coords)

    def __getitem__(self, idx):
        return self._coords[idx]

    def __setitem__(self, idx, value):
        if len(value) != self._dim:
            raise ValueError("assigned item must have %d elements" % self._dim)
        self._coords[idx] = list(value)

    def __delitem__(self, idx):
        del self._coords[idx]

    def __copy__(self):
        return self.__class__(self.coords, self.dim)

    def __repr__(self):
        if not self.coords:
            vertex_count = "no vertices"
        elif len(self.coords) == 1:
            vertex_count = "1 vertex"
        else:
            vertex_count = "%d vertices" % len(self.coords)
        if self.dim == 1:
            dim_count = "1 dimension"
        else:
            dim_count = "%d dimensions" % self.dim
        return "<%s with %s and %s>" % (
            self.__class__.__name__,
            vertex_count,
            dim_count,
        )

    @property
    def dim(self):
        """Returns the number of dimensions"""
        return self._dim

    @property
    def coords(self):
        """The coordinates as a list of lists"""
        return [row[:] for row in self._coords]

    def append(self, value):
        """Appends a new point to the layout"""
        if len(value) < self._dim:
            raise ValueError("appended item must have %d elements" % self._dim)
        self._coords.append([float(coord) for coord in value[0 : self._dim]])

    def mirror(self, dim):
        """Mirrors the layout along the given dimension(s)

        @param dim: the list of dimensions or a single dimension
        """
        if isinstance(dim, int):
            dim = [dim]
        else:
            dim = [int(x) for x in dim]

        for current_dim in dim:
            for row in self._coords:
                row[current_dim] *= -1

    def rotate(self, angle, dim1=0, dim2=1, **kwds):
        """Rotates the layout by the given degrees on the plane defined by
        the given two dimensions.

        @param angle: the angle of the rotation, specified in degrees.
        @param dim1: the first axis of the plane of the rotation.
        @param dim2: the second axis of the plane of the rotation.
        @keyword origin: the origin of the rotation. If not specified, the
          origin will be the origin of the coordinate system.
        """

        origin = list(kwds.get("origin", [0.0] * self._dim))
        if len(origin) != self._dim:
            raise ValueError("origin must have %d dimensions" % self._dim)

        radian = angle * pi / 180.0
        cos_alpha, sin_alpha = cos(radian), sin(radian)

        for idx, row in enumerate(self._coords):
            x, y = row[dim1] - origin[dim1], row[dim2] - origin[dim2]
            row[dim1] = cos_alpha * x - sin_alpha * y + origin[dim1]
            row[dim2] = sin_alpha * x + cos_alpha * y + origin[dim2]

    def scale(self, *args, **kwds):
        """Scales the layout.

        Scaling parameters can be provided either through the C{scale} keyword
        argument or through plain unnamed arguments. If a single integer or
        float is given, it is interpreted as a uniform multiplier to be applied
        on all dimensions. If it is a list or tuple, its length must be equal to
        the number of dimensions in the layout, and each element must be an
        integer or float describing the scaling coefficient in one of the
        dimensions.

        @keyword scale: scaling coefficients (integer, float, list or tuple)
        @keyword origin: the origin of scaling (this point will stay in place).
          Optional, defaults to the origin of the coordinate system being used.
        """
        origin = list(kwds.get("origin", [0.0] * self._dim))
        if len(origin) != self._dim:
            raise ValueError("origin must have %d dimensions" % self._dim)

        scaling = kwds.get("scale") or args
        if isinstance(scaling, (int, float)):
            scaling = [scaling]
        if len(scaling) == 0:
            raise ValueError("scaling factor must be given")
        elif len(scaling) == 1:
            if type(scaling[0]) == int or type(scaling[0]) == float:
                scaling *= self._dim
            else:
                scaling = scaling[0]
        if len(scaling) != self._dim:
            raise ValueError("scaling factor list must have %d elements" % self._dim)

        for idx, row in enumerate(self._coords):
            self._coords[idx] = [
                (row[d] - origin[d]) * scaling[d] + origin[d] for d in range(self._dim)
            ]

    def translate(self, *args, **kwds):
        """Translates the layout.

        The translation vector can be provided either through the C{v} keyword
        argument or through plain unnamed arguments. If unnamed arguments are
        used, the vector can be supplied as a single list (or tuple) or just as
        a series of arguments. In all cases, the translation vector must have
        the same number of dimensions as the layout.

        @keyword v: the translation vector
        """
        v = kwds.get("v") or args
        if len(v) == 0:
            raise ValueError("translation vector must be given")
        elif len(v) == 1 and type(v[0]) != int and type(v[0]) != float:
            v = v[0]
        if len(v) != self._dim:
            raise ValueError("translation vector must have %d dimensions" % self._dim)

        for idx, row in enumerate(self._coords):
            self._coords[idx] = [row[d] + v[d] for d in range(self._dim)]

    def to_radial(self, min_angle=100, max_angle=80, min_radius=0.0, max_radius=1.0):
        """Converts a planar layout to a radial one

        This method applies only to 2D layouts. The X coordinate of the
        layout is transformed to an angle, with min(x) corresponding to
        the parameter called I{min_angle} and max(y) corresponding to
        I{max_angle}. Angles are given in degrees, zero degree corresponds
        to the direction pointing upwards. The Y coordinate is
        interpreted as a radius, with min(y) belonging to the minimum and
        max(y) to the maximum radius given in the arguments.

        This is not a fully generic polar coordinate transformation, but
        it is fairly useful in creating radial tree layouts from ordinary
        top-down ones (that's why the Y coordinate belongs to the radius).
        It can also be used in conjunction with the Fruchterman-Reingold
        layout algorithm via its I{miny} and I{maxy} parameters (see
        L{Graph.layout_fruchterman_reingold()<GraphBase.layout_fruchterman_reingold()>})
        to produce radial layouts where the radius belongs to some property of
        the vertices.

        @param min_angle: the angle corresponding to the minimum X value
        @param max_angle: the angle corresponding to the maximum X value
        @param min_radius: the radius corresponding to the minimum Y value
        @param max_radius: the radius corresponding to the maximum Y value
        """
        if self._dim != 2:
            raise TypeError("implemented only for 2D layouts")
        bbox = self.bounding_box()

        while min_angle > max_angle:
            max_angle += 360
        while min_angle > 360:
            min_angle -= 360
            max_angle -= 360
        while min_angle < 0:
            min_angle += 360
            max_angle += 360

        ratio_x = (max_angle - min_angle) / bbox.width
        ratio_x *= pi / 180.0
        min_angle *= pi / 180.0
        ratio_y = (max_radius - min_radius) / bbox.height
        for idx, (x, y) in enumerate(self._coords):
            alpha = (x - bbox.left) * ratio_x + min_angle
            radius = (y - bbox.top) * ratio_y + min_radius
            self._coords[idx] = [cos(alpha) * radius, -sin(alpha) * radius]

    def transform(self, function, *args, **kwds):
        """Performs an arbitrary transformation on the layout

        Additional positional and keyword arguments are passed intact to
        the given function.

        @param function: a function which receives the coordinates as a
          tuple and returns the transformed tuple.
        """
        self._coords = [
            list(function(tuple(row), *args, **kwds)) for row in self._coords
        ]

    def centroid(self):
        """Returns the centroid of the layout.

        The centroid of the layout is the arithmetic mean of the points in
        the layout.

        @return: the centroid as a list of floats"""
        centroid = [RunningMean() for _ in range(self._dim)]
        for row in self._coords:
            for dim in range(self._dim):
                centroid[dim].add(row[dim])
        return [rm.mean for rm in centroid]

    def boundaries(self, border=0):
        """Returns the boundaries of the layout.

        The boundaries are the minimum and maximum coordinates along all
        dimensions.

        @param border: this value gets subtracted from the minimum bounds
          and gets added to the maximum bounds before returning the coordinates
          of the box. Defaults to zero.
        @return: the minimum and maximum coordinates along all dimensions,
          in a tuple containing two lists, one for the minimum coordinates,
          the other one for the maximum.
        @raises ValueError: if the layout contains no layout items
        """
        if not self._coords:
            raise ValueError("layout contains no layout items")

        mins, maxs = [], []
        for dim in range(self._dim):
            col = [row[dim] for row in self._coords]
            mins.append(min(col) - border)
            maxs.append(max(col) + border)
        return mins, maxs

    def bounding_box(self, border=0):
        """Returns the bounding box of the layout.

        The bounding box of the layout is the smallest box enclosing all the
        points in the layout.

        @param border: this value gets subtracted from the minimum bounds
          and gets added to the maximum bounds before returning the coordinates
          of the box. Defaults to zero.
        @return: the coordinates of the lower left and the upper right corner
          of the box. "Lower left" means the minimum coordinates and "upper right"
          means the maximum. These are encapsulated in a L{BoundingBox} object.
        """
        if self._dim != 2:
            raise ValueError("Layout.boundary_box() supports 2D layouts only")

        try:
            (x0, y0), (x1, y1) = self.boundaries(border)
            return BoundingBox(x0, y0, x1, y1)
        except ValueError:
            return BoundingBox(0, 0, 0, 0)

    def center(self, *args, **kwds):
        """Centers the layout around the given point.

        The point itself can be supplied as multiple unnamed arguments, as a
        simple unnamed list or as a keyword argument. This operation moves
        the centroid of the layout to the given point. If no point is supplied,
        defaults to the origin of the coordinate system.

        @keyword p: the point where the centroid of the layout will be after
          the operation."""
        center = kwds.get("p") or args
        if len(center) == 0:
            center = [0.0] * self._dim
        elif len(center) == 1 and type(center[0]) != int and type(center[0]) != float:
            center = center[0]
        if len(center) != self._dim:
            raise ValueError("the given point must have %d dimensions" % self._dim)
        centroid = self.centroid()
        vec = [center[d] - centroid[d] for d in range(self._dim)]
        self.translate(vec)

    def copy(self):
        """Creates an exact copy of the layout."""
        return self.__copy__()

    def fit_into(self, bbox, keep_aspect_ratio=True):
        """Fits the layout into the given bounding box.

        The layout will be modified in-place.

        @param bbox: the bounding box in which to fit the layout. If the
          dimension of the layout is d, it can either be a d-tuple (defining
          the sizes of the box), a 2d-tuple (defining the coordinates of the
          top left and the bottom right point of the box), or a L{BoundingBox}
          object (for 2D layouts only).
        @param keep_aspect_ratio: whether to keep the aspect ratio of the current
          layout. If C{False}, the layout will be rescaled to fit exactly into
          the bounding box. If C{True}, the original aspect ratio of the layout
          will be kept and it will be centered within the bounding box.
        """
        if isinstance(bbox, BoundingBox):
            if self._dim != 2:
                raise TypeError("bounding boxes work for 2D layouts only")
            corner, target_sizes = [bbox.left, bbox.top], [bbox.width, bbox.height]
        elif len(bbox) == self._dim:
            corner, target_sizes = [0.0] * self._dim, list(bbox)
        elif len(bbox) == 2 * self._dim:
            corner, opposite_corner = list(bbox[0 : self._dim]), list(bbox[self._dim :])
            for i in range(self._dim):
                if corner[i] > opposite_corner[i]:
                    corner[i], opposite_corner[i] = opposite_corner[i], corner[i]
            target_sizes = [
                max_val - min_val for min_val, max_val in zip(corner, opposite_corner)
            ]

        try:
            mins, maxs = self.boundaries()
        except ValueError:
            mins, maxs = [0.0] * self._dim, [0.0] * self._dim
        sizes = [max_val - min_val for min_val, max_val in zip(mins, maxs)]

        for i, size in enumerate(sizes):
            if size == 0:
                sizes[i] = 2
                mins[i] -= 1
                maxs[i] += 1

        ratios = [
            float(target_size) / current_size
            for current_size, target_size in zip(sizes, target_sizes)
        ]
        if keep_aspect_ratio:
            min_ratio = min(ratios)
            ratios = [min_ratio] * self._dim

        translations = []
        for i in range(self._dim):
            trans = (target_sizes[i] - ratios[i] * sizes[i]) / 2.0
            trans -= mins[i] * ratios[i] - corner[i]
            translations.append(trans)

        self.scale(*ratios)
        self.translate(*translations)


def _layout(graph, layout=None, *args, **kwds):
    """Returns the layout of the graph according to a layout algorithm.

    Parameters and keyword arguments not specified here are passed to the
    layout algorithm directly. See the documentation of the layout
    algorithms for the explanation of these parameters.

    Registered layout names understood by this method are:

      - C{auto}, C{automatic}: automatic layout
        (see L{Graph.layout_auto})

      - C{bipartite}: bipartite layout (see L{GraphBase.layout_bipartite})

      - C{circle}, C{circular}: circular layout
        (see L{GraphBase.layout_circle})

      - C{dh}, C{davidson_harel}: Davidson-Harel layout (see
        L{GraphBase.layout_davidson_harel})

      - C{drl}: DrL layout for large graphs (see L{GraphBase.layout_drl})

      - C{drl_3d}: 3D DrL layout for large graphs
        (see L{GraphBase.layout_drl})

      - C{fr}, C{fruchterman_reingold}: Fruchterman-Reingold layout
        (see L{GraphBase.layout_fruchterman_reingold}).

      - C{fr_3d}, C{fr3d}, C{fruchterman_reingold_3d}: 3D Fruchterman-
        Reingold layout (see L{GraphBase.layout_fruchterman_reingold}).

      - C{grid}: regular grid layout in 2D (see L{GraphBase.layout_grid})

      - C{grid_3d}: regular grid layout in 3D (see L{GraphBase.layout_grid})

      - C{graphopt}: the graphopt algorithm (see L{GraphBase.layout_graphopt})

      - C{kk}, C{kamada_kawai}: Kamada-Kawai layout
        (see L{GraphBase.layout_kamada_kawai})

      - C{kk_3d}, C{kk3d}, C{kamada_kawai_3d}: 3D Kamada-Kawai layout
        (see L{GraphBase.layout_kamada_kawai})

      - C{lgl}, C{large}, C{large_graph}: Large Graph Layout
        (see L{GraphBase.layout_lgl})

      - C{mds}: multidimensional scaling layout (see L{GraphBase.layout_mds})

      - C{random}: random layout (see L{GraphBase.layout_random})

      - C{random_3d}: random 3D layout (see L{GraphBase.layout_random})

      - C{rt}, C{tree}, C{reingold_tilford}: Reingold-Tilford tree
        layout (see L{GraphBase.layout_reingold_tilford})

      - C{rt_circular}, C{reingold_tilford_circular}: circular
        Reingold-Tilford tree layout
        (see L{GraphBase.layout_reingold_tilford_circular})

      - C{sphere}, C{spherical}, C{circle_3d}, C{circular_3d}: spherical
        layout (see L{GraphBase.layout_circle})

      - C{star}: star layout (see L{GraphBase.layout_star})

      - C{sugiyama}: Sugiyama layout (see L{Graph.layout_sugiyama})

    @param layout: the layout to use. This can be one of the registered
      layout names or a callable which returns either a L{Layout} object or
      a list of lists containing the coordinates. If C{None}, uses the
      value of the C{plotting.layout} configuration key.
    @return: a L{Layout} object.
    """
    # Deferred import to avoid cycles
    from igraph import config

    if layout is None:
        layout = config["plotting.layout"]
    if hasattr(layout, "__call__"):
        method = layout
    else:
        layout = layout.lower()
        if layout[-3:] == "_3d":
            kwds["dim"] = 3
            layout = layout[:-3]
        elif layout[-2:] == "3d":
            kwds["dim"] = 3
            layout = layout[:-2]
        method = getattr(graph.__class__, graph._layout_mapping[layout])
    if not hasattr(method, "__call__"):
        raise ValueError("layout method must be callable")
    layout = method(graph, *args, **kwds)
    if not isinstance(layout, Layout):
        layout = Layout(layout)
    return layout


def _layout_auto(graph, *args, **kwds):
    """Chooses and runs a suitable layout function based on simple
    topological properties of the graph.

    This function tries to choose an appropriate layout function for
    the graph using the following rules:

      1. If the graph has an attribute called C{layout}, it will be
         used. It may either be a L{Layout} instance, a list of
         coordinate pairs, the name of a layout function, or a
         callable function which generates the layout when called
         with the graph as a parameter.

      2. Otherwise, if the graph has vertex attributes called C{x}
         and C{y}, these will be used as coordinates in the layout.
         When a 3D layout is requested (by setting C{dim} to 3),
         a vertex attribute named C{z} will also be needed.

      3. Otherwise, if the graph is connected and has at most 100
         vertices, the Kamada-Kawai layout will be used (see
         L{GraphBase.layout_kamada_kawai()}).

      4. Otherwise, if the graph has at most 1000 vertices, the
         Fruchterman-Reingold layout will be used (see
         L{GraphBase.layout_fruchterman_reingold()}).

      5. If everything else above failed, the DrL layout algorithm
         will be used (see L{GraphBase.layout_drl()}).

    All the arguments of this function except C{dim} are passed on
    to the chosen layout function (in case we have to call some layout
    function).

    @keyword dim: specifies whether we would like to obtain a 2D or a
      3D layout.
    @return: a L{Layout} object.
    """
    if "layout" in graph.attributes():
        layout = graph["layout"]
        if isinstance(layout, Layout):
            # Layouts are used intact
            return layout
        if isinstance(layout, (list, tuple)):
            # Lists/tuples are converted to layouts
            return Layout(layout)
        if hasattr(layout, "__call__"):
            # Callables are called
            return Layout(layout(*args, **kwds))
        # Try Graph.layout()
        return graph.layout(layout, *args, **kwds)

    dim = kwds.get("dim", 2)
    vattrs = graph.vertex_attributes()
    if "x" in vattrs and "y" in vattrs:
        if dim == 3 and "z" in vattrs:
            return Layout(list(zip(graph.vs["x"], graph.vs["y"], graph.vs["z"])))
        else:
            return Layout(list(zip(graph.vs["x"], graph.vs["y"])))

    if graph.vcount() <= 100 and graph.is_connected():
        algo = "kk"
    elif graph.vcount() <= 1000:
        algo = "fr"
    else:
        algo = "drl"
    return graph.layout(algo, *args, **kwds)


def _layout_sugiyama(
    graph,
    layers=None,
    weights=None,
    hgap=1,
    vgap=1,
    maxiter=100,
    return_extended_graph=False,
):
    """Places the vertices using a layered Sugiyama layout.

    This is a layered layout that is most suitable for directed acyclic graphs,
    although it works on undirected or cyclic graphs as well.

    Each vertex is assigned to a layer and each layer is placed on a horizontal
    line. Vertices within the same layer are then permuted using the barycenter
    heuristic that tries to minimize edge crossings.

    Dummy vertices will be added on edges that span more than one layer. The
    returned layout therefore contains more rows than the number of nodes in
    the original graph; the extra rows correspond to the dummy vertices.

    @param layers: a vector specifying a non-negative integer layer index for
      each vertex, or the name of a numeric vertex attribute that contains
      the layer indices. If C{None}, a layering will be determined
      automatically. For undirected graphs, a spanning tree will be extracted
      and vertices will be assigned to layers using a breadth first search from
      the node with the largest degree. For directed graphs, cycles are broken
      by reversing the direction of edges in an approximate feedback arc set
      using the heuristic of Eades, Lin and Smyth, and then using longest path
      layering to place the vertices in layers.
    @param weights: edge weights to be used. Can be a sequence or iterable or
      even an edge attribute name.
    @param hgap: minimum horizontal gap between vertices in the same layer.
    @param vgap: vertical gap between layers. The layer index will be
      multiplied by I{vgap} to obtain the Y coordinate.
    @param maxiter: maximum number of iterations to take in the crossing
      reduction step. Increase this if you feel that you are getting too many
      edge crossings.
    @param return_extended_graph: specifies that the extended graph with the
      added dummy vertices should also be returned. When this is C{True}, the
      result will be a tuple containing the layout and the extended graph. The
      first |V| nodes of the extended graph will correspond to the nodes of the
      original graph, the remaining ones are dummy nodes. Plotting the extended
      graph with the returned layout and hidden dummy nodes will produce a layout
      that is similar to the original graph, but with the added edge bends.
      The extended graph also contains an edge attribute called C{_original_eid}
      which specifies the ID of the edge in the original graph from which the
      edge of the extended graph was created.
    @return: the calculated layout, which may (and usually will) have more rows
      than the number of vertices; the remaining rows correspond to the dummy
      nodes introduced in the layering step. When C{return_extended_graph} is
      C{True}, it will also contain the extended graph.

    @newfield ref: Reference
    @ref: K Sugiyama, S Tagawa, M Toda: Methods for visual understanding of
      hierarchical system structures. IEEE Systems, Man and Cybernetics\
      11(2):109-125, 1981.
    @ref: P Eades, X Lin and WF Smyth: A fast effective heuristic for the
      feedback arc set problem. Information Processing Letters 47:319-323, 1993.
    """
    if not return_extended_graph:
        return Layout(
            GraphBase._layout_sugiyama(
                graph, layers, weights, hgap, vgap, maxiter, return_extended_graph
            )
        )

    layout, extd_graph, extd_to_orig_eids = GraphBase._layout_sugiyama(
        graph, layers, weights, hgap, vgap, maxiter, return_extended_graph
    )
    extd_graph.es["_original_eid"] = extd_to_orig_eids
    return Layout(layout), extd_graph


def _layout_method_wrapper(func):
    """Wraps an existing layout method to ensure that it returns a Layout
    instead of a list of lists.

    @param func: the method to wrap. Must be a method of the Graph object.
    @return: a new method
    """

    def result(*args, **kwds):
        layout = func(*args, **kwds)
        if not isinstance(layout, Layout):
            layout = Layout(layout)
        return layout

    result.__name__ = func.__name__
    result.__doc__ = func.__doc__
    return result


def _3d_version_for(func):
    """Creates an alias for the 3D version of the given layout algoritm.

    This function is a decorator that creates a method which calls I{func} after
    attaching C{dim=3} to the list of keyword arguments.

    @param func: must be a method of the Graph object.
    @return: a new method
    """

    def result(*args, **kwds):
        kwds["dim"] = 3
        return func(*args, **kwds)

    result.__name__ = "%s_3d" % func.__name__
    result.__doc__ = """Alias for L{%s()} with dim=3.\n\n@see: Graph.%s()""" % (
        func.__name__,
        func.__name__,
    )
    return result


# After adjusting something here, don't forget to update the docstring
# of Graph.layout if necessary!
_layout_mapping = {
    "auto": "layout_auto",
    "automatic": "layout_auto",
    "bipartite": "layout_bipartite",
    "circle": "layout_circle",
    "circular": "layout_circle",
    "davidson_harel": "layout_davidson_harel",
    "dh": "layout_davidson_harel",
    "drl": "layout_drl",
    "fr": "layout_fruchterman_reingold",
    "fruchterman_reingold": "layout_fruchterman_reingold",
    "graphopt": "layout_graphopt",
    "grid": "layout_grid",
    "kk": "layout_kamada_kawai",
    "kamada_kawai": "layout_kamada_kawai",
    "lgl": "layout_lgl",
    "large": "layout_lgl",
    "large_graph": "layout_lgl",
    "mds": "layout_mds",
    "random": "layout_random",
    "rt": "layout_reingold_tilford",
    "tree": "layout_reingold_tilford",
    "reingold_tilford": "layout_reingold_tilford",
    "rt_circular": "layout_reingold_tilford_circular",
    "reingold_tilford_circular": "layout_reingold_tilford_circular",
    "sphere": "layout_sphere",
    "spherical": "layout_sphere",
    "star": "layout_star",
    "sugiyama": "layout_sugiyama",
}
