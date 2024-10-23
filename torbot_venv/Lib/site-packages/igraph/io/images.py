import math

from igraph.drawing import BoundingBox


def _write_graph_to_svg(
    graph,
    fname,
    layout="auto",
    width=None,
    height=None,
    labels="label",
    colors="color",
    shapes="shape",
    vertex_size=10,
    edge_colors="color",
    edge_stroke_widths="width",
    font_size=16,
    *args,
    **kwds
):
    """Saves the graph as an SVG (Scalable Vector Graphics) file

    The file will be Inkscape (http://inkscape.org) compatible.
    In Inkscape, as nodes are rearranged, the edges auto-update.

    @param fname: the name of the file or a Python file handle
    @param layout: the layout of the graph. Can be either an
      explicitly specified layout (using a list of coordinate
      pairs) or the name of a layout algorithm (which should
      refer to a method in the L{Graph} object, but without
      the C{layout_} prefix.
    @param width: the preferred width in pixels (default: 400)
    @param height: the preferred height in pixels (default: 400)
    @param labels: the vertex labels. Either it is the name of
      a vertex attribute to use, or a list explicitly specifying
      the labels. It can also be C{None}.
    @param colors: the vertex colors. Either it is the name of
      a vertex attribute to use, or a list explicitly specifying
      the colors. A color can be anything acceptable in an SVG
      file.
    @param shapes: the vertex shapes. Either it is the name of
      a vertex attribute to use, or a list explicitly specifying
      the shapes as integers. Shape 0 means hidden (nothing is drawn),
      shape 1 is a circle, shape 2 is a rectangle and shape 3 is a
      rectangle that automatically sizes to the inner text.
    @param vertex_size: vertex size in pixels
    @param edge_colors: the edge colors. Either it is the name
      of an edge attribute to use, or a list explicitly specifying
      the colors. A color can be anything acceptable in an SVG
      file.
    @param edge_stroke_widths: the stroke widths of the edges. Either
      it is the name of an edge attribute to use, or a list explicitly
      specifying the stroke widths. The stroke width can be anything
      acceptable in an SVG file.
    @param font_size: font size. If it is a string, it is written into
      the SVG file as-is (so you can specify anything which is valid
      as the value of the C{font-size} style). If it is a number, it
      is interpreted as pixel size and converted to the proper attribute
      value accordingly.
    """
    if width is None and height is None:
        width = 400
        height = 400
    elif width is None:
        width = height
    elif height is None:
        height = width

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    if isinstance(layout, str):
        layout = graph.layout(layout, *args, **kwds)

    if isinstance(labels, str):
        try:
            labels = graph.vs.get_attribute_values(labels)
        except KeyError:
            labels = [x + 1 for x in range(graph.vcount())]
    elif labels is None:
        labels = [""] * graph.vcount()

    if isinstance(colors, str):
        try:
            colors = graph.vs.get_attribute_values(colors)
        except KeyError:
            colors = ["red"] * graph.vcount()

    if isinstance(shapes, str):
        try:
            shapes = graph.vs.get_attribute_values(shapes)
        except KeyError:
            shapes = [1] * graph.vcount()

    if isinstance(edge_colors, str):
        try:
            edge_colors = graph.es.get_attribute_values(edge_colors)
        except KeyError:
            edge_colors = ["black"] * graph.ecount()

    if isinstance(edge_stroke_widths, str):
        try:
            edge_stroke_widths = graph.es.get_attribute_values(edge_stroke_widths)
        except KeyError:
            edge_stroke_widths = [2] * graph.ecount()

    if not isinstance(font_size, str):
        font_size = "%spx" % str(font_size)
    else:
        if ";" in font_size:
            raise ValueError("font size can't contain a semicolon")

    vcount = graph.vcount()
    labels.extend(str(i + 1) for i in range(len(labels), vcount))
    colors.extend(["red"] * (vcount - len(colors)))

    if isinstance(fname, str):
        f = open(fname, "w")
        our_file = True
    else:
        f = fname
        our_file = False

    bbox = BoundingBox(layout.bounding_box())

    sizes = [width - 2 * vertex_size, height - 2 * vertex_size]
    w, h = bbox.width, bbox.height

    ratios = []
    if w == 0:
        ratios.append(1.0)
    else:
        ratios.append(sizes[0] / w)
    if h == 0:
        ratios.append(1.0)
    else:
        ratios.append(sizes[1] / h)

    layout = [
        [
            (row[0] - bbox.left) * ratios[0] + vertex_size,
            (row[1] - bbox.top) * ratios[1] + vertex_size,
        ]
        for row in layout
    ]

    directed = graph.is_directed()

    print('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', file=f)
    print(
        "<!-- Created by igraph (http://igraph.org/) -->",
        file=f,
    )
    print(file=f)
    print(
        '<svg xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:cc="http://creativecommons.org/ns#" '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:svg="http://www.w3.org/2000/svg" '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"',
        file=f,
    )
    print('width="{0}px" height="{1}px">'.format(width, height), end=" ", file=f)

    edge_color_dict = {}
    print('<defs id="defs3">', file=f)
    for e_col in set(edge_colors):
        if e_col == "#000000":
            marker_index = ""
        else:
            marker_index = str(len(edge_color_dict))
        # Print an arrow marker for each possible line color
        # This is a copy of Inkscape's standard Arrow 2 marker
        print("<marker", file=f)
        print('   inkscape:stockid="Arrow2Lend{0}"'.format(marker_index), file=f)
        print('   orient="auto"', file=f)
        print('   refY="0.0"', file=f)
        print('   refX="0.0"', file=f)
        print('   id="Arrow2Lend{0}"'.format(marker_index), file=f)
        print('   style="overflow:visible;">', file=f)
        print("  <path", file=f)
        print('     id="pathArrow{0}"'.format(marker_index), file=f)
        print(
            '     style="font-size:12.0;fill-rule:evenodd;'
            "stroke-width:0.62500000;stroke-linejoin:round;"
            'fill:{0}"'.format(e_col),
            file=f,
        )
        print(
            '     d="M 8.7185878,4.0337352 L -2.2072895,0.016013256 '
            "L 8.7185884,-4.0017078 C 6.9730900,-1.6296469 "
            '6.9831476,1.6157441 8.7185878,4.0337352 z "',
            file=f,
        )
        print('     transform="scale(1.1) rotate(180) translate(1,0)" />', file=f)
        print("</marker>", file=f)

        edge_color_dict[e_col] = "Arrow2Lend{0}".format(marker_index)
    print("</defs>", file=f)
    print(
        '<g inkscape:groupmode="layer" id="layer2" inkscape:label="Lines" '
        'sodipodi:insensitive="true">',
        file=f,
    )

    for eidx, edge in enumerate(graph.es):
        vidxs = edge.tuple
        x1 = layout[vidxs[0]][0]
        y1 = layout[vidxs[0]][1]
        x2 = layout[vidxs[1]][0]
        y2 = layout[vidxs[1]][1]
        angle = math.atan2(y2 - y1, x2 - x1)
        x2 -= vertex_size * math.cos(angle)
        y2 -= vertex_size * math.sin(angle)

        print("<path", file=f)
        print(
            '    style="fill:none;stroke:{0};stroke-width:{2};'
            "stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;"
            'stroke-opacity:1;stroke-dasharray:none{1}"'.format(
                edge_colors[eidx],
                ";marker-end:url(#{0})".format(edge_color_dict[edge_colors[eidx]])
                if directed
                else "",
                edge_stroke_widths[eidx],
            ),
            file=f,
        )
        print('    d="M {0},{1} {2},{3}"'.format(x1, y1, x2, y2), file=f)
        print('    id="path{0}"'.format(eidx), file=f)
        print('    inkscape:connector-type="polyline"', file=f)
        print('    inkscape:connector-curvature="0"', file=f)
        print('    inkscape:connection-start="#g{0}"'.format(edge.source), file=f)
        print('    inkscape:connection-start-point="d4"', file=f)
        print('    inkscape:connection-end="#g{0}"'.format(edge.target), file=f)
        print('    inkscape:connection-end-point="d4" />', file=f)

    print("  </g>", file=f)
    print(file=f)

    print(
        '  <g inkscape:label="Nodes" \
                    inkscape:groupmode="layer" id="layer1">',
        file=f,
    )
    print("  <!-- Vertices -->", file=f)

    if any(x == 3 for x in shapes):
        # Only import tkFont if we really need it. Unfortunately, this will
        # flash up an unneccesary Tk window in some cases
        import tkinter.font
        import tkinter as tk

        # This allows us to dynamically size the width of the nodes.
        # Unfortunately this works only with font sizes specified in pixels.
        if font_size.endswith("px"):
            font_size_in_pixels = int(font_size[:-2])
        else:
            try:
                font_size_in_pixels = int(font_size)
            except Exception:
                raise ValueError(
                    "font sizes must be specified in pixels "
                    "when any of the nodes has shape=3 (i.e. "
                    "node size determined by text size)"
                )
        tk_window = tk.Tk()
        font = tkinter.font.Font(
            root=tk_window, font=("Sans", font_size_in_pixels, tkinter.font.NORMAL)
        )
    else:
        tk_window = None

    for vidx in range(graph.vcount()):
        print(
            '    <g id="g{0}" transform="translate({1},{2})">'.format(
                vidx, layout[vidx][0], layout[vidx][1]
            ),
            file=f,
        )
        if shapes[vidx] == 1:
            # Undocumented feature: can handle two colors but only for circles
            c = str(colors[vidx])
            if " " in c:
                c = c.split(" ")
                vs = str(vertex_size)
                print(
                    '     <path d="M -{0},0 A{0},{0} 0 0,0 {0},0 L \
                                -{0},0" fill="{1}"/>'.format(
                        vs, c[0]
                    ),
                    file=f,
                )
                print(
                    '     <path d="M -{0},0 A{0},{0} 0 0,1 {0},0 L \
                                -{0},0" fill="{1}"/>'.format(
                        vs, c[1]
                    ),
                    file=f,
                )
                print(
                    '     <circle cx="0" cy="0" r="{0}" fill="none"/>'.format(vs),
                    file=f,
                )
            else:
                print(
                    '     <circle cx="0" cy="0" r="{0}" fill="{1}"/>'.format(
                        str(vertex_size), str(colors[vidx])
                    ),
                    file=f,
                )
        elif shapes[vidx] == 2:
            print(
                '      <rect x="-{0}" y="-{0}" width="{1}" height="{1}" '
                'id="rect{2}" style="fill:{3};fill-opacity:1" />'.format(
                    vertex_size, vertex_size * 2, vidx, colors[vidx]
                ),
                file=f,
            )
        elif shapes[vidx] == 3:
            (vertex_width, vertex_height) = (
                font.measure(str(labels[vidx])) + 2,
                font.metrics("linespace") + 2,
            )
            print(
                '      <rect ry="5" rx="5" x="-{0}" y="-{1}" width="{2}" '
                'height="{3}" id="rect{4}" style="fill:{5};fill-opacity:1" '
                "/>".format(
                    vertex_width / 2.0,
                    vertex_height / 2.0,
                    vertex_width,
                    vertex_height,
                    vidx,
                    colors[vidx],
                ),
                file=f,
            )

        print(
            '      <text sodipodi:linespacing="125%" y="{0}" x="0" '
            'id="text{1}" style="font-size:{2};font-style:normal;'
            "font-weight:normal;text-align:center;line-height:125%;"
            "letter-spacing:0px;word-spacing:0px;text-anchor:middle;"
            "fill:#000000;fill-opacity:1;stroke:none;"
            'font-family:Sans">'.format(vertex_size / 2.0, vidx, font_size),
            file=f,
        )
        print(
            '<tspan y="{0}" x="0" id="tspan{1}" sodipodi:role="line">'
            "{2}</tspan></text>".format(vertex_size / 2.0, vidx, str(labels[vidx])),
            file=f,
        )
        print("    </g>", file=f)

    print("</g>", file=f)
    print(file=f)
    print("</svg>", file=f)

    if our_file:
        f.close()
    if tk_window:
        tk_window.destroy()
