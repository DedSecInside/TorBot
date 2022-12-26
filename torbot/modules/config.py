import os
import logging

from dotenv import load_dotenv

load_dotenv()
port = os.getenv("PORT")
host = os.getenv("HOST")
data_directory = os.getenv('TORBOT_DATA_DIR')


log_level_str = os.getenv("LOG_LEVEL").lower() if os.getenv("LOG_LEVEL") else "info"
LOG_LEVELS = {
    "info": logging.INFO,
    "error": logging.ERROR,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
}


def get_log_level():
    for str_input, log_level in LOG_LEVELS.items():
        if log_level_str == str_input:
            return log_level
