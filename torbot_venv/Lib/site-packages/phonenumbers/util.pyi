from collections.abc import Callable
from typing import Any, overload

from _typeshed import SupportsWrite

unicod: type[str]
u: type[str]
to_long: type[int]

@overload
def prnt(
    *values: object,
    sep: str | None = ...,
    end: str | None = ...,
    file: SupportsWrite[str] | None = ...,
) -> None: ...
@overload
def prnt(*values: object, **kwargs: Any) -> None: ...

class UnicodeMixin:
    def __str__(self) -> str: ...

U_EMPTY_STRING: str
U_SPACE: str
U_DASH: str
U_TILDE: str
U_PLUS: str
U_STAR: str
U_ZERO: str
U_SLASH: str
U_SEMICOLON: str
U_X_LOWER: str
U_X_UPPER: str
U_PERCENT: str

def rpr(s: str | None) -> str: ...
@overload
def force_unicode(s: None) -> None: ...
@overload
def force_unicode(s: str) -> str: ...

class ImmutableMixin:
    _mutable: bool
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __delattr__(self, name: str) -> None: ...

def mutating_method(func: Callable[..., Any]) -> Callable[..., Any]: ...
