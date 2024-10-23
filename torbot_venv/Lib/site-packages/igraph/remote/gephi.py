# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Classes that help igraph communicate with Gephi (http://www.gephi.org)."""

import json
import urllib.error
import urllib.parse
import urllib.request

__all__ = ("GephiConnection", "GephiGraphStreamer", "GephiGraphStreamingAPIFormat")
__docformat__ = "restructuredtext en"


class GephiConnection:
    """Object that represents a connection to a Gephi master server."""

    def __init__(self, url=None, host="127.0.0.1", port=8080, workspace=1):
        """Constructs a connection to a Gephi master server.

        The connection object can be constructed either by specifying the
        ``url`` directly, or by specifying the ``host``, ``port`` and
        ``workspace`` arguments.  The latter three are evaluated only if
        ``url`` is None; otherwise the ``url`` will take precedence.

        The ``url`` argument does not have to include the operation (e.g.,
        ``?operation=updateGraph``); the connection will take care of it.
        E.g., if you wish to connect to workspace 2 in a local Gephi instance
        on port 7341, the correct form to use for the ``url`` is as follows::

            http://localhost:7341/workspace0
        """
        self._pending_operations = []
        self._autoflush_threshold = 1024

        self.url = url or self._construct_default_url(host, port, workspace)

    def __del__(self):
        try:
            self.close()
        except urllib.error.URLError:
            # Happens when Gephi is closed before the connection is destroyed
            pass

    def _construct_default_url(self, host, port, workspace):
        return "http://%s:%d/workspace%d" % (host, port, workspace)

    def close(self):
        """Flushes all the pending operations to the Gephi master server in a
        single request."""
        self.flush()

    def flush(self):
        """Flushes all the pending operations to the Gephi master server in a
        single request."""
        data = b"".join(self._pending_operations)
        self._pending_operations = []
        conn = urllib.request.urlopen(self._update_url, data=data)
        return conn.read()

    @property
    def url(self):
        """The URL of the Gephi workspace where the data will be sent."""
        return self._url_root

    @url.setter
    def url(self, value):
        self._url_root = value
        self._get_url = self._url_root + "?operation=getGraph"
        self._update_url = self._url_root + "?operation=updateGraph"

    def write(self, data):
        """Sends the given raw data to the Gephi streaming master server in an HTTP
        POST request."""
        self._pending_operations.append(data)
        if len(self._pending_operations) >= self._autoflush_threshold:
            self.flush()

    def __repr__(self):
        return "%s(url=%r)" % (self.__class__.__name__, self.url)


class GephiGraphStreamingAPIFormat:
    """Object that implements the Gephi graph streaming API format and returns
    Python objects corresponding to the events defined in the API.
    """

    def get_add_node_event(self, identifier, attributes={}):
        """Generates a Python object corresponding to the event that adds a node
        with the given identifier and attributes in the Gephi graph streaming API.

        Example::

            >>> api = GephiGraphStreamingAPIFormat()
            >>> api.get_add_node_event("spam")
            {'an': {'spam': {}}}
            >>> api.get_add_node_event("spam", dict(ham="eggs"))
            {'an': {'spam': {'ham': 'eggs'}}}
        """
        return {"an": {identifier: attributes}}

    def get_add_edge_event(self, identifier, source, target, directed, attributes={}):
        """Generates a Python object corresponding to the event that adds an edge
        with the given source, target, directednessr and attributes in the Gephi
        graph streaming API.
        """
        result = dict(attributes)
        result["source"] = source
        result["target"] = target
        result["directed"] = bool(directed)
        return {"ae": {identifier: result}}

    def get_change_node_event(self, identifier, attributes):
        """Generates a Python object corresponding to the event that changes the
        attributes of some node in the Gephi graph streaming API. The given attributes
        are merged into the existing ones; use C{None} as the attribute value to
        delete a given attribute.

        Example::

            >>> api = GephiGraphStreamingAPIFormat()
            >>> api.get_change_node_event("spam", dict(ham="eggs"))
            {'cn': {'spam': {'ham': 'eggs'}}}
            >>> api.get_change_node_event("spam", dict(ham=None))
            {'cn': {'spam': {'ham': None}}}
        """
        return {"cn": {identifier: attributes}}

    def get_change_edge_event(self, identifier, attributes):
        """Generates a Python object corresponding to the event that changes the
        attributes of some edge in the Gephi graph streaming API. The given attributes
        are merged into the existing ones; use C{None} as the attribute value to
        delete a given attribute.

        Example::

            >>> api = GephiGraphStreamingAPIFormat()
            >>> api.get_change_edge_event("spam", dict(ham="eggs"))
            {'ce': {'spam': {'ham': 'eggs'}}}
            >>> api.get_change_edge_event("spam", dict(ham=None))
            {'ce': {'spam': {'ham': None}}}
        """
        return {"ce": {identifier: attributes}}

    def get_delete_node_event(self, identifier):
        """Generates a Python object corresponding to the event that deletes a
        node with the given identifier in the Gephi graph streaming API.

        Example::

            >>> api = GephiGraphStreamingAPIFormat()
            >>> api.get_delete_node_event("spam")
            {'dn': {'spam': {}}}
        """
        return {"dn": {identifier: {}}}

    def get_delete_edge_event(self, identifier):
        """Generates a Python object corresponding to the event that deletes an
        edge with the given identifier in the Gephi graph streaming API.

        Example::

            >>> api = GephiGraphStreamingAPIFormat()
            >>> api.get_delete_edge_event("spam:ham")
            {'de': {'spam:ham': {}}}
        """
        return {"de": {identifier: {}}}


class GephiGraphStreamer:
    """Class that produces JSON event objects that stream an igraph graph to
    Gephi using the Gephi Graph Streaming API.

    The Gephi graph streaming format is a simple JSON-based format that can be used
    to post mutations to a graph (i.e. node and edge additions, removals and updates)
    to a remote component. For instance, one can open up Gephi (http://www.gephi.org),
    install the Gephi graph streaming plugin and then send a graph from igraph
    straight into the Gephi window by using `GephiGraphStreamer` with the
    appropriate URL where Gephi is listening.

    Example::

        >>> from cStringIO import StringIO
        >>> from igraph import Graph
        >>> buf = StringIO()
        >>> streamer = GephiGraphStreamer()
        >>> graph = Graph.Formula("A --> B, B --> C")
        >>> streamer.post(graph, buf)
        >>> print(buf.getvalue())        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        {"an": {"igraph:...:v:0": {"name": "A"}}}
        {"an": {"igraph:...:v:1": {"name": "B"}}}
        {"an": {"igraph:...:v:2": {"name": "C"}}}
        {"ae": {"igraph:...:e:0:1": {...}}}
        {"ae": {"igraph:...:e:1:2": {...}}}
        <BLANKLINE>

    """

    def __init__(self, encoder=None):
        """Constructs a Gephi graph streamer that will post graphs to a
        given file-like object or a Gephi connection.

        ``encoder`` must either be ``None`` or an instance of ``json.JSONEncoder``
        and it must contain the JSON encoder to be used when posting JSON objects.
        """
        self.encoder = encoder or json.JSONEncoder(ensure_ascii=True)
        self.format = GephiGraphStreamingAPIFormat()

    def iterjsonobj(self, graph):
        """Iterates over the JSON objects that build up the graph using the
        Gephi graph streaming API. The objects returned from this function are
        Python objects; they must be formatted with ``json.dumps`` before
        sending them to the destination.
        """

        # Construct a unique ID prefix
        id_prefix = "igraph:%s" % (hex(id(graph)),)

        # Add the vertices
        add_node = self.format.get_add_node_event
        for vertex in graph.vs:
            yield add_node("%s:v:%d" % (id_prefix, vertex.index), vertex.attributes())

        # Add the edges
        add_edge = self.format.get_add_edge_event
        directed = graph.is_directed()
        for edge in graph.es:
            yield add_edge(
                "%s:e:%d:%d" % (id_prefix, edge.source, edge.target),
                "%s:v:%d" % (id_prefix, edge.source),
                "%s:v:%d" % (id_prefix, edge.target),
                directed,
                edge.attributes(),
            )

    def post(self, graph, destination, encoder=None):
        """Posts the given graph to the destination of the streamer using the
        given JSON encoder. When ``encoder`` is ``None``, it falls back to the
        default JSON encoder of the streamer in the `encoder` property.

        ``destination`` must be a file-like object or an instance of
        `GephiConnection`.
        """
        encoder = encoder or self.encoder
        for jsonobj in self.iterjsonobj(graph):
            self.send_event(jsonobj, destination, encoder=encoder, flush=False)
        destination.flush()

    def send_event(self, event, destination, encoder=None, flush=True):
        """Sends a single JSON event to the given destination using the given
        JSON encoder.  When ``encoder`` is ``None``, it falls back to the
        default JSON encoder of the streamer in the `encoder` property.

        ``destination`` must be a file-like object or an instance of
        `GephiConnection`.

        The method flushes the destination after sending the event. If you want
        to avoid this (e.g., because you are sending many events), set
        ``flush`` to ``False``.
        """
        encoder = encoder or self.encoder
        destination.write(encoder.encode(event).encode("utf-8"))
        destination.write(b"\r\n")
        if flush:
            destination.flush()
