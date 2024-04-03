import os

from dotenv import load_dotenv
from inspect import getsourcefile
from unipath import Path

source_file = getsourcefile(lambda: 0)
config_file_path = None
if isinstance(source_file, str):
    config_file_path = os.path.abspath(source_file)

if not config_file_path:
    raise Exception("Unable to load environment.")

modules_directory = Path(config_file_path).parent
torbot_directory = modules_directory.parent
project_root_directory = torbot_directory.parent
dotenv_path = os.path.join(project_root_directory, ".env")
load_dotenv(dotenv_path=dotenv_path, verbose=True)


def get_data_directory():
    data_directory = os.getenv("TORBOT_DATA_DIR")
    # if a path is not set, write data to the config directory
    if not data_directory:
        data_directory = project_root_directory

    if data_directory.strip() == "":
        data_directory = project_root_directory

    # create directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.mkdir(data_directory)

    return data_directory
