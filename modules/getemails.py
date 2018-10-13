
"""
Module returns emails found on webpage
"""
from bs4 import BeautifulSoup
from modules.getweblinks import get_urls_from_page
from modules.color import color


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
        emails = get_urls_from_page(soup, email=True)

        # Pretty print output as below
        success_string = color(f'Mails Found - {str(len(emails))}', 'green')
        print(success_string)
        print('-------------------------------')

        return emails

    raise ValueError('Method parameter is not of instance BeautifulSoup')
