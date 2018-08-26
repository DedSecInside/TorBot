import sys
from bs4 import BeautifulSoup
from modules.utils import get_url_status
from modules.bcolors import Bcolors


def display_url(url):
    """
        Prints the status of a url based on if it can be reached using a GET
        request. url is printed with a color based on status.
        Green for a reachable status code and red for not reachable.

        Args:
            url (str): url to be printed
        Returns:
            None
    """
    resp = get_url_status(url)
    if resp != 0:
        title = BeautifulSoup(resp.text, 'html.parser').title.string
        coloredurl = add_green(url)
        print_row(coloredurl, title)
    else:
        coloredurl = add_red(url)
        print_row(coloredurl, "Not found")


def print_row(url, description):
    print("%-80s %-30s" % (url, description))


def add_green(link):
    colors = Bcolors()
    return '\t' + colors.OKGREEN + link + colors.ENDC


def add_red(link):
    colors = Bcolors()
    return '\t' + colors.On_Red + link + colors.ENDC


def connection_msg(site):
    yield "Attempting to connect to {site}".format(site=site)


def read_first_page(site):
    headers = {'User-Agent': 'XXXX-XXXXX-XXXX'}
    attempts_left = 3
    err = " "
    while attempts_left:
        if attempts_left == 3:
            response = get_url_status(site, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response
            else:
                attempts_left -= 1
                continue

        if attempts_left == 2:
            https_url = 'https://' + site
            print(next(connection_msg(https_url)))
            response = get_url_status(https_url, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response
            else:
                attempts_left -= 1
                continue

        if attempts_left == 1:
            http_url = 'http://' + site
            print(next(connection_msg(http_url)))
            response = get_url_status(http_url, headers)
            if response != 0:
                page = BeautifulSoup(response.text, 'html.parser')
                return page, response
            else:
                attempts_left -= 1
                continue

        if not attempts_left:
            msg = ''.join(("There has been an {err} while attempting to ",
                           "connect to {site}.")).format(err=err, site=site)
            sys.exit(msg)


def get_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    b_colors = Bcolors()
    page = read_first_page('https://check.torproject.org/')[0]
    pg = page.find('strong')
    ip_addr = pg.renderContents()
    COLOR_BEGIN = b_colors.WARNING + b_colors.BOLD
    COLOR_END = b_colors.ENDC
    return COLOR_BEGIN + ip_addr.decode("utf-8") + COLOR_END
