import requests

from requests import HTTPError, ConnectionError
from modules.net_utils import get_urls_from_page, get_url_status
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors
from threading import Thread
from queue import Queue


def traverse_links(links, ext, depth=0, stop_depth=None, targetLink=None):
    """
        Traverses links passed using Breadth First Search. You can specify stop depth
        or specify a target to look for. The depth argument is used for recursion

        Args:
            links (list): list of urls to traverse
            ext (string): string representing extension to use for URLs
            depth (int): used for recursion
            stop_depth (int): stops traversing at this depth if specified
            targetLink (string): stops at this link if specified

        Returns:
            depth (int): depth stopped at
    """

    if depth == stop_depth:
        return depth

    toVisit = list()
    for link in links:
        if targetLink == link and targetLink:
            return depth
        try:
            resp = requests.get(link)
        except (HTTPError, ConnectionError):
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        websitesToVisit = get_urls_from_page(soup, extension=ext)
        for site in websitesToVisit:
            toVisit.append(site)
    depth += 1
    if stop_depth and targetLink:
        traverse_links(toVisit, ext, depth, stop_depth, targetLink)
    elif stop_depth:
        traverse_links(toVisit, ext, depth, stop_depth=stop_depth)
    elif targetLink:
        traverse_links(toVisit, ext, depth, targetLink=targetLink)
    else:
        traverse_links(toVisit, ext, depth)


def search_page(html_text, ext, stop=None):
    soup = BeautifulSoup(html_text, 'html.parser')
    links = get_urls_from_page(soup, extension=ext)
    if stop:
        traverse_links(links, ext, stop=stop)
    else:
        traverse_links(links, ext)


def add_green(link):
    colors = Bcolors()
    return '\t' + colors.OKGREEN + link + colors.ENDC


def add_red(link):
    colors = Bcolors()
    return '\t' + colors.On_Red + link + colors.ENDC


def get_links(soup, ext=False, live=False):
    """
        Returns list of links listed on the webpage of the soup passed. If live
        is set to true then it will also print the status of each of the links
        and setting ext to an actual extension such as '.com' will allow those
        extensions to be recognized as valid urls and not just '.tor'.

        Args:
            soup (bs4.BeautifulSoup): webpage to be searched for links.

        Returns:
            websites (list(str)): List of websites that were found
    """
    b_colors = Bcolors()
    if isinstance(soup, BeautifulSoup):
        websites = get_urls_from_page(soup, extension=ext)
        # Pretty print output as below
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')

        if live:
            queue_tasks(websites, display_link)
        return websites

    else:
        raise(Exception('Method parameter is not of instance BeautifulSoup'))


def display_link(link):
    """
        Prints the status of a link based on if it can be reached using a GET
        request. Link is printed with a color based on status.
        Green for a reachable status code and red for not reachable.

        Args:
            link (str): url to be printed
        Returns:
            None
    """
    resp = get_url_status(link)
    if resp != 0:
        title = BeautifulSoup(resp.text, 'html.parser').title.string
        coloredlink = add_green(link)
        print_row(coloredlink, title)
    else:
        coloredlink = add_red(link)
        print_row(coloredlink, "Not found")


def execute_tasks(q, task_func, tasks_args=tuple()):
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
        Starts threads with tasks and queue, then queues tasks and spawned threads
        begin to pull tasks off queue to execute

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
                t = Thread(target=execute_tasks, args=(q, task_func, tasks_args))
                t.daemon = True
                t.start()
            else:
                raise(Exception('Function arguments must be passed in the form of a tuple.'))
        else:
            t = Thread(target=execute_tasks, args=(q, task_func))
            t.daemon = True
            t.start()

    for task in tasks:
        q.put(task)
    q.join()


def print_row(url, description):
    print("%-80s %-30s" % (url, description))
