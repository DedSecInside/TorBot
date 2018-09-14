import re
import modules.utils

from bs4 import BeautifulSoup
from modules.bcolors import Bcolors

def is_url(url):
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z, A-Z]+)(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return 1
    return 0


def is_onion_url(url):
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
        raise(Exception("First arg must be bs4.BeautifulSoup object"))

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


def search_page(html, ext, stop_depth=None):
    """
        Takes in a pages HTML and searches the links on the page using
        BFS.

        Args:
            html (str): HTML with links to search
            add_exts (str): additional extension
            stop_depth (int): The depth at which to stop
        Returns:
            links_found (list): links found on page and associated pages
    """

    soup = BeautifulSoup(html, 'html.parser')
    links = get_urls_from_page(soup, extension=ext)
    if stop_depth:
        links_found = utils.bfs_urls(links, ext, stop_depth=stop_depth)
    else:
        links_found = utils.bfs_urls(links, ext)

    return links_found


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
            utils.queue_tasks(websites, utils.display_link)
        return websites

    else:
        raise(Exception('Method parameter is not of instance BeautifulSoup'))
