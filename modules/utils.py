
"""
Provides essential utilites for the rest of TorBot app
"""
from queue import Queue
from threading import Thread
from requests.exceptions import HTTPError
import requests
from .proxy import proxy_get

# ALGORITHM UTILITY FUNCTIONS

def process_data(data_queue, data_stack, process, *args):
    """
    Processes tasks using by grabbing threads from queue

    Args:
       data_queue (queue.Queue): contains tasks in FIFO data structure
       data_processor (function): function to be executed on task and args
       data_args (tuple): contains arguments for tasks
    Returns:
        None
    """
    while True:
        data = data_queue.get()
        if args:
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
        data (list): lists of values that you'd like to operate on
        data_function (function): function that you would like to use for processsing
        args (tuple): arguments for function
    Returns:
        None
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
    Uses GET request to check if website exists

    *NOTE: May look into changing this to HEAD requests to improve perf

    Args:
        url (str): url to be tested

    Return:
        something? (int/Response object): return value of the connection
        object's GET request if successful & zero upon failure
    """
    try:
        if headers:
            resp = proxy_get(url, headers)
        else:
            resp = proxy_get(url)
        resp.raise_for_status()
        return resp
    except (ConnectionError, HTTPError):
        return 0
