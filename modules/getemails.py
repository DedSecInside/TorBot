
"""
Module returns emails found on webpage
"""
from bs4 import BeautifulSoup

import modules.getweblinks
from modules.colors import Colors

COLOR = Colors()

def get_mails(soup):
    """
    Searches for <a href> tags for links then checks if link contains the
    substring 'mailto' indicating that it's an email. If it is determined
    to be an email then the link is split and the username is appeneded to
    the list

    Args:
        soup: BeautifulSoup isntance that will be used for parsing

    Returns:
        emails: list of email IDs
    """

    if isinstance(type(soup), type(BeautifulSoup)):
        emails = modules.getweblinks.get_urls_from_page(soup, email=True)

        # Pretty print output as below
        print('')
        success_string = 'Mails Found - ' + str(len(emails))
        print(COLOR.add(success_string, 'green'))
        print('-------------------------------')

        return emails

    raise ValueError('Method parameter is not of instance BeautifulSoup')
