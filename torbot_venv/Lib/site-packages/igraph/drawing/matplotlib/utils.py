from igraph.drawing.utils import FakeModule
from typing import Any

__all__ = ("find_matplotlib",)
__docformat__ = "restructuredtext en"


def find_matplotlib() -> Any:
    """Tries to import the ``matplotlib`` Python module if it is installed.
    Returns a fake module if everything fails.
    """
    try:
        import matplotlib as mpl

        has_mpl = True
    except ImportError:
        mpl = FakeModule("You need to install matplotlib to use this functionality")
        has_mpl = False

    if has_mpl:
        import matplotlib.pyplot as plt
    else:
        plt = FakeModule(
            "You need to install matplotlib.pyplot to use this functionality"
        )

    return mpl, plt
