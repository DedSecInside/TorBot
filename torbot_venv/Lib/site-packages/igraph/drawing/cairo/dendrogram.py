"""This module provides a dendrogram drawer for the Cairo backend."""

from math import pi

from igraph.drawing.utils import str_to_orientation

from .base import AbstractCairoDrawer

__all__ = ("CairoDendrogramDrawer",)


class CairoDendrogramDrawer(AbstractCairoDrawer):
    """Default Cairo drawer object for dendrograms."""

    def __init__(self, context, bbox, palette):
        """Constructs the drawer and associates it to the given palette.

        @param context: the context on which we will draw
        @param bbox:    the bounding box within which we will draw.
                        Can be anything accepted by the constructor
                        of L{BoundingBox} (i.e., a 2-tuple, a 4-tuple
                        or a L{BoundingBox} object).
        @param palette: the palette that can be used to map integer
                        color indices to colors when drawing vertices
        """
        super().__init__(context, bbox)
        self.palette = palette

    @staticmethod
    def _item_box_size(dendro, context, horiz, idx):
        """Calculates the amount of space needed for drawing an
        individual vertex at the bottom of the dendrogram."""
        if dendro._names is None or dendro._names[idx] is None:
            x_bearing, _, _, height, x_advance, _ = context.text_extents("")
        else:
            x_bearing, _, _, height, x_advance, _ = context.text_extents(
                str(dendro._names[idx])
            )

        if horiz:
            return x_advance - x_bearing, height
        return height, x_advance - x_bearing

    def _plot_item(self, dendro, context, horiz, idx, x, y):
        """Plots a dendrogram item to the given Cairo context

        @param context: the Cairo context we are plotting on
        @param horiz: whether the dendrogram is horizontally oriented
        @param idx: the index of the item
        @param x: the X position of the item
        @param y: the Y position of the item
        """
        if dendro._names is None or dendro._names[idx] is None:
            return

        height = self._item_box_size(dendro, context, True, idx)[1]
        if horiz:
            context.move_to(x, y + height)
            context.show_text(str(dendro._names[idx]))
        else:
            context.save()
            context.translate(x, y)
            context.rotate(-pi / 2.0)
            context.move_to(0, height)
            context.show_text(str(dendro._names[idx]))
            context.restore()

    def draw(self, dendro, **kwds):
        """Draws the given Dendrogram in a Cairo context.

        @param dendro: the igraph.Dendrogram to plot.

        It accepts the following keyword arguments:

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
        from igraph.layout import Layout

        context = self.context
        bbox = self.bbox

        if dendro._names is None:
            dendro._names = [str(x) for x in range(dendro._nitems)]

        orientation = str_to_orientation(
            kwds.get("orientation", "lr"), reversed_vertical=True
        )
        horiz = orientation in ("lr", "rl")

        # Get the font height
        font_height = context.font_extents()[2]

        # Calculate space needed for individual items at the
        # bottom of the dendrogram
        item_boxes = [
            self._item_box_size(dendro, context, horiz, idx) for idx in range(dendro._nitems)
        ]

        # Small correction for cases when the right edge of the labels is
        # aligned with the tips of the dendrogram branches
        ygap = 2 if orientation == "bt" else 0
        xgap = 2 if orientation == "lr" else 0
        item_boxes = [(x + xgap, y + ygap) for x, y in item_boxes]

        # Calculate coordinates
        layout = Layout([(0, 0)] * dendro._nitems, dim=2)
        inorder = dendro._traverse_inorder()
        if not horiz:
            x, y = 0, 0
            for idx, element in enumerate(inorder):
                layout[element] = (x, 0)
                x += max(font_height, item_boxes[element][0])

            for id1, id2 in dendro._merges:
                y += 1
                layout.append(((layout[id1][0] + layout[id2][0]) / 2.0, y))

            # Mirror or rotate the layout if necessary
            if orientation == "bt":
                layout.mirror(1)
        else:
            x, y = 0, 0
            for idx, element in enumerate(inorder):
                layout[element] = (0, y)
                y += max(font_height, item_boxes[element][1])

            for id1, id2 in dendro._merges:
                x += 1
                layout.append((x, (layout[id1][1] + layout[id2][1]) / 2.0))

            # Mirror or rotate the layout if necessary
            if orientation == "rl":
                layout.mirror(0)

        # Rescale layout to the bounding box
        maxw = max(e[0] for e in item_boxes)
        maxh = max(e[1] for e in item_boxes)

        # w, h: width and height of the area containing the dendrogram
        # tree without the items.
        # delta_x, delta_y: displacement of the dendrogram tree
        width, height = float(bbox.width), float(bbox.height)
        delta_x, delta_y = 0, 0
        if horiz:
            width -= maxw
            if orientation == "lr":
                delta_x = maxw
        else:
            height -= maxh
            if orientation == "tb":
                delta_y = maxh

        if horiz:
            delta_y += font_height / 2.0
        else:
            delta_x += font_height / 2.0
        layout.fit_into(
            (delta_x, delta_y, width - delta_x, height - delta_y),
            keep_aspect_ratio=False,
        )

        context.save()

        context.translate(bbox.left, bbox.top)
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.set_line_width(1)

        # Draw items
        if horiz:
            sgn = 0 if orientation == "rl" else -1
            for idx in range(dendro._nitems):
                x = layout[idx][0] + sgn * item_boxes[idx][0]
                y = layout[idx][1] - item_boxes[idx][1] / 2.0
                self._plot_item(dendro, context, horiz, idx, x, y)
        else:
            sgn = 1 if orientation == "bt" else 0
            for idx in range(dendro._nitems):
                x = layout[idx][0] - item_boxes[idx][0] / 2.0
                y = layout[idx][1] + sgn * item_boxes[idx][1]
                dendro._plot_item(dendro, context, horiz, idx, x, y)

        # Draw dendrogram lines
        if not horiz:
            for idx, (id1, id2) in enumerate(dendro._merges):
                x0, y0 = layout[id1]
                x1, y1 = layout[id2]
                x2, y2 = layout[idx + dendro._nitems]
                context.move_to(x0, y0)
                context.line_to(x0, y2)
                context.line_to(x1, y2)
                context.line_to(x1, y1)
                context.stroke()
        else:
            for idx, (id1, id2) in enumerate(dendro._merges):
                x0, y0 = layout[id1]
                x1, y1 = layout[id2]
                x2, y2 = layout[idx + dendro._nitems]
                context.move_to(x0, y0)
                context.line_to(x2, y0)
                context.line_to(x2, y1)
                context.line_to(x1, y1)
                context.stroke()

        context.restore()
