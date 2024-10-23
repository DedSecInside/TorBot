"""
Drawing and plotting routines for igraph.

IGraph has two stable plotting backends at the moment: Cairo and Matplotlib.
It also has experimental support for plotly.

The Cairo backend is dependent on the C{pycairo} or C{cairocffi} libraries that
provide Python bindings to the popular U{Cairo library<http://www.cairographics.org>}.
This means that if you don't have U{pycairo<http://www.cairographics.org/pycairo>}
or U{cairocffi<http://cairocffi.readthedocs.io>} installed, you won't be able
to use the Cairo plotting backend. Whenever the documentation refers to the
C{pycairo} library, you can safely replace it with C{cairocffi} as the two are
API-compatible.

The Matplotlib backend uses the U{Matplotlib library<https://matplotlib.org>}.
You will need to install it from PyPI if you want to use the Matplotlib
plotting backend. Many of our gallery examples use the matplotlib backend.

The plotly backend uses the U{plotly library <https://plotly.com/python/>} and,
like matplotlib, requires installation from PyPI.

If you do not want to (or cannot) install any of the dependencies outlined
above, you can still save the graph to an SVG file and view it from
U{Mozilla Firefox<http://www.mozilla.org/firefox>} (free) or edit it in
U{Inkscape<http://www.inkscape.org>} (free), U{Skencil<http://www.skencil.org>}
(formerly known as Sketch, also free) or Adobe Illustrator.
"""


from pathlib import Path
from warnings import warn

from igraph.configuration import Configuration
from igraph.drawing.cairo.utils import find_cairo
from igraph.drawing.matplotlib.utils import find_matplotlib
from igraph.drawing.plotly.utils import find_plotly
from igraph.drawing.cairo.plot import CairoPlot
from igraph.drawing.colors import Palette, palettes

from igraph.drawing.cairo.graph import CairoGraphDrawer
from igraph.drawing.cairo.matrix import CairoMatrixDrawer
from igraph.drawing.cairo.histogram import CairoHistogramDrawer
from igraph.drawing.cairo.palette import CairoPaletteDrawer
from igraph.drawing.matplotlib.graph import MatplotlibGraphDrawer
from igraph.drawing.matplotlib.matrix import MatplotlibMatrixDrawer
from igraph.drawing.matplotlib.histogram import MatplotlibHistogramDrawer
from igraph.drawing.matplotlib.palette import MatplotlibPaletteDrawer
from igraph.drawing.plotly.graph import PlotlyGraphDrawer

from igraph.drawing.utils import BoundingBox, Point, Rectangle
from igraph.utils import _is_running_in_ipython

__all__ = (
    "BoundingBox",
    "CairoGraphDrawer",
    "MatplotlibGraphDrawer",
    "DefaultGraphDrawer",
    "Plot",
    "Point",
    "Rectangle",
    "plot",
    "DrawerDirectory",
)

# TODO: deprecate
Plot = CairoPlot

# TODO: deprecate
DefaultGraphDrawer = CairoGraphDrawer


class DrawerDirectory:
    """Static class that finds the object/backend drawer

    This directory is used by the __plot__ functions.
    """

    valid_backends = ("cairo", "matplotlib")
    valid_objects = (
        "Graph",
        "Matrix",
        "Histogram",
        "Palette",
    )
    known_drawers = {
        "cairo": {
            "Graph": CairoGraphDrawer,
            "Matrix": CairoMatrixDrawer,
            "Histogram": CairoHistogramDrawer,
            "Palette": CairoPaletteDrawer,
        },
        "matplotlib": {
            "Graph": MatplotlibGraphDrawer,
            "Matrix": MatplotlibMatrixDrawer,
            "Histogram": MatplotlibHistogramDrawer,
            "Palette": MatplotlibPaletteDrawer,
        },
        "plotly": {
            "Graph": PlotlyGraphDrawer,
        },
    }

    @classmethod
    def resolve(cls, obj, backend):
        """Given a shape name, returns the corresponding shape drawer class

        @param cls: the class to resolve
        @param obj: an instance of the object to plot
        @param backend: the name of the backend
        @return: the corresponding shape drawer class

        @raise ValueError: if no drawer is available for this backend/object
        """
        object_name = str(obj.__class__).split(".")[-1].strip("<'>")

        try:
            return cls.known_drawers[backend][object_name]
        except KeyError:
            raise ValueError(
                f"unknown drawer for {object_name} and backend {backend}",
            )


def plot(obj, target=None, bbox=(0, 0, 600, 600), *args, **kwds):
    """Plots the given object to the given target.

    Positional and keyword arguments not explicitly mentioned here will be
    passed down to the C{__plot__} method of the object being plotted.
    Since you are most likely interested in the keyword arguments available
    for graph plots, see L{Graph.__plot__} as well.

    @param obj: the object to be plotted
    @param target: the target where the object should be plotted. It can be one
      of the following types:

        - C{matplotib.axes.Axes} -- a matplotlib/pyplot axes in which the
          graph will be plotted. Drawing is delegated to the chosen matplotlib
          backend, and you can use interactive backends and matplotlib
          functions to save to file as well.

        - C{string} -- a file with the given name will be created and the plot
          will be stored there. If you are using the Cairo backend, an
          appropriate Cairo surface will be attached to the file. If you are
          using the matplotlib backend, the Figure will be saved to that file
          using Figure.savefig with default parameters. The supported image
          formats for Cairo are: PNG, PDF, SVG and PostScript; matplotlib might
          support additional formats.

        - C{cairo.Surface} -- the given Cairo surface will be used. This can
          refer to a PNG image, an arbitrary window, an SVG file, anything that
          Cairo can handle.

        - C{None} -- If you are using the Cairo backend, no plotting will be
          performed; igraph simply returns a CairoPlot_ object that you can use
          to manipulate the plot and save it to a file later. If you are using
          the matplotlib backend, a Figure objet and an Axes are created and
          the Axes is returned so you can manipulate it further. Similarly, if
          you are using the plotly backend, a Figure object is returned.

    @param bbox: the bounding box of the plot. It must be a tuple with either
      two or four integers, or a L{BoundingBox} object. If this is a tuple
      with two integers, it is interpreted as the width and height of the plot
      (in pixels for PNG images and on-screen plots, or in points for PDF,
      SVG and PostScript plots, where 72 pt = 1 inch = 2.54 cm). If this is
      a tuple with four integers, the first two denotes the X and Y coordinates
      of a corner and the latter two denoting the X and Y coordinates of the
      opposite corner. Ignored for Matplotlib plots.

    @keyword opacity: the opacity of the object being plotted. It can be
      used to overlap several plots of the same graph if you use the same
      layout for them -- for instance, you might plot a graph with opacity
      0.5 and then plot its spanning tree over it with opacity 0.1. To
      achieve this, you'll need to modify the L{Plot} object returned with
      L{Plot.add}. Ignored for Matplotlib plots.

    @keyword palette: the palette primarily used on the plot if the
      added objects do not specify a private palette. Must be either
      an L{igraph.drawing.colors.Palette} object or a string referring
      to a valid key of C{igraph.drawing.colors.palettes} (see module
      L{igraph.drawing.colors}) or C{None}. In the latter case, the default
      palette given by the configuration key C{plotting.palette} is used.

    @keyword margin: the top, right, bottom, left margins as a 4-tuple.
      If it has less than 4 elements or is a single float, the elements
      will be re-used until the length is at least 4. The default margin
      is 20 units on each side. Ignored for Matplotlib plots.

    @keyword inline: whether to try and show the plot object inline in the
      current IPython notebook. Passing C{None} here or omitting this keyword
      argument will look up the preferred behaviour from the
      C{shell.ipython.inlining.Plot} configuration key.  Note that this keyword
      argument has an effect only if igraph is run inside IPython and C{target}
      is C{None}.

    @keyword backend: the plotting backend to use; one of C{"cairo"},
      C{"matplotlib"} or C{"plotly"}. C{None} means to try to decide the backend
      from the plotting target and the default igraph configuration object.

    @return: an appropriate L{CairoPlot} object for the Cairo backend, the
      Matplotlib C{Axes} object for the Matplotlib backend, and the C{Figure}
      object for the plotly backend.

    @see: Graph.__plot__
    """

    VALID_BACKENDS = ("cairo", "matplotlib", "plotly")

    _, plt = find_matplotlib()
    cairo = find_cairo()
    plotly = find_plotly()

    backend = kwds.pop("backend", None)

    # Switch backend based on target (first) and config (second) if it was not
    # selected explicitly
    if backend is not None:
        pass
    elif hasattr(plt, "Axes") and isinstance(target, plt.Axes):
        backend = "matplotlib"
    elif hasattr(plotly, "graph_objects") and isinstance(
        target, plotly.graph_objects.Figure
    ):
        backend = "plotly"
    elif hasattr(cairo, "Surface") and isinstance(target, cairo.Surface):
        backend = "cairo"
    else:
        backend = Configuration.instance()["plotting.backend"]

    if backend not in VALID_BACKENDS:
        raise ValueError(f"unknown plotting backend: {backend!r}")

    if backend in ("matplotlib", "plotly"):
        # Choose palette
        # If explicit, use it. If not or None, ask the object: None is an
        # acceptable response from the object (e.g. for clusterings), it means
        # the palette is handled internally. If no response, default to config.
        palette = kwds.pop("palette", None)
        if palette is None:
            palette = getattr(
                obj,
                "_default_palette",
                Configuration.instance()["plotting.palette"],
            )
        if palette is not None and not isinstance(palette, Palette):
            palette = palettes[palette]

        if isinstance(target, (str, Path)):
            save_path = str(target)
            target = None
        else:
            save_path = None

        if target is None:
            if backend == "matplotlib":
                # Create a new axes if needed
                _, target = plt.subplots()
            elif backend == "plotly":
                # Create a new figure if needed
                target = plotly.graph_objects.Figure()

        # Get the plotting function from the object
        plotter = getattr(obj, "__plot__", None)
        if plotter is None:
            warn("%s does not support plotting" % (obj,))
            return
        else:
            result = plotter(
                backend,
                target,
                palette=palette,
                *args,
                **kwds,
            )
            # NOTE: for matplotlib, result is the container Artist. It would be
            # good to return this instead of target, like we do for Cairo.
            # However, that breaks API so let's wait for a major release

            if save_path is not None:
                if backend == "matplotlib":
                    target.figure.savefig(save_path)
                elif backend == "plotly":
                    target.write_image(save_path)

            return target

    # Cairo backend
    inline = False
    if target is None and _is_running_in_ipython():
        inline = kwds.get("inline")
        if inline is None:
            inline = Configuration.instance()["shell.ipython.inlining.Plot"]

    palette = kwds.pop("palette", None)
    background = kwds.pop("background", "white")
    margin = float(kwds.pop("margin", 20))
    result = CairoPlot(
        target=target,
        bbox=bbox,
        palette=palette,
        background=background,
    )
    item_bbox = result.bbox.contract(margin)
    result.add(obj, item_bbox, *args, **kwds)

    # If we requested an inline plot, just return the result and IPython will
    # call its _repr_svg_ method. If we requested a non-inline plot, show the
    # plot in a separate window and return nothing
    if inline:
        return result

    # We are either not in IPython or the user specified an explicit plot target,
    # so just show or save the result

    if isinstance(target, (str, Path)):
        # save
        result.save()

    # Also return the plot itself
    return result
