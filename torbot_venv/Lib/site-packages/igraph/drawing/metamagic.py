"""Auxiliary classes for the default graph drawer in igraph.

This module contains heavy metaclass magic. If you don't understand
the logic behind these classes, probably you don't need them either.

igraph's default graph drawer uses various data sources to determine
the visual appearance of vertices and edges. These data sources
are the following (in order of precedence):

  - The keyword arguments passed to the L{igraph.plot()} function
    (or to L{igraph.Graph.__plot__()} as a matter of fact, since
    L{igraph.plot()} just passes these attributes on). For instance,
    a keyword argument named C{vertex_label} can be used to set
    the labels of vertices.

  - The attributes of the vertices/edges being drawn. For instance,
    a vertex that has a C{label} attribute will use that label when
    drawn by the default graph drawer.

  - The global configuration of igraph. For instance, if the global
    L{igraph.config.Configuration} instance has a key called
    C{plotting.vertex_color}, that will be used as a default color
    for the vertices.

  - If all else fails, there is a built-in default; for instance,
    the default vertex color is C{"red"}. This is hard-wired in the
    source code.

The logic above can be useful in other graph drawers as well, not
only in the default one, therefore it is refactored into the classes
found in this module. Different graph drawers may inspect different
vertex or edge attributes, hence the classes that collect the attributes
from the various data sources are generated in run-time using a
metaclass called L{AttributeCollectorMeta}. You don't have to use
L{AttributeCollectorMeta} directly, just implement a subclass of
L{AttributeCollectorBase} and it will ensure that the appropriate
metaclass is used. With L{AttributeCollectorBase}, you can use a
simple declarative syntax to specify which attributes you are
interested in. For example::

    class VisualEdgeBuilder(AttributeCollectorBase):
        arrow_size = 1.0
        arrow_width = 1.0
        color = ("black", palette.get)
        width = 1.0

    for edge in VisualEdgeBuilder(graph.es):
        print edge.color

The above class is a visual edge builder -- a class that gives the
visual attributes of the edges of a graph that is specified at
construction time. It specifies that the attributes we are interested
in are C{arrow_size}, C{arrow_width}, C{color} and C{width}; the
default values are also given. For C{color}, we also specify that
a method called {palette.get} should be called on every attribute
value to translate color names to RGB values. For the other three
attributes, C{float} will implicitly be called on all attribute values,
this is inferred from the type of the default value itself.

@see: AttributeCollectorMeta, AttributeCollectorBase
"""

from configparser import NoOptionError


from igraph.configuration import Configuration

__all__ = ("AttributeSpecification", "AttributeCollectorBase")


class AttributeSpecification:
    """Class that describes how the value of a given attribute should be
    retrieved.

    The class contains the following members:

        - C{name}: the name of the attribute. This is also used when we
          are trying to get its value from a vertex/edge attribute of a
          graph.

        - C{alt_name}: alternative name of the attribute. This is used
          when we are trying to get its value from a Python dict or an
          L{igraph.Configuration} object. If omitted at construction time,
          it will be equal to C{name}.

        - C{default}: the default value of the attribute when none of
          the sources we try can provide a meaningful value.

        - C{transform}: optional transformation to be performed on the
          attribute value. If C{None} or omitted, it defaults to the
          type of the default value.

        - C{func}: when given, this function will be called with an
          index in order to derive the value of the attribute.
    """

    __slots__ = ("name", "alt_name", "default", "transform", "accessor", "func")

    def __init__(self, name, default=None, alt_name=None, transform=None, func=None):
        if isinstance(default, tuple):
            default, transform = default

        self.name = name
        self.default = default
        self.alt_name = alt_name or name
        self.transform = transform or None
        self.func = func
        self.accessor = None

        if self.transform and not hasattr(self.transform, "__call__"):
            raise TypeError("transform must be callable")

        if self.transform is None and self.default is not None:
            self.transform = type(self.default)


class AttributeCollectorMeta(type):
    """Metaclass for attribute collector classes

    Classes that use this metaclass are intended to collect vertex/edge
    attributes from various sources (a Python dict, a vertex/edge sequence,
    default values from the igraph configuration and such) in a given
    order of precedence. See the module documentation for more details.
    This metaclass enables the user to use a simple declarative syntax
    to specify which attributes he is interested in. For each vertex/edge
    attribute, a corresponding class attribute must be defined with a
    value that describes the default value of that attribute if no other
    data source provides us with any suitable value. The default value
    can also be a tuple; in that case, the first element of the tuple
    is the actual default value, the second element is a converter
    function that will convert the attribute values to a format expected
    by the caller who uses the class being defined.

    There is a special class attribute called C{_kwds_prefix}; this is
    not used as an attribute declaration. It can contain a string which
    will be used to derive alternative names for the attributes when
    the attribute is accessed in a Python dict. This is useful in many
    situations; for instance, the default graph drawer would want to access
    the vertex colors using the C{color} vertex attribute, but when
    it looks at the keyword arguments passed to the original call of
    L{igraph.Graph.__plot__}, the C{vertex_color} keyword argument should
    be looked up because we also have colors for the edges. C{_kwds_prefix}
    will be prepended to the attribute names when they are looked up in
    a dict of keyword arguments.

    If you require a more fine-tuned behaviour, you can assign an
    L{AttributeSpecification} instance to a class attribute directly.

    @see: AttributeCollectorBase
    """

    def __new__(mcs, name, bases, attrs):
        attr_specs = []
        for attr, value in attrs.items():
            if attr.startswith("_") or hasattr(value, "__call__"):
                continue
            if isinstance(value, AttributeSpecification):
                attr_spec = value
            elif isinstance(value, dict):
                attr_spec = AttributeSpecification(attr, **value)
            else:
                attr_spec = AttributeSpecification(attr, value)
            attr_specs.append(attr_spec)

        prefix = attrs.get("_kwds_prefix", None)
        if prefix:
            for attr_spec in attr_specs:
                if attr_spec.name == attr_spec.alt_name:
                    attr_spec.alt_name = "%s%s" % (prefix, attr_spec.name)

        attrs["_attributes"] = attr_specs
        attrs["Element"] = mcs.record_generator(
            "%s.Element" % name, (attr_spec.name for attr_spec in attr_specs)
        )

        return super().__new__(mcs, name, bases, attrs)

    @classmethod
    def record_generator(mcs, name, slots):
        """Generates a simple class that has the given slots and nothing else"""

        class Element:
            """A simple class that holds the attributes collected by the
            attribute collector"""

            __slots__ = tuple(slots)

            def __init__(self, attrs=()):
                for attr, value in attrs:
                    setattr(self, attr, value)

        Element.__name__ = name
        return Element


class AttributeCollectorBase(object, metaclass=AttributeCollectorMeta):
    """Base class for attribute collector subclasses. Classes that inherit
    this class may use a declarative syntax to specify which vertex or edge
    attributes they intend to collect. See L{AttributeCollectorMeta} for
    the details.
    """

    def __init__(self, seq, kwds=None):
        """Constructs a new attribute collector that uses the given
        vertex/edge sequence and the given dict as data sources.

        @param seq: an L{igraph.VertexSeq} or L{igraph.EdgeSeq} class
          that will be used as a data source for attributes.
        @param kwds: a Python dict that will be used to override the
          attributes collected from I{seq} if necessary.
        """
        elt = self.__class__.Element
        self._cache = [elt() for _ in range(len(seq))]

        self.seq = seq
        self.kwds = kwds or {}

        for attr_spec in self._attributes:
            values = self._collect_attributes(attr_spec)
            attr_name = attr_spec.name
            for cache_elt, val in zip(self._cache, values):
                setattr(cache_elt, attr_name, val)

    def _collect_attributes(self, attr_spec, config=None):
        """Collects graph visualization attributes from various sources.

        This method can be used to collect the attributes required for graph
        visualization from various sources. Attribute value sources are:

          - A specific value of a Python dict belonging to a given key. This dict
            is given by the argument M{self.kwds} at construction time, and
            the name of the key is determined by the argument specification
            given in M{attr_spec}.

          - A vertex or edge sequence of a graph, given in M{self.seq}

          - The global configuration, given in M{config}

          - A default value when all other sources fail to provide the value.
            This is also given in M{attr_spec}.

        @param  attr_spec: an L{AttributeSpecification} object which contains
                           the name of the attribute when it is coming from a
                           list of Python keyword arguments, the name of the
                           attribute when it is coming from the graph attributes
                           directly, the default value of the attribute and an
                           optional callable transformation to call on the values.
                           This can be used to ensure that the attributes are of
                           a given type.
        @param  config:    a L{Configuration} object to be used for determining the
                           defaults if all else fails. If C{None}, the global
                           igraph configuration will be used
        @return: the collected attributes
        """
        kwds = self.kwds
        seq = self.seq

        n = len(seq)

        # Special case if the attribute name is "label"
        if attr_spec.name == "label":
            if attr_spec.alt_name in kwds and kwds[attr_spec.alt_name] is None:
                return [None] * n

        # If the attribute uses an external callable to derive the attribute
        # values, call it and store the results
        if attr_spec.func is not None:
            func = attr_spec.func
            result = [func(i) for i in range(n)]
            return result

        # Get the configuration object
        if config is None:
            config = Configuration.instance()

        # Fetch the defaults from the vertex/edge sequence
        try:
            attrs = seq[attr_spec.name]
        except KeyError:
            attrs = None

        # Override them from the keyword arguments (if any)
        result = kwds.get(attr_spec.alt_name, None)
        if attrs:
            if not result:
                result = attrs
            else:
                if isinstance(result, str):
                    result = [result] * n
                try:
                    len(result)
                except TypeError:
                    result = [result] * n
                result = [result[idx] or attrs[idx] for idx in range(len(result))]

        # Special case for string overrides, strings are not treated
        # as sequences here
        if isinstance(result, str):
            result = [result] * n

        # If the result is still not a sequence, make it one
        try:
            len(result)
        except TypeError:
            result = [result] * n

        # If it is not a list, ensure that it is a list
        if not hasattr(result, "extend"):
            result = list(result)

        # Ensure that the length is n
        while len(result) < n:
            if len(result) <= n / 2:
                result.extend(result)
            else:
                result.extend(result[0 : (n - len(result))])

        # By now, the length of the result vector should be n as requested
        # Get the configuration defaults
        try:
            default = config["plotting.%s" % attr_spec.alt_name]
        except NoOptionError:
            default = None

        if default is None:
            default = attr_spec.default

        # Fill the None values with the default values
        for idx in range(len(result)):
            if result[idx] is None:
                result[idx] = default

        # Finally, do the transformation
        if attr_spec.transform is not None:
            transform = attr_spec.transform
            result = [transform(x) for x in result]

        return result

    def __getitem__(self, index):
        """Returns the collected attributes of the vertex/edge with the
        given index."""
        return self._cache[index]

    def __len__(self):
        return len(self.seq)
