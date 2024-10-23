# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Utility functions that cannot be categorised anywhere else."""

from contextlib import contextmanager

from collections.abc import MutableMapping
from itertools import chain
from warnings import warn

import os
import tempfile

__all__ = (
    "dbl_epsilon",
    "deprecated",
    "multidict",
    "named_temporary_file",
    "numpy_to_contiguous_memoryview",
    "rescale",
    "safemin",
    "safemax",
)

__docformat__ = "restructuredtext en"


def deprecated(message):
    """Prints a warning message related to the deprecation of some igraph
    feature."""
    warn(message, DeprecationWarning, stacklevel=3)


def _is_running_in_ipython():
    """Internal function that determines whether igraph is running inside
    IPython or not."""
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


@contextmanager
def named_temporary_file(*args, **kwds):
    """Context manager that creates a named temporary file and
    returns its name.

    All parameters are passed on to ``tempfile.mkstemp``, see
    its documentation for more info.
    """
    handle, tmpfile = tempfile.mkstemp(*args, **kwds)
    os.close(handle)
    try:
        yield tmpfile
    finally:
        os.unlink(tmpfile)


def numpy_to_contiguous_memoryview(obj):
    """Converts a NumPy array or matrix into a contiguous memoryview object
    that is suitable to be forwarded to the Graph constructor.

    This is used internally to allow us to use a NumPy array or matrix
    directly when constructing a Graph.
    """
    # Deferred import to prevent a hard dependency on NumPy
    from numpy import int32, int64, require
    from igraph._igraph import INTEGER_SIZE

    if INTEGER_SIZE == 64:
        dtype = int64
    elif INTEGER_SIZE == 32:
        dtype = int32
    else:
        raise TypeError(
            f"size of igraph_integer_t in the C layer ({INTEGER_SIZE} bits) is not supported"
        )

    return memoryview(require(obj, dtype=dtype, requirements="AC"))


def rescale(values, out_range=(0.0, 1.0), in_range=None, clamp=False, scale=None):
    """Rescales a list of numbers into a given range.

    ``out_range`` gives the range of the output values; by default, the minimum
    of the original numbers in the list will be mapped to the first element
    in the output range and the maximum will be mapped to the second element.
    Elements between the minimum and maximum values in the input list will be
    interpolated linearly between the first and second values of the output
    range.

    ``in_range`` may be used to override which numbers are mapped to the first
    and second values of the output range. This must also be a tuple, where
    the first element will be mapped to the first element of the output range
    and the second element to the second.

    If ``clamp`` is ``True``, elements which are outside the given ``out_range``
    after rescaling are clamped to the output range to ensure that no number
    will be outside ``out_range`` in the result.

    If ``scale`` is not ``None``, it will be called for every element of ``values``
    and the rescaling will take place on the results instead. This can be used,
    for instance, to transform the logarithm of the original values instead of
    the actual values. A typical use-case is to map a range of values to color
    identifiers on a logarithmic scale. Scaling also applies to the ``in_range``
    parameter if present.

    :param out_range: the range of output values
    :param in_range: the range of the input values; this is the range that is mapped
        to ``out_range``. ``None`` means to use the minimum and maximum of
        the input, respectively.
    :param clamp: specifies what to do when an input value falls outside ``in_range``.
        ``True`` means to clamp the value to the bounds of ``in_range``,
        ``False`` means not to clamp.
    :param scale: an optional transformation to perform on the input values before
        mapping them to the output range.

    Examples:

        >>> rescale(range(5), (0, 8))
        [0.0, 2.0, 4.0, 6.0, 8.0]
        >>> rescale(range(5), (2, 10))
        [2.0, 4.0, 6.0, 8.0, 10.0]
        >>> rescale(range(5), (0, 4), (1, 3))
        [-2.0, 0.0, 2.0, 4.0, 6.0]
        >>> rescale(range(5), (0, 4), (1, 3), clamp=True)
        [0.0, 0.0, 2.0, 4.0, 4.0]
        >>> rescale([0]*5, (1, 3))
        [2.0, 2.0, 2.0, 2.0, 2.0]
        >>> from math import log10
        >>> rescale([1, 10, 100, 1000, 10000], (0, 8), scale=log10)
        [0.0, 2.0, 4.0, 6.0, 8.0]
        >>> rescale([1, 10, 100, 1000, 10000], (0, 4), (10, 1000), scale=log10)
        [-2.0, 0.0, 2.0, 4.0, 6.0]
    """
    if scale is not None:
        values = [scale(value) for value in values]

    if in_range is None:
        mi, ma = min(values), max(values)
    else:
        mi, ma = in_range
        if scale is not None:
            mi, ma = scale(mi), scale(ma)

    ratio = float(ma - mi)
    if not ratio:
        return [(out_range[0] + out_range[1]) / 2.0] * len(values)

    min_out, max_out = list(map(float, out_range))
    ratio = (max_out - min_out) / ratio
    result = [(x - mi) * ratio + min_out for x in values]

    if clamp:
        return [max(min(x, max_out), min_out) for x in result]
    else:
        return result


def consecutive_pairs(iterable, circular=False):
    """Returns consecutive pairs of items from the given iterable.

    When ``circular`` is ``True``, the pair consisting of the last
    and first elements is also returned.

    Example:

        >>> list(consecutive_pairs(range(5)))
        [(0, 1), (1, 2), (2, 3), (3, 4)]
        >>> list(consecutive_pairs(range(5), circular=True))
        [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
        >>> list(consecutive_pairs([]))
        []
        >>> list(consecutive_pairs([], circular=True))
        []
        >>> list(consecutive_pairs([0]))
        []
        >>> list(consecutive_pairs([0], circular=True))
        [(0, 0)]
    """
    it = iter(iterable)

    try:
        prev = next(it)
    except StopIteration:
        return
    first = prev

    for item in it:
        yield prev, item
        prev = item

    if circular:
        try:
            yield item, first
        except UnboundLocalError:
            yield first, first


class multidict(MutableMapping):
    """A dictionary-like object that is customized to deal with multiple
    values for the same key.

    Each value in this dictionary will be a list. Methods which emulate
    the methods of a standard Python ``dict`` object will return or manipulate
    the first items of the lists only. Special methods are provided to
    deal with keys having multiple values.
    """

    def __init__(self, *args, **kwds):
        self._dict = {}
        if len(args) > 1:
            raise ValueError(
                "%r expected at most 1 argument, got %d"
                % (self.__class__.__name__, len(args))
            )
        if args:
            args = args[0]
            self.update(args)
        self.update(kwds)

    def __contains__(self, key):
        """Returns whether there are any items associated to the given
        ``key``."""
        try:
            return len(self._dict[key]) > 0
        except KeyError:
            return False

    def __delitem__(self, key):
        """Removes all the items associated to the given ``key``."""
        del self._dict[key]

    def __getitem__(self, key):
        """Returns an arbitrary item associated to the given key. Raises ``KeyError``
        if no such key exists.

        Example:

            >>> d = multidict([("spam", "eggs"), ("spam", "bacon")])
            >>> d["spam"]
            'eggs'
        """
        try:
            return self._dict[key][0]
        except IndexError:
            raise KeyError(key)

    def __iter__(self):
        """Iterates over the keys of the multidict."""
        return iter(self._dict)

    def __len__(self):
        """Returns the number of distinct keys in this multidict."""
        return len(self._dict)

    def __setitem__(self, key, value):
        """Sets the item associated to the given ``key``. Any values associated to the
        key will be erased and replaced by ``value``.

        Example:

           >>> d = multidict([("spam", "eggs"), ("spam", "bacon")])
           >>> d["spam"] = "ham"
           >>> d["spam"]
           'ham'
        """
        self._dict[key] = [value]

    def add(self, key, value):
        """Adds `value` to the list of items associated to ``key``.

        Example:

            >>> d = multidict()
            >>> d.add("spam", "ham")
            >>> d["spam"]
            'ham'
            >>> d.add("spam", "eggs")
            >>> d.getlist("spam")
            ['ham', 'eggs']
        """
        try:
            self._dict[key].append(value)
        except KeyError:
            self._dict[key] = [value]

    def clear(self):
        """Removes all the items from the multidict."""
        self._dict.clear()

    def get(self, key, default=None):
        """Returns an arbitrary item associated to the given ``key``. If ``key``
        does not exist or has zero associated items, ``default`` will be
        returned."""
        try:
            items = self._dict[key]
            return items[0]
        except (KeyError, IndexError):
            return default

    def getlist(self, key):
        """Returns the list of values for the given ``key``. An empty list will
        be returned if there is no such key."""
        try:
            return self._dict[key]
        except KeyError:
            return []

    def iterlists(self):
        """Iterates over ``(key, values)`` pairs where ``values`` is the list
        of values associated with ``key``."""
        return iter(self._dict.items())

    def lists(self):
        """Returns a list of ``(key, values)`` pairs where ``values`` is the list
        of values associated with ``key``."""
        return list(self._dict.items())

    def update(self, arg, **kwds):
        if hasattr(arg, "keys") and callable(arg.keys):
            for key in arg.keys():
                self.add(key, arg[key])
        else:
            for key, value in arg:
                self.add(key, value)
        for key, value in kwds.items():
            self.add(key, value)


def safemax(iterable, default=0):
    """Safer variant of ``max()`` that returns a default value if the iterable
    is empty.

    Example:

        >>> safemax([-5, 6, 4])
        6
        >>> safemax([])
        0
        >>> safemax((), 2)
        2
    """
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return default
    else:
        return max(chain([first], it))


def safemin(iterable, default=0):
    """Safer variant of ``min()`` that returns a default value if the iterable
    is empty.

    Example:

        >>> safemin([-5, 6, 4])
        -5
        >>> safemin([])
        0
        >>> safemin((), 2)
        2
    """
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        return default
    else:
        return min(chain([first], it))


def dbl_epsilon():
    """Approximates the machine epsilon value for doubles."""
    epsilon = 1.0
    while 1.0 + epsilon / 2.0 != 1.0:
        epsilon /= 2
    return epsilon


dbl_epsilon = dbl_epsilon()
