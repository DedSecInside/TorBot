from contextlib import contextmanager
from typing import Iterator

__all__ = ("safe_locale", )


@contextmanager
def safe_locale() -> Iterator[None]:
    """Helper function that establishes a context that temporarily switches the
    current locale to use decimal dots when printing numbers.

    This can be used to establish an execution context within which it is safe
    to call functions that read or write graphs from/to the disk and ensure that
    they use decimal dots for interoperability with systems that are running
    with another locale.
    """
    from igraph._igraph import _enter_safelocale, _exit_safelocale

    locale = _enter_safelocale()
    try:
        yield
    finally:
        _exit_safelocale(locale)
