from modules.net_utils import get_urls_from_page, get_url_status
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors
from threading import Thread
from queue import Queue


def add_green(link):
    colors = Bcolors()
    return '\t' + colors.OKGREEN + link + colors.ENDC


def add_red(link):
    colors = Bcolors()
    return '\t' + colors.On_Red + link + colors.ENDC


def get_links(soup, ext=False, live=False):
    """
        Searches through all <a ref> (hyperlinks) tags and stores them in a
        list then validates if the url is formatted correctly.

        Args:
            soup: BeautifulSoup instance currently being used.

        Returns:
            websites: List of websites that were found
    """
    b_colors = Bcolors()
    if isinstance(soup, BeautifulSoup):
        websites = get_urls_from_page(soup, extension=ext)
        # Pretty print output as below
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')

        if live:
            display_link_status(websites)
        return websites

    else:
        raise(Exception('Method parameter is not of instance BeautifulSoup'))


def display_links(q):
    while True:
        link = q.get()
        resp = get_url_status(link)
        if resp != 0:
            title = BeautifulSoup(resp.text, 'html.parser').title
            coloredlink = add_green(link)
            print_row(coloredlink, title)
        else:
            coloredlink = add_red(link)
            print_row(coloredlink, "Not found")
        q.task_done()


def display_link_status(websites):
    q = Queue(len(websites)*2)
    for _ in websites:
        t = Thread(target=display_links, args=(q,))
        t.start()

    for link in websites:
        q.put(link)
    q.join()


def print_row(url, description):
    print("%-80s %-30s" % (url, description))
