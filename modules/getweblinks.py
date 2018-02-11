import re
import requests

from bs4 import BeautifulSoup
from modules.bcolors import Bcolors
from requests.exceptions import ConnectionError, HTTPError


def valid_url(url):
    """Checks for any valid url using regular expression matching

        Matches all possible url patterns with the url that is passed and
        returns True if it is a url and returns False if it is not.

        Args:
            url: string representing url to be checked

        Returns:
            bool: True if valid url format and False if not
    """

    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z, A-Z]+)(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return True
    return False


def valid_onion_url(url):
    """Checks for valid onion url using regular expression matching

        Only matches onion urls

        Args:
            url: string representing url to be checked

        Returns:
            bool: True if valid onion url format, False if not
    """
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z,A-Z]+)(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return True
    return False


def get_link_status(link, colors):
    """Generator that yields links as they come

        Uses head request because it uses less bandwith than get and timeout is
        set to 10 seconds and then link is automatically declared as dead.

        Args:
            link: link to be tested
            colors: object containing colors for link

        Yields:
            string: link with either no color or red which indicates failure
    """

    try:
        resp = requests.head(link, timeout=10)
        resp.raise_for_status()
        yield '\t'+link
    except (ConnectionError, HTTPError):
        yield '\t'+colors.On_Red+link+colors.ENDC


def getLinks(soup, ext=False, live=False):
    """
        Searches through all <a ref> (hyperlinks) tags and stores them in a
        list then validates if the url is formatted correctly.

        Args:
            soup: BeautifulSoup instance currently being used.

        Returns:
            wfebsites: List of websites that were found
    """
    b_colors = Bcolors()
    if isinstance(soup, BeautifulSoup):
        websites = []

        links = soup.find_all('a')
        for ref in links:
            url = ref.get('href')
            if ext:
                if url and valid_url(url):
                    websites.append(url)
            else:
                if url and valid_onion_url(url):
                    websites.append(url)

        """Pretty print output as below"""
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')

        for link in websites:
            print(next(get_link_status(link, b_colors)))
        return websites

    else:
        raise('Method parameter is not of instance BeautifulSoup')
