import logging

from .config import get_log_level


logging.basicConfig(level=get_log_level(),
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def info(msg: str):
    logging.info(msg)


def fatal(msg: str):
    logging.error(msg)


def debug(msg: str):
    logging.debug(msg)
