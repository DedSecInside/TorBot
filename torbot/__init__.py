"""
Torbot Config.
"""
import os
from dotenv import load_dotenv
from .modules import link_io
# from .modules.linktree import LinkTree
from .modules.color import color
from .modules.updater import updateTor
from .modules.savefile import saveJson
from .modules.info import execute_all
from .modules.collect_data import collect_data

load_dotenv()  # Loads environment variables from .env file

__version__ = '2.1.0'

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

