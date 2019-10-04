
"""
Provides essential utilites for the rest of TorBot app.
"""
import os

from queue import Queue
from threading import Thread

import requests
from requests.exceptions import HTTPError



# ALGORITHM UTILITY FUNCTIONS

def process_data(data_queue, data_stack, process, *args):
    """
    Processes tasks using by grabbing threads from queue

    Args:
       data_queue (queue.Queue): Contains tasks in FIFO data structure.
       data_processor (function): Function to be executed on task and args.
       data_args (tuple): Contains arguments for tasks.
    """
    while True:
        data = data_queue.get()
        if isinstance(data, list):
            for single_inst in data:
                if args:
                    result = process(single_inst, args)
                else:
                    result = process(single_inst)
        elif args:
            result = process(data, args)
        else:
            result = process(data)

        if result:
            data_stack.append(result)
        data_queue.task_done()


def multi_thread(data, data_function, *args):
    """
    Start threads with function to process data and arguments then process the data
    in FIFO order.

    Args:
        data (list): Lists of values that you'd like to operate on.
        data_function (function): Function that you would like to use
            for processsing.
        args (tuple): Arguments for function.

    Returns:
        (list): List of processed data elements.
    """
    data_queue = Queue(len(data)*2)
    ret_stack = list()
    for _ in data:
        data_args = (data_queue, ret_stack, data_function, *args)
        thd = Thread(target=process_data, args=data_args)
        thd.daemon = True
        thd.start()

    for obj in data:
        data_queue.put(obj)

    data_queue.join()
    return ret_stack


# Networking functions

def get_url_status(url, headers=False):
    """
    Uses GET request to check if website exists.

    *NOTE: May look into changing this to HEAD requests to improve perf

    Args:
        url (str): URL to be tested.

    Return:
        (response object): Return response object from connection
            if successful.
        (int): Return 0 if connection not successful.
    """
    try:
        if headers:
            resp = requests.get(url, headers=headers)
        else:
            resp = requests.get(url)
        resp.raise_for_status()
        return resp
    except (ConnectionError, HTTPError):
        return 0


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
