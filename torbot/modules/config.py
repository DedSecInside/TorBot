import os
import logging

from dotenv import load_dotenv
from inspect import getsourcefile
from unipath import Path


config_file_path = (os.path.abspath(getsourcefile(lambda: 0)))
modules_directory = Path(config_file_path).parent
torbot_directory = modules_directory.parent
project_root_directory = torbot_directory.parent
dotenv_path = os.path.join(project_root_directory, '.env')
load_dotenv(dotenv_path=dotenv_path, verbose=True)

port = os.getenv("PORT")
host = os.getenv("HOST")


def get_log_level() -> int:
    log_level_str = os.getenv('LOG_LEVEL')
    if log_level_str:
        log_level_str = log_level_str.lower()
        mapping = logging.getLevelNamesMapping()
        if log_level_str in mapping:
            return mapping[log_level_str]
    return logging.INFO


def get_data_directory():
    data_directory = os.getenv('TORBOT_DATA_DIR')
    # if a path is not set, write data to the config directory
    if not data_directory:
        data_directory = project_root_directory

    if data_directory.strip() == "":
        data_directory = project_root_directory

    # create directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.mkdir(data_directory)

    return data_directory
