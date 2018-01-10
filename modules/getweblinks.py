import re

from modules.bcolors import Bcolors
from bs4 import BeautifulSoup


def validate_url(link):

    """
        Validates url

        Takes in string which is a link and returns decides validitity of url
        using regex

        Args:
            link: the url to be checked

        Returns:
            bool: True/False based on link
    """

    pattern = r"^https?\b(://+)(.+)(.+)\bonion/(.*)"
    re_obj = re.compile(pattern)
    if re_obj.fullmatch(link):
        return True

    return False


def getLinks(soup):

    """
        Returns list of webistes or raises error if not BeautifulSoup object

        Searches through all <a ref> (hyperlinks) tags and stores them in a
        list then validates if the url is formatted correctly.

        Args:
            soup: BeautifulSoup instance currently being used.

        Returns:
            websites: List of websites that were found
    """

    b_colors = Bcolors()

    if isinstance(type(soup), type(BeautifulSoup)):
        websites = []

        links = soup.find_all('a')
        for link in links:
            url = link.get('href')
            if url and validate_url(url):
                websites.append(url)

        """Pretty print output as below"""
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('-------------------------------')
        return websites

    else:
        raise('Method parameter is not of instance BeautifulSoup')
