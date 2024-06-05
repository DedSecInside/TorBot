"""
Drawing routines to draw graphs.

This module contains routines to draw graphs on:

  - Cairo surfaces (L{DefaultGraphDrawer})
  - Matplotlib axes (L{MatplotlibGraphDrawer})

It also contains routines to send an igraph graph directly to
(U{Cytoscape<http://www.cytoscape.org>}) using the
(U{CytoscapeRPC plugin<http://gforge.nbic.nl/projects/cytoscaperpc/>}), see
L{CytoscapeGraphDrawer}. L{CytoscapeGraphDrawer} can also fetch the current
network from Cytoscape and convert it to igraph format.
"""

from warnings import warn
from functools import wraps, partial

from igraph._igraph import convex_hull, VertexSeq
from igraph.drawing.baseclasses import AbstractGraphDrawer
from igraph.drawing.utils import Point, FakeModule

from .edge import MatplotlibEdgeDrawer
from .polygon import MatplotlibPolygonDrawer
from .utils import find_matplotlib
from .vertex import MatplotlibVertexDrawer

__all__ = ("MatplotlibGraphDrawer",)

mpl, plt = find_matplotlib()
try:
    Artist = mpl.artist.Artist
except AttributeError:
    Artist = FakeModule

#####################################################################


# NOTE: https://github.com/networkx/grave/blob/main/grave/grave.py
def _stale_wrapper(func):
    """Decorator to manage artist state."""

    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        finally:
            self.stale = False

    return inner


def _forwarder(forwards, cls=None):
    """Decorator to forward specific methods to Artist children."""
    if cls is None:
        return partial(_forwarder, forwards)

    def make_forward(name):
        def method(self, *args, **kwargs):
            ret = getattr(cls.mro()[1], name)(self, *args, **kwargs)
            for c in self.get_children():
                getattr(c, name)(*args, **kwargs)
            return ret

        return method

    for f in forwards:
        method = make_forward(f)
        method.__name__ = f
        method.__doc__ = "broadcasts {} to children".format(f)
        setattr(cls, f, method)

    return cls


def _additional_set_methods(attributes, cls=None):
    """Decorator to add specific set methods for children properties."""
    if cls is None:
        return partial(_additional_set_methods, attributes)

    def make_setter(name):
        def method(self, value):
            self.set(**{name: value})

        return method

    for attr in attributes:
        desc = attr.replace("_", " ")
        method = make_setter(attr)
        method.__name__ = f"set_{attr}"
        method.__doc__ = f"Set {desc}."
        setattr(cls, f"set_{attr}", method)

    return cls


@_additional_set_methods(
    (
        "vertex_color",
        "vertex_size",
        "vertex_font",
        "vertex_label",
        "vertex_label_angle",
        "vertex_label_color",
        "vertex_label_dist",
        "vertex_label_size",
        "vertex_order",
        "vertex_shape",
        "vertex_size",
        "edge_color",
        "edge_curved",
        "edge_font",
        "edge_arrow_size",
        "edge_arrow_width",
        "edge_width",
        "edge_label",
        "edge_background",
        "edge_align_label",
        "autocurve",
        "layout",
    )
)
@_forwarder(
    (
        "set_clip_path",
        "set_clip_box",
        "set_transform",
        "set_snap",
        "set_sketch_params",
        "set_figure",
        "set_animated",
        "set_picker",
    )
)
class GraphArtist(Artist, AbstractGraphDrawer):
    """Artist for an igraph.Graph object.

    @param graph: An igraph.Graph object to plot
    @param layout: A layout object or matrix of coordinates to use for plotting.
        Each element or row should describes the coordinates for a vertex.
    @param vertex_style: A dictionary specifying style options for vertices.
    @param edge_style: A dictionary specifying style options for edges.
    """

    def __init__(
        self,
        graph,
        vertex_drawer_factory=MatplotlibVertexDrawer,
        edge_drawer_factory=MatplotlibEdgeDrawer,
        mark_groups=None,
        layout=None,
        palette=None,
        **kwds,
    ):
        super().__init__()
        self.graph = graph
        self.vertex_drawer_factory = vertex_drawer_factory
        self.edge_drawer_factory = edge_drawer_factory
        self.kwds = kwds
        self.kwds["mark_groups"] = mark_groups
        self.kwds["palette"] = palette
        self.kwds["layout"] = layout

        self._kwds_post_update()

    def _kwds_post_update(self):
        self.kwds["layout"] = self.ensure_layout(self.kwds["layout"], self.graph)
        self.kwds["edge_curved"] = self._set_edge_curve(**self.kwds)
        self._clear_state()
        self.stale = True

    def _clear_state(self):
        self._vertices = []
        self._edges = []
        self._vertex_labels = []
        self._edge_labels = []
        self._group_artists = []
        self._legend_info = {}

    def get_children(self):
        artists = sum(
            [
                self._group_artists,
                self._edges,
                self._vertices,
                self._edge_labels,
                self._vertex_labels,
            ],
            [],
        )
        return tuple(artists)

    def _set_edge_curve(self, **kwds):
        graph = self.graph

        # Decide whether we need to calculate the curvature of edges
        # automatically -- and calculate them if needed.
        autocurve = kwds.get("autocurve", None)
        if autocurve or (
            autocurve is None
            and "edge_curved" not in kwds
            and "curved" not in self.graph.edge_attributes()
            and self.graph.ecount() < 10000
        ):
            from igraph import autocurve

            default = kwds.get("edge_curved", 0)
            if default is True:
                default = 0.5
            default = float(default)
            return autocurve(
                graph,
                attribute=None,
                default=default,
            )
        return None

    def get_vertices(self):
        """Get vertex artists."""
        return self._vertices

    def get_edges(self):
        """Get edge artists.

        Note that for directed edges, an edge might have more than one
        artist, e.g. arrow shaft and arrowhead.
        """
        return self._edges

    def get_groups(self):
        """Get group/cluster/cover artists."""
        return self._group_artists

    def get_vertex_labels(self):
        """Get vertex label artists."""
        return self._vertex_labels

    def get_edge_labels(self):
        """Get edge label artists."""
        return self._edge_labels

    def get_datalim(self):
        """Get limits on x/y axes based on the graph layout data.

        There is a small padding based on the size of the vertex marker to
        ensure it fits into the canvas.
        """
        import numpy as np

        layout = self.kwds["layout"]

        if len(layout) == 0:
            mins = np.array([0, 0])
            maxs = np.array([1, 1])
        else:
            mins = np.min(layout, axis=0).astype(float)
            maxs = np.max(layout, axis=0).astype(float)

            # Pad by vertex size, to ensure they fit
            vertex_builder = self.vertex_builder
            if vertex_builder.size is not None:
                mins -= vertex_builder.size * 1.1
                maxs += vertex_builder.size * 1.1
            else:
                mins[0] -= vertex_builder.width * 0.55
                mins[1] -= vertex_builder.height * 0.55
                maxs[0] += vertex_builder.width * 0.55
                maxs[1] += vertex_builder.height * 0.55

        return (mins, maxs)

    def _draw_vertex_labels(self):
        import numpy as np

        kwds = self.kwds
        layout = self.kwds["layout"]
        vertex_builder = self.vertex_builder
        vertex_order = self.vertex_order

        # Construct the iterator that we will use to draw the vertex labels
        if vertex_order is None:
            # Default vertex order
            vertex_coord_iter = zip(vertex_builder, layout)
        else:
            # Specified vertex order
            vertex_coord_iter = ((vertex_builder[i], layout[i]) for i in vertex_order)

        # Draw the vertex labels
        for vertex, coords in vertex_coord_iter:
            if vertex.label is None:
                continue

            label_size = kwds.get(
                "vertex_label_size",
                vertex.label_size,
            )

            # Locate text relative to vertex in data units. This is consistent
            # with the vertex size being in data units, but might be not fully
            # satisfactory when zooming in/out. In that case, revisit this
            # section
            dist = vertex.label_dist
            angle = vertex.label_angle
            if vertex.size is not None:
                vertex_width = vertex.size
                vertex_height = vertex.size
            else:
                vertex_width = vertex.width
                vertex_height = vertex.height
            xtext = coords[0] + dist * vertex_width * np.cos(angle)
            ytext = coords[1] + dist * vertex_height * np.sin(angle)
            xytext = (xtext, ytext)
            textcoords = "data"

            art = mpl.text.Annotation(
                vertex.label,
                coords,
                xytext=xytext,
                textcoords=textcoords,
                fontsize=label_size,
                ha="center",
                va="center",
                transform=self.axes.transData,
                clip_on=True,
                zorder=3,
            )
            self._vertex_labels.append(art)

    def _draw_edge_labels(self):
        graph = self.graph
        kwds = self.kwds
        vertex_builder = self.vertex_builder
        edge_builder = self.edge_builder
        edge_drawer = self.edge_drawer
        edge_order = self.edge_order or range(self.graph.ecount())

        labels = kwds.get("edge_label", None)
        if labels is None:
            return

        edge_label_iter = (
            (labels[i], edge_builder[i], graph.es[i]) for i in edge_order
        )
        for label, visual_edge, edge in edge_label_iter:
            # Ask the edge drawer to propose an anchor point for the label
            src, dest = edge.tuple
            src_vertex, dest_vertex = vertex_builder[src], vertex_builder[dest]
            (x, y), (halign, valign) = edge_drawer.get_label_position(
                visual_edge,
                src_vertex,
                dest_vertex,
            )

            text_kwds = {}
            text_kwds["ha"] = halign.value
            text_kwds["va"] = valign.value

            if visual_edge.background is not None:
                text_kwds["bbox"] = dict(
                    facecolor=visual_edge.background,
                    edgecolor="none",
                )
                text_kwds["ha"] = "center"
                text_kwds["va"] = "center"

            if visual_edge.align_label:
                # Rotate the text to align with the edge
                rotation = edge_drawer.get_label_rotation(
                    visual_edge,
                    src_vertex,
                    dest_vertex,
                )
                text_kwds["rotation"] = rotation

            art = mpl.text.Annotation(
                label,
                (x, y),
                fontsize=visual_edge.label_size,
                color=visual_edge.label_color,
                transform=self.axes.transData,
                clip_on=True,
                zorder=3,
                **text_kwds,
            )
            self._vertex_labels.append(art)

    def _draw_groups(self):
        """Draw the highlighted vertex groups, if requested"""
        # Deferred import to avoid a cycle in the import graph
        from igraph.clustering import VertexClustering, VertexCover

        kwds = self.kwds
        palette = self.kwds["palette"]
        layout = self.kwds["layout"]
        mark_groups = self.kwds["mark_groups"]
        vertex_builder = self.vertex_builder

        if not mark_groups:
            return

        # Figure out what to do with mark_groups in order to be able to
        # iterate over it and get memberlist-color pairs
        if isinstance(mark_groups, dict):
            # Dictionary mapping vertex indices or tuples of vertex
            # indices to colors
            group_iter = iter(mark_groups.items())
        elif isinstance(mark_groups, (VertexClustering, VertexCover)):
            # Vertex clustering
            group_iter = ((group, color) for color, group in enumerate(mark_groups))
        elif hasattr(mark_groups, "__iter__"):
            # One-off generators: we need to store the actual list for future
            # calls (e.g. resizing, recoloring, etc.). If we don't do this,
            # the generator is exhausted: we cannot rewind it.
            self.mark_groups = mark_groups = list(mark_groups)
            # Lists, tuples, iterators etc
            group_iter = iter(mark_groups)
        else:
            # False
            group_iter = iter({}.items())

        if kwds.get("legend", False):
            legend_info = {
                "handles": [],
                "labels": [],
            }

        # Iterate over color-memberlist pairs
        for group, color_id in group_iter:
            if not group or color_id is None:
                continue

            color = palette.get(color_id)

            if isinstance(group, VertexSeq):
                group = [vertex.index for vertex in group]
            if not hasattr(group, "__iter__"):
                raise TypeError("group membership list must be iterable")

            # Get the vertex indices that constitute the convex hull
            hull = [group[i] for i in convex_hull([layout[idx] for idx in group])]

            # Calculate the preferred rounding radius for the corners
            corner_radius = 1.25 * max(vertex_builder[idx].size for idx in hull)

            # Construct the polygon
            polygon = [layout[idx] for idx in hull]

            if len(polygon) == 2:
                # Expand the polygon (which is a flat line otherwise)
                a, b = Point(*polygon[0]), Point(*polygon[1])
                c = corner_radius * (a - b).normalized()
                n = Point(-c[1], c[0])
                polygon = [a + n, b + n, b - c, b - n, a - n, a + c]
            else:
                # Expand the polygon around its center of mass
                center = Point(
                    *[sum(coords) / float(len(coords)) for coords in zip(*polygon)]
                )
                polygon = [
                    Point(*point).towards(center, -corner_radius) for point in polygon
                ]

            # Draw the hull
            facecolor = (color[0], color[1], color[2], 0.25 * color[3])
            drawer = MatplotlibPolygonDrawer(self.axes)
            art = drawer.draw(
                polygon,
                corner_radius=corner_radius,
                facecolor=facecolor,
                edgecolor=color,
            )
            if art is not None:
                self._group_artists.append(art)

            if kwds.get("legend", False):
                legend_info["handles"].append(
                    plt.Rectangle(
                        (0, 0),
                        0,
                        0,
                        facecolor=facecolor,
                        edgecolor=color,
                    )
                )
                legend_info["labels"].append(str(color_id))

        if kwds.get("legend", False):
            self.legend_info = legend_info

    def _draw_vertices(self):
        """Draw the vertices"""
        graph = self.graph
        layout = self.kwds["layout"]
        vertex_drawer = self.vertex_drawer
        vertex_builder = self.vertex_builder
        vertex_order = self.vertex_order

        vs = graph.vs
        if vertex_order is None:
            # Default vertex order
            vertex_coord_iter = zip(vs, vertex_builder, layout)
        else:
            # Specified vertex order
            vertex_coord_iter = (
                (vs[i], vertex_builder[i], layout[i]) for i in vertex_order
            )
        for vertex, visual_vertex, coords in vertex_coord_iter:
            art = vertex_drawer.draw(visual_vertex, vertex, coords)
            self._vertices.append(art)

    def _draw_edges(self):
        """Draw the edges"""
        graph = self.graph
        vertex_builder = self.vertex_builder
        edge_drawer = self.edge_drawer
        edge_builder = self.edge_builder
        edge_order = self.edge_order

        es = graph.es
        if edge_order is None:
            # Default edge order
            edge_coord_iter = zip(es, edge_builder)
        else:
            # Specified edge order
            edge_coord_iter = ((es[i], edge_builder[i]) for i in edge_order)

        directed = graph.is_directed()
        if directed:
            # Arrows and the likes
            drawer_method = edge_drawer.draw_directed_edge
        else:
            # Lines
            drawer_method = edge_drawer.draw_undirected_edge
        for edge, visual_edge in edge_coord_iter:
            src, dest = edge.tuple
            src_vertex, dest_vertex = vertex_builder[src], vertex_builder[dest]
            arts = drawer_method(visual_edge, src_vertex, dest_vertex)
            self._edges.extend(arts)

    def _reprocess(self):
        """Prepare artist and children for the actual drawing.

        Children are not drawn here, but the dictionaries of properties are
        marshalled to their specific artists.
        """
        # clear state and mark as stale
        # since all children artists are part of the state, clearing it
        # will trigger a deletion by the backend at the next draw cycle
        self._clear_state()
        self.stale = True

        # get local refs to everything (just for less typing)
        graph = self.graph
        palette = self.kwds["palette"]
        layout = self.kwds["layout"]
        kwds = self.kwds

        # Construct the vertex, edge and label drawers
        self.vertex_drawer = self.vertex_drawer_factory(self.axes, palette, layout)
        self.edge_drawer = self.edge_drawer_factory(self.axes, palette)

        # Construct the visual vertex/edge builders based on the specifications
        # provided by the vertex_drawer and the edge_drawer
        self.vertex_builder = self.vertex_drawer.VisualVertexBuilder(graph.vs, kwds)
        self.edge_builder = self.edge_drawer.VisualEdgeBuilder(graph.es, kwds)

        # Determine the order in which we will draw the vertices and edges
        # These methods come from AbstractGraphDrawer
        self.vertex_order = self._determine_vertex_order(graph, kwds)
        self.edge_order = self._determine_edge_order(graph, kwds)

        self._draw_groups()
        self._draw_edges()
        self._draw_vertices()
        self._draw_vertex_labels()
        self._draw_edge_labels()

        # Forward mpl properties to children
        # TODO sort out all of the things that need to be forwarded
        for child in self.get_children():
            # set the figure / axes on child, this ensures each primitive
            # knows where to draw
            if hasattr(child, "set_figure"):
                child.set_figure(self.figure)
            child.axes = self.axes

            # forward the clippath/box to the children need this logic
            # because mpl exposes some fast-path logic
            clip_path = self.get_clip_path()
            if clip_path is None:
                clip_box = self.get_clip_box()
                child.set_clip_box(clip_box)
            else:
                child.set_clip_path(clip_path)

    @_stale_wrapper
    def draw(self, renderer, *args, **kwds):
        """Draw each of the children, with some buffering mechanism."""
        if not self.get_visible():
            return

        if not self.get_children():
            self._reprocess()

        # NOTE: looks like we have to manage the zorder ourselves
        children = list(self.get_children())
        children.sort(key=lambda x: x.zorder)
        for art in children:
            art.draw(renderer, *args, **kwds)

    def set(
        self,
        **kwds,
    ):
        """Set multiple parameters at once.

        The same options can be used as in the igraph.plot function.
        """
        if len(kwds) == 0:
            return

        self.kwds.update(kwds)
        self._kwds_post_update()

    def contains(self, mouseevent):
        """Track 'contains' event for mouse interactions."""
        props = {"vertices": [], "edges": []}
        hit = False
        for i, art in enumerate(self._edges):
            edge_hit = art.contains(mouseevent)[0]
            hit |= edge_hit
            props["edges"].append(i)

        for i, art in enumerate(self._vertices):
            vertex_hit = art.contains(mouseevent)[0]
            hit |= vertex_hit
            props["vertices"].append(i)

        return hit, props

    def pick(self, mouseevent):
        """Track 'pick' event for mouse interactions."""
        if self.pickable():
            picker = self.get_picker()
            if callable(picker):
                inside, prop = picker(self, mouseevent)
            else:
                inside, prop = self.contains(mouseevent)
            if inside:
                self.figure.canvas.pick_event(mouseevent, self, **prop)


class MatplotlibGraphDrawer(AbstractGraphDrawer):
    """Graph drawer that uses a pyplot.Axes as context"""

    _shape_dict = {
        "rectangle": "s",
        "circle": "o",
        "hidden": "none",
        "triangle-up": "^",
        "triangle-down": "v",
    }

    def __init__(
        self,
        ax,
        vertex_drawer_factory=MatplotlibVertexDrawer,
        edge_drawer_factory=MatplotlibEdgeDrawer,
    ):
        """Constructs the graph drawer and associates it with the mpl Axes

        @param ax: the matplotlib Axes to draw into.
        @param vertex_drawer_factory: a factory method that returns an
            L{AbstractVertexDrawer} instance bound to the given Matplotlib axes.
            The factory method must take three parameters: the axes and the
            palette to be used for drawing colored vertices, and the layout of
            the graph. The default vertex drawer is L{MatplotlibVertexDrawer}.
        @param edge_drawer_factory: a factory method that returns an
            L{AbstractEdgeDrawer} instance bound to a given Matplotlib Axes.
            The factory method must take two parameters: the Axes and the palette
            to be used for drawing colored edges. The default edge drawer is
            L{MatplotlibEdgeDrawer}.
        """
        self.ax = ax
        self.vertex_drawer_factory = vertex_drawer_factory
        self.edge_drawer_factory = edge_drawer_factory

    def draw(self, graph, *args, **kwds):
        if args:
            warn(
                "Positional arguments to plot functions are ignored "
                "and will be deprecated soon.",
                DeprecationWarning,
            )

        # Some abbreviations for sake of simplicity
        ax = self.ax

        # Create artist
        art = GraphArtist(
            graph,
            vertex_drawer_factory=self.vertex_drawer_factory,
            edge_drawer_factory=self.edge_drawer_factory,
            *args,
            **kwds,
        )

        # Bind artist to axes
        ax.add_artist(art)

        # Create children artists (this also binds them to the axes)
        art._reprocess()

        # Legend for groups
        if ("mark_groups" in kwds) and kwds.get("legend", False):
            ax.legend(
                art._legend_info["handles"],
                art._legend_info["labels"],
            )

        # Set new data limits
        ax.update_datalim(art.get_datalim())

        # Despine
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Set equal aspect to get actual circles
        ax.set_aspect(1)

        # Autoscale for x/y axis limits
        ax.autoscale_view()

        return art
