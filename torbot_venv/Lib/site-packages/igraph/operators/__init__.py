# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Implementation of union, disjoint union and intersection operators."""

__all__ = (
    "disjoint_union",
    "union",
    "intersection",
    "operator_method_registry",
)

from igraph.operators.functions import (
    disjoint_union,
    union,
    intersection,
)
from igraph.operators.methods import (
    __iadd__,
    __add__,
    __and__,
    __isub__,
    __sub__,
    __mul__,
    __or__,
    _disjoint_union,
    _union,
    _intersection,
)

operator_method_registry = {
    "__iadd__": __iadd__,
    "__add__": __add__,
    "__and__": __and__,
    "__isub__": __isub__,
    "__sub__": __sub__,
    "__mul__": __mul__,
    "__or__": __or__,
    "disjoint_union": _disjoint_union,
    "union": _union,
    "intersection": _intersection,
}
