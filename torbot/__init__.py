"""
Torbot API.
"""
from .modules import link_io
# from .modules.linktree import LinkTree
from .modules.color import color
from .modules.updater import check_version
from .modules.savefile import saveJson
from .modules.info import execute_all
from .modules.collect_data import collect_data

from . import version
