from modules.net_utils import get_urls_from_page, get_url_status
from modules import pagereader
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors


def add_green(link):
    colors = Bcolors()
    return '\t' + colors.OKGREEN + link + colors.ENDC


def add_red(link):
    colors = Bcolors()
    return '\t' + colors.On_Red + link + colors.ENDC


def get_links(soup, ext=False, live=False):
    """
        Searches through all <a ref> (hyperlinks) tags and stores them in a
        list then validates if the url is formatted correctly.

        Args:
            soup: BeautifulSoup instance currently being used.

        Returns:
            websites: List of websites that were found
    """
    b_colors = Bcolors()
    if isinstance(soup, BeautifulSoup):
        websites = get_urls_from_page(soup, extension=ext)
        """Pretty print output as below"""
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('------------------------------------')

        if live:
            for link in websites:
                if get_url_status(link) != 0:
                    coloredlink = add_green(link)
                    page = pagereader.read_first_page(link)[0]
                    if page is not None and page.title is not None:
                        print_row(coloredlink, page.title.string)
                else:
                    coloredlink = add_red(link)
                    print_row(coloredlink, "Not found")

        return websites

    else:
        raise(Exception('Method parameter is not of instance BeautifulSoup'))


def print_row(url, description):
    print("%-80s %-30s" % (url, description))
