
"""
Module used to interact with a pages urls
"""
import re
from bs4 import BeautifulSoup

from .color import color
from .utils import multi_thread
from .pagereader import read, display


def is_url(url):
    """
    Returns an integer representing validity of url syntax

    Args:
        url (str): url to be verified
    Returns
        (int): integer representing if url is a valid format
    """
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z, A-Z]+)(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return 1
    return 0


def is_onion_url(url):
    """
    Returns an integer representing validity of an onion url syntax

    Args:
        url (str): url to be verified
    Returns
        (int): integer representing if url is a valid format
    """
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.onion/(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return 1
    return 0

def get_urls_from_page(page_soup, email=False, extension=False):
    """
    Searches for urls on page using the anchor tag and href attribute,
    also searchs for emails using 'mailto' if specified.

    Args:
        page (bs4.BeauitulSoup): html soup to search
        email (bool): flag whether to collect emails as well
        extension (bool): flag whether to use additional extensions

    Returns:
        urls (list): urls found on page
    """
    if not isinstance(page_soup, BeautifulSoup):
        raise Exception("First arg must be bs4.BeautifulSoup object")

    urls = []
    anchors_on_page = page_soup.find_all('a')
    for anchor_tag in anchors_on_page:
        url = anchor_tag.get('href')
        if extension:
            if url and is_url(url) == 1:
                urls.append(url)
        elif email:
            if url and 'mailto' in url:
                email_addr = url.split(':')
                if len(email_addr) > 1:
                    urls.append(email_addr[1])
        else:
            if url and is_onion_url(url) == 1:
                urls.append(url)

    return urls


def get_links(link, ext=False, display_status=False):
    """
    Returns list of links listed on the webpage of the soup passed. If live
    is set to true then it will also print the status of each of the links
    and setting ext to an actual extension such as '.com' will allow those
    extensions to be recognized as valid urls and not just '.tor'.

    Args:
        link (str): link to find children of
        ext (bool): additional top-level-domains

    Returns:
        websites (list(str)): List of websites that were found
    """
    page = read(link, show_msg=display_status)
    soup = BeautifulSoup(page, 'html.parser')
    if isinstance(soup, BeautifulSoup):
        links = get_urls_from_page(soup, extension=ext)
        # Pretty print output as below
        success_string = color(f'Links Found - {str(len(links))}', 'green')
        print(success_string)
        print('------------------------------------')

        if display_status:
            multi_thread(links, display)
        return links

    raise Exception('Method parameter is not of instance BeautifulSoup')
