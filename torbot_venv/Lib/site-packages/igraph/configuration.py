# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""
Configuration framework for igraph.

igraph has some parameters which usually affect the behaviour of many functions.
This module provides the framework for altering and querying igraph parameters
as well as saving them to and retrieving them from disk.
"""

import os.path

from configparser import ConfigParser


class Configuration:
    """Class representing igraph configuration details.

    Note that there is one primary instance of this class, which is used by
    igraph itself to retrieve configuration parameters when needed. You can
    access this instance with the L{instance()} method. You I{may} construct
    other instances by invoking the constructor directly, but these instances
    will I{not} affect igraph's behaviour. If you are interested in configuring
    igraph, use L{igraph.config} to get hold of the singleton instance and then
    modify it.

    General ideas
    =============

    The configuration of igraph is stored in the form of name-value pairs.
    This object provides an interface to the configuration data using the
    syntax known from dict:

      >>> c = Configuration()
      >>> c["general.verbose"] = True
      >>> print(c["general.verbose"])
      True

    Configuration keys are organized into sections, and the name to be used
    for a given key is always in the form C{section.keyname}, like
    C{general.verbose} in the example above. In that case, C{general} is the
    name of the configuration section, and C{verbose} is the name of the key.
    If the name of the section is omitted, it defaults to C{general}, so
    C{general.verbose} can be referred to as C{verbose}:

      >>> c = Configuration()
      >>> c["verbose"] = True
      >>> print(c["general.verbose"])
      True

    User-level configuration is stored in C{~/.igraphrc} per default on Linux
    and Mac OS X systems, or in C{C:\\Documents and Settings\\username\\.igraphrc}
    on Windows systems. However, this configuration is read only when C{igraph}
    is launched through its shell interface defined in L{igraph.app.shell}.
    This behaviour might change before version 1.0.

    Known configuration keys
    ========================

    The known configuration keys are presented below, sorted by section. When
    referring to them in program code, don't forget to add the section name,
    expect in the case of section C{general}.

    General settings
    ----------------

    These settings are all stored in section C{general}.

        - B{shells}: the list of preferred Python shells to be used with the
          command-line C{igraph} script. The shells in the list are tried one
          by one until any of them is found on the system. C{igraph} functions
          are then imported into the main namespace of the shell and the shell
          is launched. Known shells and their respective class names to be
          used can be found in L{igraph.app.shell}. Example:
          C{IPythonShell, ClassicPythonShell}. This is the default, by the way.
        - B{verbose}: whether L{igraph} should talk more than really necessary.
          For instance, if set to C{True}, some functions display progress bars.

    Plotting settings
    -----------------

    These settings specify the default values used by plotting functions.
    They are all stored in section C{plotting}.

        - B{backend}: either "cairo" if you want to use Cairo for plotting
          or "matplotlib" if you want to use the Matplotlib plotting backend.

        - B{layout}: default graph layout algorithm to be used.

        - B{mark_groups}: whether to mark the clusters by polygons when
          plotting a clustering object.

        - B{palette}: default palette to be used for converting integer
          numbers to colors. See L{colors.Palette} for more information.
          Valid palette names are stored in C{colors.palettes}.

        - B{wrap_labels}: whether to try to wrap the labels of the
          vertices automatically if they don't fit within the vertex.
          Default: C{False}.

    Shell settings
    --------------

    These settings specify options for external environments in which igraph is
    embedded (e.g., IPython and its Qt console). These settings are stored in
    section C{shell}.

        - B{ipython.inlining.Plot}: whether to show instances of the
          L{Plot<drawing.Plot>} class
          inline in IPython's console if the console supports it. Default: C{True}
    """

    class Types:
        """Static class for the implementation of custom getter/setter functions
        for configuration keys"""

        def __init__(self):
            pass

        @staticmethod
        def setboolean(obj, section, key, value):
            """Sets a boolean value in the given configuration object.

            @param obj: a configuration object
            @param section: the section of the value to be set
            @param key: the key of the value to be set
            @param value: the value itself. C{0}, C{false}, C{no} and C{off}
              means false, C{1}, C{true}, C{yes} and C{on} means true,
              everything else results in a C{ValueError} being thrown.
              Values are case insensitive
            """
            value = str(value).lower()
            if value in ("0", "false", "no", "off"):
                value = "false"
            elif value in ("1", "true", "yes", "on"):
                value = "true"
            else:
                raise ValueError("value cannot be coerced to boolean type")
            obj.set(section, key, value)

        @staticmethod
        def setint(obj, section, key, value):
            """Sets an integer value in the given configuration object.

            @param obj: a configuration object
            @param section: the section of the value to be set
            @param key: the key of the value to be set
            @param value: the value itself.
            """
            obj.set(section, key, str(int(value)))

        @staticmethod
        def setfloat(obj, section, key, value):
            """Sets a float value in the given configuration object.

            Note that float values are converted to strings in the configuration
            object, which may lead to some precision loss.

            @param obj: a configuration object
            @param section: the section of the value to be set
            @param key: the key of the value to be set
            @param value: the value itself.
            """
            obj.set(section, key, str(float(value)))

    _types = {
        "boolean": {"getter": ConfigParser.getboolean, "setter": Types.setboolean},
        "int": {"getter": ConfigParser.getint, "setter": Types.setint},
        "float": {"getter": ConfigParser.getfloat, "setter": Types.setfloat},
    }

    _sections = ("general", "apps", "plotting", "remote", "shell")
    _definitions = {
        "general.shells": {"default": "IPythonShell,ClassicPythonShell"},
        "general.verbose": {"default": True, "type": "boolean"},
        "plotting.backend": {"default": "cairo"},
        "plotting.layout": {"default": "auto"},
        "plotting.mark_groups": {"default": False, "type": "boolean"},
        "plotting.palette": {"default": "gray"},
        "plotting.wrap_labels": {"default": False, "type": "boolean"},
        "shell.ipython.inlining.Plot": {"default": True, "type": "boolean"},
    }

    # The singleton instance we are using throughout other modules
    _instance = None

    def __init__(self, filename=None):
        """Creates a new configuration instance.

        @param filename: file or file pointer to be read. Can be omitted.
        """
        self._config = ConfigParser()
        self._filename = None

        # Create default sections
        for sec in self._sections:
            self._config.add_section(sec)
        # Create default values
        for name, definition in self._definitions.items():
            if "default" in definition:
                self[name] = definition["default"]

        if filename is not None:
            self.load(filename)

    @property
    def filename(self):
        """Returns the filename associated to the object.

        It is usually the name of the configuration file that was used when
        creating the object. L{Configuration.load} always overwrites it with
        the filename given to it. If C{None}, the configuration was either
        created from scratch or it was updated from a stream without name
        information."""
        return self._filename

    def _get(self, section, key):
        """Internal function that returns the value of a given key in a
        given section."""
        definition = self._definitions.get("%s.%s" % (section, key), {})
        getter = None
        if "type" in definition:
            getter = self._types[definition["type"]].get("getter")
        if getter is None:
            getter = self._config.__class__.get
        return getter(self._config, section, key)

    @staticmethod
    def _item_to_section_key(item):
        """Converts an item description to a section-key pair.

        @param item: the item to be converted
        @return: if C{item} contains a period (C{.}), it is splitted into two parts
          at the first period, then the two parts are returned, so the part before
          the period is the section. If C{item} does not contain a period, the
          section is assumed to be C{general}, and the second part of the returned
          pair contains C{item} unchanged"""
        if "." in item:
            section, key = item.split(".", 1)
        else:
            section, key = "general", item
        return section, key

    def __contains__(self, item):
        """Checks whether the given configuration item is set.

        @param item: the configuration key to check.
        @return: C{True} if the key has an associated value, C{False} otherwise.
        """
        section, key = self._item_to_section_key(item)
        return self._config.has_option(section, key)

    def __getitem__(self, item):
        """Returns the given configuration item.

        @param item: the configuration key to retrieve.
        @return: the configuration value"""
        section, key = self._item_to_section_key(item)
        if key == "*":
            # Special case: retrieving all the keys within a section and
            # returning it in a dict
            keys = self._config.items(section)
            return dict((key, self._get(section, key)) for key, _ in keys)
        else:
            return self._get(section, key)

    def __setitem__(self, item, value):
        """Sets the given configuration item.

        @param item: the configuration key to set
        @param value: the new value of the configuration key
        """
        section, key = self._item_to_section_key(item)
        definition = self._definitions.get("%s.%s" % (section, key), {})
        setter = None
        if "type" in definition:
            setter = self._types[definition["type"]].get("setter", None)
        if setter is None:
            setter = self._config.__class__.set
        return setter(self._config, section, key, value)

    def __delitem__(self, item):
        """Deletes the given item from the configuration.

        If the item has a default value, the default value is written back instead
        of the current value. Without a default value, the item is really deleted.
        """
        section, key = self._item_to_section_key(item)
        definition = self._definitions.get("%s.%s" % (section, key), {})
        if "default" in definition:
            self[item] = definition["default"]
        else:
            self._config.remove_option(section, key)

    def has_key(self, item):
        """Checks if the configuration has a given key.

        @param item: the key being sought"""
        if "." in item:
            section, key = item.split(".", 1)
        else:
            section, key = "general", item
        return self._config.has_option(section, key)

    def load(self, stream=None):
        """Loads the configuration from the given file.

        @param stream: name of a file or a file object. The configuration will be loaded
          from here. Can be omitted, in this case, the user-level configuration is
          loaded.
        """
        stream = stream or get_user_config_file()
        if isinstance(stream, str):
            stream = open(stream, "r")
            file_was_open = True
        self._config.read_file(stream)
        self._filename = getattr(stream, "name", None)
        if file_was_open:
            stream.close()

    def save(self, stream=None):
        """Saves the configuration.

        @param stream: name of a file or a file object. The configuration will be saved
          there. Can be omitted, in this case, the user-level configuration file will
          be overwritten.
        """
        stream = stream or get_user_config_file()
        if not hasattr(stream, "write") or not hasattr(stream, "close"):
            stream = open(stream, "w")
            file_was_open = True
        self._config.write(stream)
        if file_was_open:
            stream.close()

    @classmethod
    def instance(cls):
        """Returns the single instance of the configuration object."""
        if cls._instance is None:
            cfile = get_user_config_file()
            try:
                config = cls(cfile)
            except IOError:
                # No config file yet, whatever
                config = cls()
            cls._instance = config
        return cls._instance


def get_user_config_file():
    """Returns the path where the user-level configuration file is stored"""
    return os.path.expanduser("~/.igraphrc")


def init():
    """Default mechanism to initiate igraph configuration

    This method loads the user-specific configuration file from the
    user's home directory, or if it does not exist, creates a default
    configuration.

    The method is safe to be called multiple times, it will not parse
    the configuration file twice.

    @return: the L{Configuration} object loaded or created."""
    return Configuration.instance()
