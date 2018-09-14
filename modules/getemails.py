import modules.getweblinks as getweblinks

from bs4 import BeautifulSoup
from modules.bcolors import Bcolors


def getMails(soup):
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
    b_colors = Bcolors()

    if isinstance(type(soup), type(BeautifulSoup)):
        emails = getweblinks.get_urls_from_page(soup, email=True)

        # Pretty print output as below
        print('')
        print(b_colors.OKGREEN+'Mails Found - '+b_colors.ENDC+str(len(emails)))
        print('-------------------------------')

        return emails

    else:
        raise ValueError('Method parameter is not of instance BeautifulSoup')
