
"""
This module is used for reading HTML pages using either bs4.BeautifulSoup objects or url strings
"""

import sys
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


def read_page(url):
    """
    Attempts to connect to url and returns the HTML from page

    Args:
        url (str): url of website to be read
    Returns:
        page (str): html from page
        response (int): indicator of success
    """
    headers = {'User-Agent': 'XXXX-XXXXX-XXXX'}
    attempts_left = 3
    err = " "
    while attempts_left:
        if attempts_left == 3:
            print(next(connection_msg(url)))
            response = get_url_status(url, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response

            attempts_left -= 1
            continue

        if attempts_left == 2:
            https_url = 'https://' + url
            print(next(connection_msg(https_url)))
            response = get_url_status(https_url, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response

            attempts_left -= 1
            continue

        if attempts_left == 1:
            http_url = 'http://' + url
            print(next(connection_msg(http_url)))
            response = get_url_status(http_url, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response

            attempts_left -= 1
            continue

        if not attempts_left:
            msg = ''.join(("There has been an {err} while attempting to ",
                           "connect to {url}.")).format(err=err, url=url)
            sys.exit(msg)


def get_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    page = read_page('https://check.torproject.org/')[0]
    ip_cont = page.find('strong')
    ip_addr = ip_cont.renderContents()
    ip_string = ip_addr.decode("utf-8")
    return COLOR.add(ip_string, 'yellow')
