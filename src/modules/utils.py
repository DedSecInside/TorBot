"""
Provides essential utilites for the rest of TorBot app.
"""
import os

from dotenv import load_dotenv

# File Functions


def find_file(name, path):
    """Search for file within specific dir and any child dirs.

    Args:
        name (str): Filename to be searched for.
        path (str): Dir path to search for file.

    Returns:
        str: Full path of found file (if found).
        bool: If file not found, returns false.
    """
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return False


def join_local_path(file_name=""):
    """
    Returns a path to the data directory with the given filename appended

    Args:
        file_name (str): filename to be joined

    Returns:
        str: local path to data directory
    """
    if file_name == "":
        return

    dev_file = find_file("torbot_dev.env", "../")
    if not dev_file:
        raise FileNotFoundError
    load_dotenv(dotenv_path=dev_file)
    # Create data directory if it doesn't exist
    data_directory = os.getenv('TORBOT_DATA_DIR')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    local_path = os.path.join(data_directory, file_name)
    return local_path
