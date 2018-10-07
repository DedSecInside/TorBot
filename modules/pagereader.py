
"""
This module is used for reading HTML pages using either bs4.BeautifulSoup objects or url strings
"""

from bs4 import BeautifulSoup
from modules.utils import get_url_status
from modules.colors import Colors

COLOR = Colors()

def display_url(url):
    """
    Prints the status of a url based on if it can be reached using a GET
    request. url is printed with a color based on status.
    Green for a reachable status code and red for not reachable.

    Args:
        url (str): url to be printed
    Returns:
        None
    """
    resp = get_url_status(url)
    if resp != 0:
        title = BeautifulSoup(resp.text, 'html.parser').title.string
        coloredurl = COLOR.add(url, 'green')
        print_row(coloredurl, title)
    else:
        coloredurl = COLOR.add(url, 'red')
        print_row(coloredurl, "Not found")


def print_row(url, description):
    """
    Prints row in specified format
    """
    print("%-80s %-30s" % (url, description))


def connection_msg(url):
    """
    Generator used to yield message while waiting for response
    """
    yield "Attempting to connect to {url}".format(url=url)

def read_page(url, headers=None, schemes=None, show_msg=False):
    """
    Attempts to connect to url and returns the HTML from page

    Args:
        url (str): url of website to be read
    Returns:
        page (str): html from page
        response (int): indicator of success
    """
    headers = {'User-Agent': 'XXXX-XXXXX-XXXX'} if not headers else headers
    # Attempts to connect directly to site if no scheme is passed
    if not schemes:
        if show_msg:
            print(next(connection_msg(url)))
        schemes = ['https://', 'http://']
        resp = get_url_status(url, headers)
        if resp != 0:
            return resp.text

    schemes = ['https://', 'http://'] if not schemes else schemes

    for scheme in schemes:
        temp_url = scheme + url
        if show_msg:
            print(next(connection_msg(temp_url)))
        resp = get_url_status(temp_url, headers)
        if resp != 0:
            return resp.text

    raise ConnectionError



def get_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    page = read_page('https://check.torproject.org/')
    page = BeautifulSoup(page, 'html.parser')
    ip_cont = page.find('strong')
    ip_addr = ip_cont.renderContents()
    ip_string = ip_addr.decode("utf-8")
    return COLOR.add(ip_string, 'yellow')
