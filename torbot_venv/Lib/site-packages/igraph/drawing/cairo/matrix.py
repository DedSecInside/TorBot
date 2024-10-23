"""This module provides implementation for a Cairo-specific matrix drawer."""

from itertools import islice
from math import pi

from igraph.drawing.cairo.base import AbstractCairoDrawer

__all__ = ("CairoMatrixDrawer",)


class CairoMatrixDrawer(AbstractCairoDrawer):
    """Default Cairo drawer object for matrices."""

    def __init__(self, context):
        """Constructs the vertex drawer and associates it to the given
        palette.

        @param context: the context on which we will draw
        """
        super().__init__(context, bbox=None)

    def draw(self, matrix, **kwds):
        """Draws the given Matrix in a Cairo context.

        @param matrix: the igraph.Matrix to plot.

        It accepts the following keyword arguments:

          - C{bbox}:    the bounding box within which we will draw.
            Can be anything accepted by the constructor of L{BoundingBox}
            (i.e., a 2-tuple, a 4-tuple or a L{BoundingBox} object).

          - C{palette}: the palette that can be used to map integer color
            indices to colors when drawing vertices

          - C{style}: the style of the plot. C{boolean} is useful for plotting
            matrices with boolean (C{True}/C{False} or 0/1) values: C{False}
            will be shown with a white box and C{True} with a black box.
            C{palette} uses the given palette to represent numbers by colors,
            the minimum will be assigned to palette color index 0 and the maximum
            will be assigned to the length of the palette. C{None} draws transparent
            cell backgrounds only. The default style is C{boolean} (but it may
            change in the future). C{None} values in the matrix are treated
            specially in both cases: nothing is drawn in the cell corresponding
            to C{None}.

          - C{square}: whether the cells of the matrix should be square or not.
            Default is C{True}.

          - C{grid_width}: line width of the grid shown on the matrix. If zero or
            negative, the grid is turned off. The grid is also turned off if the size
            of a cell is less than three times the given line width. Default is C{1}.
            Fractional widths are also allowed.

          - C{border_width}: line width of the border drawn around the matrix.
            If zero or negative, the border is turned off. Default is C{1}.

          - C{row_names}: the names of the rows

          - C{col_names}: the names of the columns.

          - C{values}: values to be displayed in the cells. If C{None} or
            C{False}, no values are displayed. If C{True}, the values come
            from the matrix being plotted. If it is another matrix, the
            values of that matrix are shown in the cells. In this case,
            the shape of the value matrix must match the shape of the
            matrix being plotted.

          - C{value_format}: a format string or a callable that specifies how
            the values should be plotted. If it is a callable, it must be a
            function that expects a single value and returns a string.
            Example: C{"%#.2f"} for floating-point numbers with always exactly
            two digits after the decimal point. See the Python documentation of
            the C{%} operator for details on the format string. If the format
            string is not given, it defaults to the C{str} function.

        If only the row names or the column names are given and the matrix
        is square-shaped, the same names are used for both column and row
        names.
        """
        context = self.context
        Matrix = matrix.__class__

        bbox = self.bbox = kwds.pop("bbox", None)
        palette = kwds.pop("palette", None)
        if bbox is None:
            raise ValueError("bbox is required for Cairo plots")
        if palette is None:
            raise ValueError("palette is required for Cairo plots")

        grid_width = float(kwds.get("grid_width", 1.0))
        border_width = float(kwds.get("border_width", 1.0))
        style = kwds.get("style", "boolean")
        row_names = kwds.get("row_names")
        col_names = kwds.get("col_names", row_names)
        values = kwds.get("values")
        value_format = kwds.get("value_format", str)

        # Validations
        if style not in ("boolean", "palette", "none", None):
            raise ValueError("invalid style")
        if style == "none":
            style = None
        if row_names is None and col_names is not None:
            row_names = col_names
        if row_names is not None:
            row_names = [str(name) for name in islice(row_names, matrix._nrow)]
            if len(row_names) < matrix._nrow:
                row_names.extend([""] * (matrix._nrow - len(row_names)))
        if col_names is not None:
            col_names = [str(name) for name in islice(col_names, matrix._ncol)]
            if len(col_names) < matrix._ncol:
                col_names.extend([""] * (matrix._ncol - len(col_names)))
        if values is False:
            values = None
        if values is True:
            values = matrix
        if isinstance(values, list):
            values = Matrix(list)
        if values is not None and not isinstance(values, Matrix):
            raise TypeError("values must be None, False, True or a matrix")
        if values is not None and values.shape != matrix.shape:
            raise ValueError("values must be a matrix of size %s" % matrix.shape)

        # Calculate text extents if needed
        if row_names is not None or col_names is not None:
            te = context.text_extents
            space_width = te(" ")[4]
            if row_names is not None:
                max_row_name_width = max([te(s)[4] for s in row_names]) + space_width
            else:
                max_row_name_width = 0
            if col_names is not None:
                max_col_name_width = max([te(s)[4] for s in col_names]) + space_width
            else:
                max_col_name_width = 0
        else:
            max_row_name_width, max_col_name_width = 0, 0
            space_width = 0

        # Calculate sizes
        total_width = float(bbox.width) - max_row_name_width
        total_height = float(bbox.height) - max_col_name_width
        dx = total_width / matrix.shape[1]
        dy = total_height / matrix.shape[0]
        if kwds.get("square", True):
            dx, dy = min(dx, dy), min(dx, dy)
        total_width, total_height = dx * matrix.shape[1], dy * matrix.shape[0]
        ox = bbox.left + (bbox.width - total_width - max_row_name_width) / 2.0
        oy = bbox.top + (bbox.height - total_height - max_col_name_width) / 2.0
        ox += max_row_name_width
        oy += max_col_name_width

        # Determine rescaling factors for the palette if needed
        if style == "palette":
            mi, ma = matrix.min(), matrix.max()
            color_offset = mi
            color_ratio = (len(palette) - 1) / float(ma - mi)
        else:
            color_offset, color_ratio = 0, 1

        # Validate grid width
        if dx < 3 * grid_width or dy < 3 * grid_width:
            grid_width = 0.0
        if grid_width > 0:
            context.set_line_width(grid_width)
        else:
            # When the grid width is zero, we will still stroke the
            # rectangles, but with the same color as the fill color
            # of the cell - otherwise we would get thin white lines
            # between the cells as a drawing artifact
            context.set_line_width(1)

        # Draw row names (if any)
        context.set_source_rgb(0.0, 0.0, 0.0)
        if row_names is not None:
            x, y = ox, oy
            for heading in row_names:
                _, _, _, h, xa, _ = context.text_extents(heading)
                context.move_to(x - xa - space_width, y + (dy + h) / 2.0)
                context.show_text(heading)
                y += dy

        # Draw column names (if any)
        if col_names is not None:
            context.save()
            context.translate(ox, oy)
            context.rotate(-pi / 2)
            x, y = 0.0, 0.0
            for heading in col_names:
                _, _, _, h, _, _ = context.text_extents(heading)
                context.move_to(x + space_width, y + (dx + h) / 2.0)
                context.show_text(heading)
                y += dx
            context.restore()

        # Draw matrix
        x, y = ox, oy
        if style is None:
            fill = lambda: None  # noqa: E731
        else:
            fill = context.fill_preserve
        for row in matrix:
            for item in row:
                if item is None:
                    x += dx
                    continue
                if style == "boolean":
                    if item:
                        context.set_source_rgb(0.0, 0.0, 0.0)
                    else:
                        context.set_source_rgb(1.0, 1.0, 1.0)
                elif style == "palette":
                    cidx = int((item - color_offset) * color_ratio)
                    if cidx < 0:
                        cidx = 0
                    context.set_source_rgba(*palette.get(cidx))
                context.rectangle(x, y, dx, dy)
                if grid_width > 0:
                    fill()
                    context.set_source_rgb(0.5, 0.5, 0.5)
                    context.stroke()
                else:
                    fill()
                    context.stroke()
                x += dx
            x, y = ox, y + dy

        # Draw cell values
        if values is not None:
            x, y = ox, oy
            context.set_source_rgb(0.0, 0.0, 0.0)
            for row in values.data:
                if hasattr(value_format, "__call__"):
                    values = [value_format(item) for item in row]
                else:
                    values = [value_format % item for item in row]
                for item in values:
                    th, tw = context.text_extents(item)[3:5]
                    context.move_to(x + (dx - tw) / 2.0, y + (dy + th) / 2.0)
                    context.show_text(item)
                    x += dx
                x, y = ox, y + dy

        # Draw borders
        if border_width > 0:
            context.set_line_width(border_width)
            context.set_source_rgb(0.0, 0.0, 0.0)
            context.rectangle(ox, oy, dx * matrix.shape[1], dy * matrix.shape[0])
            context.stroke()
