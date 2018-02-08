import re
import requests
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors


def valid_url(url):
    """Checks if url is valid using regular expression matching

        Matches all possible url patterns with the url that is passed and returns
        True if it is a url and returns False if it is not.

        Args:
            url: string representing url to be checked

        Returns:
            bool: True if valid url format, False if not
    """
    regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
    except requests.exceptions.ConnectionError:
        yield '\t'+colors.On_Red+link+colors.ENDC

    if not resp.status_code == 200:
        yield '\t'+colors.On_Red+link+colors.ENDC
    else:
        yield '\t'+link


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
            if url and valid_url(url):
                if ext:
                    for extension in ext:
                        if not url.endswith(extension):
                            continue
                websites.append(url)

        """Pretty print output as below"""
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')
        if live:
            for link in websites:
                print(next(get_link_status(link, b_colors)))
            return websites

    else:
        raise('Method parameter is not of instance BeautifulSoup')
