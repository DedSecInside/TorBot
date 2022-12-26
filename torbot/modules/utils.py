"""
Provides essential utilites for the rest of TorBot app.
"""
import os

from .config import data_directory


# File Functions

def find_file(name: str, path: str):
    """Search for file within specific dir and any child dirs.

    Returns:
        str | bool: Full path of found file (if found). False otherwise
    """
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return False


def join_local_path(file_name: str=""):
    """
    Returns:
        str: local path to data directory
    """
    if file_name == "":
        return

    # Create data directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    local_path = os.path.join(data_directory, file_name)
    return local_path
