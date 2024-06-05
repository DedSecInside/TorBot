import gzip
import os

from shutil import copyfileobj
from warnings import warn

from igraph._igraph import GraphBase
from igraph.utils import (
    named_temporary_file,
)


def _identify_format(filename):
    """_identify_format(filename)

    Tries to identify the format of the graph stored in the file with the
    given filename. It identifies most file formats based on the extension
    of the file (and not on syntactic evaluation). The only exception is
    the adjacency matrix format and the edge list format: the first few
    lines of the file are evaluated to decide between the two.

    @note: Internal function, should not be called directly.

    @param filename: the name of the file or a file object whose C{name}
      attribute is set.
    @return: the format of the file as a string.
    """
    import os.path

    if hasattr(filename, "name") and hasattr(filename, "read"):
        # It is most likely a file
        try:
            filename = filename.name
        except Exception:
            return None

    root, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext == ".gz":
        _, ext2 = os.path.splitext(root)
        ext2 = ext2.lower()
        if ext2 == ".pickle":
            return "picklez"
        elif ext2 == ".graphml":
            return "graphmlz"

    if ext in [
        ".dimacs",
        ".dl",
        ".dot",
        ".edge",
        ".edges",
        ".edgelist",
        ".gml",
        ".graphml",
        ".graphmlz",
        ".gw",
        ".lgl",
        ".lgr",
        ".ncol",
        ".net",
        ".pajek",
        ".pickle",
        ".picklez",
        ".svg",
    ]:
        return ext[1:]

    if ext == ".txt" or ext == ".dat":
        # Most probably an adjacency matrix or an edge list
        f = open(filename, "r")
        line = f.readline()
        if line is None:
            return "edges"
        parts = line.strip().split()
        if len(parts) == 2:
            line = f.readline()
            if line is None:
                return "edges"
            parts = line.strip().split()
            if len(parts) == 2:
                line = f.readline()
                if line is None:
                    # This is a 2x2 matrix, it can be a matrix or an edge
                    # list as well and we cannot decide
                    return None
                else:
                    parts = line.strip().split()
                    if len(parts) == 0:
                        return None
                return "edges"
            else:
                # Not a matrix
                return None
        else:
            return "adjacency"


def _construct_graph_from_adjacency_file(
    cls, f, sep=None, comment_char="#", attribute=None, *args, **kwds
):
    """Constructs a graph based on an adjacency matrix from the given file.

    Additional positional and keyword arguments not mentioned here are
    passed intact to L{Graph.Adjacency}.

    @param f: the name of the file to be read or a file object
    @param sep: the string that separates the matrix elements in a row.
      C{None} means an arbitrary sequence of whitespace characters.
    @param comment_char: lines starting with this string are treated
      as comments.
    @param attribute: an edge attribute name where the edge weights are
      stored in the case of a weighted adjacency matrix. If C{None},
      no weights are stored, values larger than 1 are considered as
      edge multiplicities.
    @return: the created graph"""
    if isinstance(f, str):
        f = open(f)

    matrix, ri = [], 0
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith(comment_char):
            continue
        row = [float(x) for x in line.split(sep)]
        matrix.append(row)
        ri += 1

    f.close()

    if attribute is None:
        graph = cls.Adjacency(matrix, *args, **kwds)
    else:
        graph, weights = cls._Weighted_Adjacency(matrix, *args, **kwds)
        graph.es[attribute] = weights

    return graph


def _construct_graph_from_dimacs_file(cls, f, directed=False):
    """Reads a graph from a file conforming to the DIMACS minimum-cost flow
    file format.

    For the exact definition of the format, see
    U{http://lpsolve.sourceforge.net/5.5/DIMACS.htm}.

    Restrictions compared to the official description of the format are
    as follows:

      - igraph's DIMACS reader requires only three fields in an arc
        definition, describing the edge's source and target node and
        its capacity.
      - Source vertices are identified by 's' in the FLOW field, target
        vertices are identified by 't'.
      - Node indices start from 1. Only a single source and target node
        is allowed.

    @param f: the name of the file or a Python file handle
    @param directed: whether the generated graph should be directed.
    @return: the generated graph. The indices of the source and target
      vertices are attached as graph attributes C{source} and C{target},
      the edge capacities are stored in the C{capacity} edge attribute.
    """
    # Deferred import to avoid cycles
    from igraph import Graph

    graph, source, target, cap = super(Graph, cls).Read_DIMACS(f, directed)
    graph.es["capacity"] = cap
    graph["source"] = source
    graph["target"] = target
    return graph


def _construct_graph_from_graphmlz_file(cls, f, index=0):
    """Reads a graph from a zipped GraphML file.

    @param f: the name of the file
    @param index: if the GraphML file contains multiple graphs,
      specified the one that should be loaded. Graph indices
      start from zero, so if you want to load the first graph,
      specify 0 here.
    @return: the loaded graph object"""
    with named_temporary_file() as tmpfile:
        with open(tmpfile, "wb") as outf:
            copyfileobj(gzip.GzipFile(f, "rb"), outf)
        return cls.Read_GraphML(tmpfile, index=index)


def _construct_graph_from_pickle_file(cls, fname=None):
    """Reads a graph from Python pickled format

    @param fname: the name of the file, a stream to read from, or
      a string containing the pickled data.
    @return: the created graph object.
    """
    import pickle as pickle

    if hasattr(fname, "read"):
        # Probably a file or a file-like object
        result = pickle.load(fname)
    else:
        try:
            fp = open(fname, "rb")
        except UnicodeDecodeError:
            try:
                # We are on Python 3.6 or above and we are passing a pickled
                # stream that cannot be decoded as Unicode. Try unpickling
                # directly.
                result = pickle.loads(fname)
            except TypeError:
                raise IOError(
                    "Cannot load file. If fname is a file name, that "
                    "filename may be incorrect."
                )
        except IOError:
            try:
                # No file with the given name, try unpickling directly.
                result = pickle.loads(fname)
            except TypeError:
                raise IOError(
                    "Cannot load file. If fname is a file name, that "
                    "filename may be incorrect."
                )
        else:
            result = pickle.load(fp)
            fp.close()

    if not isinstance(result, cls):
        raise TypeError("unpickled object is not a %s" % cls.__name__)

    return result


def _construct_graph_from_picklez_file(cls, fname):
    """Reads a graph from compressed Python pickled format, uncompressing
    it on-the-fly.

    @param fname: the name of the file or a stream to read from.
    @return: the created graph object.
    """
    import pickle as pickle

    if hasattr(fname, "read"):
        # Probably a file or a file-like object
        if isinstance(fname, gzip.GzipFile):
            result = pickle.load(fname)
        else:
            result = pickle.load(gzip.GzipFile(mode="rb", fileobj=fname))
    else:
        result = pickle.load(gzip.open(fname, "rb"))

    if not isinstance(result, cls):
        raise TypeError("unpickled object is not a %s" % cls.__name__)

    return result


def _construct_graph_from_file(cls, f, format=None, *args, **kwds):
    """Unified reading function for graphs.

    This method tries to identify the format of the graph given in
    the first parameter and calls the corresponding reader method.

    The remaining arguments are passed to the reader method without
    any changes.

    @param f: the file containing the graph to be loaded
    @param format: the format of the file (if known in advance).
      C{None} means auto-detection. Possible values are: C{"ncol"}
      (NCOL format), C{"lgl"} (LGL format), C{"graphdb"} (GraphDB
      format), C{"graphml"}, C{"graphmlz"} (GraphML and gzipped
      GraphML format), C{"gml"} (GML format), C{"net"}, C{"pajek"}
      (Pajek format), C{"dimacs"} (DIMACS format), C{"edgelist"},
      C{"edges"} or C{"edge"} (edge list), C{"adjacency"}
      (adjacency matrix), C{"dl"} (DL format used by UCINET),
      C{"pickle"} (Python pickled format),
      C{"picklez"} (gzipped Python pickled format)
    @raises IOError: if the file format can't be identified and
      none was given.
    """
    if isinstance(f, os.PathLike):
        f = str(f)
    if format is None:
        format = _identify_format(f)
    try:
        reader = cls._format_mapping[format][0]
    except (KeyError, IndexError):
        raise IOError("unknown file format: %s" % str(format))
    if reader is None:
        raise IOError("no reader method for file format: %s" % str(format))
    reader = getattr(cls, reader)
    return reader(f, *args, **kwds)


def _write_graph_to_adjacency_file(graph, f, sep=" ", eol="\n", *args, **kwds):
    """Writes the adjacency matrix of the graph to the given file

    All the remaining arguments not mentioned here are passed intact
    to L{Graph.get_adjacency}.

    @param f: the name of the file to be written.
    @param sep: the string that separates the matrix elements in a row
    @param eol: the string that separates the rows of the matrix. Please
      note that igraph is able to read back the written adjacency matrix
      if and only if this is a single newline character
    """
    if isinstance(f, str):
        f = open(f, "w")
    matrix = graph.get_adjacency(*args, **kwds)
    for row in matrix:
        f.write(sep.join(map(str, row)))
        f.write(eol)
    f.close()


def _write_graph_to_dimacs_file(
    graph, f, source=None, target=None, capacity="capacity"
):
    """Writes the graph in DIMACS format to the given file.

    @param f: the name of the file to be written or a Python file handle.
    @param source: the source vertex ID. If C{None}, igraph will try to
      infer it from the C{source} graph attribute.
    @param target: the target vertex ID. If C{None}, igraph will try to
      infer it from the C{target} graph attribute.
    @param capacity: the capacities of the edges in a list or the name of
      an edge attribute that holds the capacities. If there is no such
      edge attribute, every edge will have a capacity of 1.
    """
    if source is None:
        try:
            source = graph["source"]
        except KeyError:
            raise ValueError(
                "source vertex must be provided in the 'source' graph "
                "attribute or in the 'source' argument of write_dimacs()"
            )

    if target is None:
        try:
            target = graph["target"]
        except KeyError:
            raise ValueError(
                "target vertex must be provided in the 'target' graph "
                "attribute or in the 'target' argument of write_dimacs()"
            )

    if isinstance(capacity, str) and capacity not in graph.edge_attributes():
        warn("'%s' edge attribute does not exist" % capacity)
        capacity = [1] * graph.ecount()

    return GraphBase.write_dimacs(graph, f, source, target, capacity)


def _write_graph_to_graphmlz_file(graph, f, compresslevel=9):
    """Writes the graph to a zipped GraphML file.

    The library uses the gzip compression algorithm, so the resulting
    file can be unzipped with regular gzip uncompression (like
    C{gunzip} or C{zcat} from Unix command line) or the Python C{gzip}
    module.

    Uses a temporary file to store intermediate GraphML data, so
    make sure you have enough free space to store the unzipped
    GraphML file as well.

    @param f: the name of the file to be written.
    @param compresslevel: the level of compression. 1 is fastest and
      produces the least compression, and 9 is slowest and produces
      the most compression."""
    with named_temporary_file() as tmpfile:
        graph.write_graphml(tmpfile)
        outf = gzip.GzipFile(f, "wb", compresslevel)
        copyfileobj(open(tmpfile, "rb"), outf)
        outf.close()


def _write_graph_to_pickle_file(graph, fname=None, version=-1):
    """Saves the graph in Python pickled format

    @param fname: the name of the file or a stream to save to. If
      C{None}, saves the graph to a string and returns the string.
    @param version: pickle protocol version to be used. If -1, uses
      the highest protocol available
    @return: C{None} if the graph was saved successfully to the
      given file, or a string if C{fname} was C{None}.
    """
    import pickle as pickle

    if fname is None:
        return pickle.dumps(graph, version)
    if not hasattr(fname, "write"):
        file_was_opened = True
        fname = open(fname, "wb")
    else:
        file_was_opened = False
    result = pickle.dump(graph, fname, version)
    if file_was_opened:
        fname.close()
    return result


def _write_graph_to_picklez_file(graph, fname=None, version=-1):
    """Saves the graph in Python pickled format, compressed with
    gzip.

    Saving in this format is a bit slower than saving in a Python pickle
    without compression, but the final file takes up much less space on
    the hard drive.

    @param fname: the name of the file or a stream to save to.
    @param version: pickle protocol version to be used. If -1, uses
      the highest protocol available
    @return: C{None} if the graph was saved successfully to the
      given file.
    """
    import pickle as pickle

    file_was_opened = False

    if not hasattr(fname, "write"):
        file_was_opened = True
        fname = gzip.open(fname, "wb")
    elif not isinstance(fname, gzip.GzipFile):
        file_was_opened = True
        fname = gzip.GzipFile(mode="wb", fileobj=fname)

    result = pickle.dump(graph, fname, version)

    if file_was_opened:
        fname.close()

    return result


def _write_graph_to_file(graph, f, format=None, *args, **kwds):
    """Unified writing function for graphs.

    This method tries to identify the format of the graph given in
    the first parameter (based on extension) and calls the corresponding
    writer method.

    The remaining arguments are passed to the writer method without
    any changes.

    @param f: the file containing the graph to be saved
    @param format: the format of the file (if one wants to override the
      format determined from the filename extension, or the filename itself
      is a stream). C{None} means auto-detection. Possible values are:

        - C{"adjacency"}: adjacency matrix format

        - C{"dimacs"}: DIMACS format

        - C{"dot"}, C{"graphviz"}: GraphViz DOT format

        - C{"edgelist"}, C{"edges"} or C{"edge"}: numeric edge list format

        - C{"gml"}: GML format

        - C{"graphml"} and C{"graphmlz"}: standard and gzipped GraphML
          format

        - C{"gw"}, C{"leda"}, C{"lgr"}: LEDA native format

        - C{"lgl"}: LGL format

        - C{"ncol"}: NCOL format

        - C{"net"}, C{"pajek"}: Pajek format

        - C{"pickle"}, C{"picklez"}: standard and gzipped Python pickled
          format

        - C{"svg"}: SVG format

    @raises IOError: if the file format can't be identified and
      none was given.
    """
    if isinstance(f, os.PathLike):
        f = str(f)
    if format is None:
        format = _identify_format(f)
    try:
        writer = graph._format_mapping[format][1]
    except (KeyError, IndexError):
        raise IOError("unknown file format: %s" % str(format))
    if writer is None:
        raise IOError("no writer method for file format: %s" % str(format))
    writer = getattr(graph, writer)
    return writer(f, *args, **kwds)
