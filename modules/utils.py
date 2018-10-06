
"""
Provides essential utilites for the rest of TorBot app
"""
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from ete3 import Tree

import requests
import modules.getweblinks


# ALGORITHM UTILITY FUNCTIONS

def bfs_urls(urls, add_exts, stop_depth=None, rec_depth=0, tree=None):
    """
    Traverses urls passed using Breadth First Search. You can specify stop
    depth or specify a target to look for. The rec_depth argument is used
    for recursion.

    *NOTE: This function uses a GET request for each url found, this can
    be very expensive so avoid if possible try to acquire the urls to
    be traversed and use bfs function.

    Args:
        urls (list): urls to traverse
        add_exts (str): additional extensions to use
        rec_depth (int): used for recursion
        stop_depth (int): stops traversing at this depth if specified

    Returns:
        rec_depth (int): depth stopped at
    """
    if rec_depth == stop_depth and rec_depth != 0:
        return tree
    
    urls_to_visit = list()
    t = Tree(name=tree.name)
    for url in urls:
        parent = t.add_child(name=url)
        if stop_depth != rec_depth + 1:
            try:
                resp = requests.get(url)
            except (HTTPError, ConnectionError):
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            page_urls = modules.getweblinks.get_urls_from_page(soup, extension=add_exts)
            for page_url in page_urls:
                parent.add_child(name=page_url)
                urls_to_visit.append(page_url)
    if stop_depth == rec_depth + 1:
        return t
    child = tree.add_child(t)
    rec_depth += 1

    return bfs_urls(urls_to_visit, add_exts, stop_depth, rec_depth=rec_depth, tree=child)


def bfs(nodes, target_node=None, rec_depth=0, stop_depth=None):
    """
    Traverses nodes using Breadth First Search. You can specify stop
    depth or specify a target to look for. The rec_depth argument is used
    for recursion.

    Args:
        nodes (list): objects to traverse
        target_node (object): object being searched for
        rec_depth (int): used for recursion
        stop_depth (int): stops traversing at this depth if specified

    Returns:
        rec_depth (int): depth stopped at
    """

    if rec_depth == stop_depth:
        return rec_depth

    adjacent_nodes = list()
    # Checks that nodes is a list or has a Visit method
    if not isinstance(nodes, list) and not hasattr(nodes, 'Visit', False):
        raise Exception('nodes must be a list')

    for node in nodes:
        if target_node == node and target_node:
            return rec_depth
        node.Visit()
        adjacent_nodes.append(node)
    rec_depth += 1

    if target_node and not stop_depth:
        return bfs(adjacent_nodes, target_node, rec_depth)
    if not target_node and stop_depth:
        return bfs(adjacent_nodes, rec_depth=rec_depth, stop_depth=stop_depth)
    if target_node and stop_depth:
        return bfs(adjacent_nodes, target_node, rec_depth, stop_depth)

    return bfs(adjacent_nodes, rec_depth)


def exec_tasks(que, task_func, tasks_args=tuple()):
    """
    Executes tasks inside of queue using function and arguments passed
    inside of threads

    Args:
        que (queue.Queue): contains tasks
        task_func (function): function to be executed on tasks and args
        task_args (tuple): contains arguments for function
    Returns:
        None
    """
    while True:
        task = que.get()
        if tasks_args:
            task_func(task, tasks_args)
        else:
            task_func(task)
        que.task_done()


def queue_tasks(tasks, task_func, tasks_args=tuple()):
    """
    Starts threads with tasks and queue, then queues tasks and spawned
    threads begin to pull tasks off queue to execute

    Args:
        tasks (list): lists of values that you'd like to operate on
        task_func (function): function that you would like to use
        tasks_args (tuple): arguments for function
    Returns:
        None
    """
    que = Queue(len(tasks)*2)
    for _ in tasks:
        if tasks_args:
            if isinstance(tasks_args, tuple):
                thd = Thread(target=exec_tasks, args=(que, task_func, tasks_args))
                thd.daemon = True
                thd.start()
            else:
                raise Exception('Arguments must be in the form of a tuple.')
        else:
            thd = Thread(target=exec_tasks, args=(que, task_func))
            thd.daemon = True
            thd.start()

    for task in tasks:
        que.put(task)
    que.join()


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
            resp = requests.get(url, headers=headers)
        else:
            resp = requests.get(url)
        resp.raise_for_status()
        return resp
    except (ConnectionError, HTTPError):
        return 0
