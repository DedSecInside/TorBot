"""
Drawers for labels on plots.
"""

import re
from warnings import warn

from igraph.drawing.cairo.base import AbstractCairoDrawer

__all__ = ("CairoTextDrawer",)


class CairoTextDrawer(AbstractCairoDrawer):
    """Class that draws text on a Cairo context.

    This class supports multi-line text unlike the original Cairo text
    drawing methods."""

    LEFT, CENTER, RIGHT = "left", "center", "right"
    TOP, BOTTOM = "top", "bottom"

    def __init__(self, context, text="", halign="center", valign="center"):
        """Constructs a new instance that will draw the given C{text} on
        the given Cairo C{context}.
        """
        super().__init__(context, (0, 0))
        self.text = text
        self.halign = halign
        self.valign = valign

    def draw(self, wrap=False):
        """Draws the text in the current bounding box of the drawer.

        Since the class itself is an instance of L{AbstractCairoDrawer}, it
        has an attribute named C{bbox} which will be used as a bounding box.

        @param wrap: whether to allow re-wrapping of the text if it does not
            fit within the bounding box horizontally.
        """
        ctx = self.context
        bbox = self.bbox

        text_layout = self.get_text_layout(bbox.left, bbox.top, bbox.width, wrap)
        if not text_layout:
            return

        _, font_descent, line_height = ctx.font_extents()[:3]
        yb = ctx.text_extents(text_layout[0][2])[1]
        total_height = len(text_layout) * line_height

        if self.valign == self.BOTTOM:
            # Bottom vertical alignment
            dy = bbox.height - total_height - yb + font_descent
        elif self.valign == self.CENTER:
            # Centered vertical alignment
            dy = (bbox.height - total_height - yb + font_descent + line_height) / 2.0
        else:
            # Top vertical alignment
            dy = line_height

        for ref_x, ref_y, line in text_layout:
            ctx.move_to(ref_x, ref_y + dy)
            ctx.show_text(line)
        ctx.new_path()

    def get_text_layout(self, x=None, y=None, width=None, wrap=False):
        """Calculates the layout of the current text. C{x} and C{y} denote the
        coordinates where the drawing should start. If they are both C{None},
        the current position of the context will be used.

        Vertical alignment settings are not taken into account in this method
        as the text is not drawn within a box.

        @param x: The X coordinate of the reference point where the layout should
            start.
        @param y: The Y coordinate of the reference point where the layout should
            start.
        @param width: The width of the box in which the text will be fitted. It
            matters only when the text is right-aligned or centered. The text
            will overflow the box if any of the lines is longer than the box
            width and C{wrap} is C{False}.
        @param wrap: whether to allow re-wrapping of the text if it does not
            fit within the given width.

        @return: a list consisting of C{(x, y, line)} tuples where C{x} and
            C{y} refer to reference points on the Cairo canvas and C{line}
            refers to the corresponding text that should be plotted there.
        """
        ctx = self.context

        if x is None or y is None:
            x, y = ctx.get_current_point()

        line_height = ctx.font_extents()[2]

        if wrap and width and width > 0:
            iterlines = self._iterlines_wrapped(width)
        elif wrap:
            warn("ignoring wrap=True as no width was specified")
            iterlines = self._iterlines()
        else:
            iterlines = self._iterlines()

        result = []

        if self.halign == self.CENTER:
            # Centered alignment
            if width is None:
                width = self.text_extents()[2]
            for line, line_width, x_bearing in iterlines:
                result.append((x + (width - line_width) / 2.0 - x_bearing, y, line))
                y += line_height

        elif self.halign == self.RIGHT:
            # Right alignment
            if width is None:
                width = self.text_extents()[2]
            x += width
            for line, line_width, x_bearing in iterlines:
                result.append((x - line_width - x_bearing, y, line))
                y += line_height

        else:
            # Left alignment
            for line, _, x_bearing in iterlines:
                result.append((x - x_bearing, y, line))
                y += line_height

        return result

    def draw_at(self, x=None, y=None, width=None, wrap=False):
        """Draws the text by setting up an appropriate path on the Cairo
        context and filling it. C{x} and C{y} denote the coordinates where the
        drawing should start. If they are both C{None}, the current position
        of the context will be used.

        Vertical alignment settings are not taken into account in this method
        as the text is not drawn within a box.

        @param x: The X coordinate of the reference point where the layout should
            start.
        @param y: The Y coordinate of the reference point where the layout should
            start.
        @param width: The width of the box in which the text will be fitted. It
            matters only when the text is right-aligned or centered. The text
            will overflow the box if any of the lines is longer than the box
            width and C{wrap} is C{False}.
        @param wrap: whether to allow re-wrapping of the text if it does not
            fit within the given width.
        """
        ctx = self.context
        for ref_x, ref_y, line in self.get_text_layout(x, y, width, wrap):
            ctx.move_to(ref_x, ref_y)
            ctx.show_text(line)
        ctx.new_path()

    def _iterlines(self):
        """Iterates over the label line by line and returns a tuple containing
        the folloing for each line: the line itself, the width of the line and
        the X-bearing of the line."""
        ctx = self.context
        for line in self._text.split("\n"):
            xb, _, line_width, _, _, _ = ctx.text_extents(line)
            yield (line, line_width, xb)

    def _iterlines_wrapped(self, width):
        """Iterates over the label line by line and returns a tuple containing
        the folloing for each line: the line itself, the width of the line and
        the X-bearing of the line.

        The difference between this method and L{_iterlines()} is that this
        method is allowed to re-wrap the line if necessary.

        @param width: The width of the box in which the text will be fitted.
            Lines will be wrapped if they are wider than this width.
        """
        ctx = self.context
        for line in self._text.split("\n"):
            xb, _, line_width, _, _, _ = ctx.text_extents(line)
            if line_width <= width:
                yield (line, line_width, xb)
                continue

            # We have to wrap the line
            current_line, current_width, last_sep_width = [], 0, 0
            for match in re.finditer(r"(\S+)(\s+)?", line):
                word, sep = match.groups()
                word_width = ctx.text_extents(word)[4]
                if sep:
                    sep_width = ctx.text_extents(sep)[4]
                else:
                    sep_width = 0
                current_width += word_width
                if current_width >= width and current_line:
                    yield ("".join(current_line), current_width - word_width, 0)
                    # Starting a new line
                    current_line, current_width = [word], word_width
                    if sep is not None:
                        current_line.append(sep)
                else:
                    current_width += last_sep_width
                    current_line.append(word)
                    if sep is not None:
                        current_line.append(sep)
                last_sep_width = sep_width
            if current_line:
                yield ("".join(current_line), current_width, 0)

    @property
    def text(self):
        """Returns the text to be drawn."""
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text that will be drawn.

        If C{text} is C{None}, it will be mapped to an empty string; otherwise,
        it will be converted to a string."""
        if text is None:
            self._text = ""
        else:
            self._text = str(text)

    def text_extents(self):
        """Returns the X-bearing, Y-bearing, width, height, X-advance and
        Y-advance of the text.

        For multi-line text, the X-bearing and Y-bearing correspond to the
        first line, while the X-advance is extracted from the last line.
        and the Y-advance is the sum of all the Y-advances. The width and
        height correspond to the entire bounding box of the text."""
        lines = self.text.split("\n")
        if len(lines) <= 1:
            return self.context.text_extents(self.text)

        (
            x_bearing,
            y_bearing,
            width,
            height,
            x_advance,
            y_advance,
        ) = self.context.text_extents(lines[0])

        line_height = self.context.font_extents()[2]
        for line in lines[1:]:
            _, _, w, _, x_advance, ya = self.context.text_extents(line)
            width = max(width, w)
            height += line_height
            y_advance += ya

        return x_bearing, y_bearing, width, height, x_advance, y_advance


def test():
    """Testing routine for L{CairoTextDrawer}"""
    import math
    from igraph.drawing.cairo.utils import find_cairo
    from igraph.drawing.text import TextAlignment

    cairo = find_cairo()

    text = "The quick brown fox\njumps over a\nlazy dog"
    width, height = (600, 1000)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    drawer = CairoTextDrawer(context, text)

    context.set_source_rgb(1, 1, 1)
    context.set_font_size(16.0)
    context.rectangle(0, 0, width, height)
    context.fill()

    context.set_source_rgb(0.5, 0.5, 0.5)
    for i in range(200, width, 200):
        context.move_to(i, 0)
        context.line_to(i, height)
        context.stroke()
    for i in range(200, height, 200):
        context.move_to(0, i)
        context.line_to(width, i)
        context.stroke()
    context.set_source_rgb(0.75, 0.75, 0.75)
    context.set_line_width(0.5)
    for i in range(100, width, 200):
        context.move_to(i, 0)
        context.line_to(i, height)
        context.stroke()
    for i in range(100, height, 200):
        context.move_to(0, i)
        context.line_to(width, i)
        context.stroke()

    def mark_point(red, green, blue):
        """Marks the current point on the canvas by the given color"""
        x, y = context.get_current_point()
        context.set_source_rgba(red, green, blue, 0.5)
        context.arc(x, y, 4, 0, 2 * math.pi)
        context.fill()

    # Testing drawer.draw_at()
    alignments = TextAlignment.LEFT, TextAlignment.CENTER, TextAlignment.RIGHT
    for i, halign in enumerate(alignments):
        # Mark the reference points
        context.move_to(i * 200, 40)
        mark_point(0, 0, 1)
        context.move_to(i * 200, 140)
        mark_point(0, 0, 1)

        # Draw the text
        context.set_source_rgb(0, 0, 0)
        drawer.halign = halign
        drawer.draw_at(i * 200, 40)
        drawer.draw_at(i * 200, 140, width=200)

        # Mark the new reference point
        mark_point(1, 0, 0)

    # Testing TextDrawer.draw()
    for i, halign in enumerate(("left", "center", "right")):
        for j, valign in enumerate(("top", "center", "bottom")):
            # Draw the text
            context.set_source_rgb(0, 0, 0)
            drawer.halign = halign
            drawer.valign = valign
            drawer.bbox = (i * 200, j * 200 + 200, i * 200 + 200, j * 200 + 400)
            drawer.draw()
            # Mark the new reference point
            mark_point(1, 0, 0)

    # Testing TextDrawer.wrap()
    drawer.text = (
        "Jackdaws love my big sphinx of quartz. Yay, wrapping! "
        + "Jackdaws love my big sphinx of quartz.\n\n"
        + "Jackdaws  love  my  big  sphinx  of  quartz."
    )
    drawer.valign = TextAlignment.TOP
    for i, halign in enumerate(("left", "center", "right")):
        context.move_to(i * 200, 840)

        # Mark the reference point
        mark_point(0, 0, 1)

        # Draw the text
        context.set_source_rgb(0, 0, 0)
        drawer.halign = halign
        drawer.draw_at(i * 200, 840, width=199, wrap=True)

        # Mark the new reference point
        mark_point(1, 0, 0)

    surface.write_to_png("test.png")


if __name__ == "__main__":
    test()
