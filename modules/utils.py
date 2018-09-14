import re
import requests
import modules.getweblinks

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError
from queue import Queue
from threading import Thread

# ALGORITHM UTILITY FUNCTIONS

def bfs_urls(urls, add_exts, rec_depth=0, stop_depth=None, target_url=None):
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
            target_url (str): stops at this url if specified

        Returns:
            rec_depth (int): depth stopped at
    """

    if rec_depth == stop_depth:
        return rec_depth

    urls_to_visit = list()
    for url in urls:
        if target_url == url and target_url:
            return rec_depth
        try:
            resp = requests.get(url)
        except (HTTPError, ConnectionError):
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        page_urls = getweblinks.get_urls_from_page(soup, extension=add_exts)
        for url in page_urls:
            urls_to_visit.append(url)
    rec_depth += 1
    if stop_depth and target_url:
        bfs_urls(urls_to_visit, add_exts, rec_depth, stop_depth, target_url)
    elif stop_depth:
        bfs_urls(urls_to_visit, add_exts, rec_depth, stop_depth=stop_depth)
    elif target_url:
        bfs_urls(urls_to_visit, add_exts, rec_depth, target_url=target_url)
    else:
        bfs_urls(urls_to_visit, add_exts, rec_depth=rec_depth)


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
        raise(Exception('nodes must be a list'))

    for node in nodes:
        if target_node == node and target_node:
            return rec_depth
        node.Visit()
        adjacent_nodes.append(node)
    rec_depth += 1
    if target_node and not stop_depth:
        bfs(adjacent_nodes, target_node, rec_depth)
    elif not target_node and stop_depth:
        bfs(adjacent_nodes, rec_depth=rec_depth, stop_depth=stop_depth)
    elif target_node and stop_depth:
        bfs(adjacent_nodes, target_node, rec_depth, stop_depth)
    else:
        bfs(adjacent_nodes, rec_depth)


def exec_tasks(q, task_func, tasks_args=tuple()):
    """
        Executes tasks inside of queue using function and arguments passed
        inside of threads

        Args:
            q (queue.Queue): contains tasks
            task_func (function): function to be executed on tasks and args
            task_args (tuple): contains arguments for function
        Returns:
            None
    """
    while True:
        task = q.get()
        if tasks_args:
            task_func(task, tasks_args)
        else:
            task_func(task)
        q.task_done()


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
    q = Queue(len(tasks)*2)
    for _ in tasks:
        if tasks_args:
            if isinstance(tasks_args, tuple):
                t = Thread(target=exec_tasks, args=(q, task_func, tasks_args))
                t.daemon = True
                t.start()
            else:
                raise(Exception('Arguments must be in the form of a tuple.'))
        else:
            t = Thread(target=exec_tasks, args=(q, task_func))
            t.daemon = True
            t.start()

    for task in tasks:
        q.put(task)
    q.join()


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
