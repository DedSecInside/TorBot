"""unipath.py - A two-class approach to file/directory operations in Python.
"""

from unipath.abstractpath import AbstractPath
from unipath.path import Path

FSPath = Path

#### FILTER FUNCTIONS (PUBLIC) ####
def DIRS(p):  return p.isdir()
def FILES(p):  return p.isfile()
def LINKS(p):  return p.islink()
def DIRS_NO_LINKS(p):  return p.isdir() and not p.islink()
def FILES_NO_LINKS(p):  return p.isfile() and not p.islink()
def DEAD_LINKS(p):  return p.islink() and not p.exists()
    
