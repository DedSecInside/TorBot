"""
This module is used for reading HTML pages using either bs4.BeautifulSoup objects or url strings
"""

from bs4 import BeautifulSoup
from modules.utils import get_url_status
from modules.color import color


def read(link, response=False, headers=None, schemes=None):
    """
    Attempts to retrieve HTML from link

    Args:
        headers (dict)
        schemes (list)
    Returns:
        resp.text (str): html from page
    """
    headers = {'User-Agent': 'XXXX-XXXXX-XXXX'} if not headers else headers
    # Attempts to connect directly to site if no scheme is passed
    if not schemes:
        print(f"Attempting to connect to {link}")
        resp = get_url_status(link, headers)
        if resp != 0:
            if response:
                return resp.text, resp
            return resp.text

    schemes = ['https://', 'http://'] if not schemes else schemes

    for scheme in schemes:
        temp_url = scheme + link
        print(f"Attempting to connect to {link}")

        resp = get_url_status(temp_url, headers)
        if resp != 0:
            if response:
                return resp.text, resp

            return resp.text

    raise ConnectionError


def display(link):
    """
    Prints the status of a link
    """
    resp = get_url_status(link)
    if resp != 0:
        try:
            title = BeautifulSoup(resp.text, 'html.parser').title.string
            link_status = color(link, 'green')
        except AttributeError:
            title = "Not Found"
            link_status = color(link, 'red')
    else:
        title = "Not Found"
        link_status = color(link, 'red')

    print("%-80s %-30s" % (link_status, title))



def display_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    page = read('https://check.torproject.org/')
    page = BeautifulSoup(page, 'html.parser')
    ip_cont = page.find('strong')
    ip_addr = ip_cont.renderContents()
    ip_string = color(ip_addr.decode("utf-8"), 'yellow')
    print(f'Tor IP Address: {ip_string}')
