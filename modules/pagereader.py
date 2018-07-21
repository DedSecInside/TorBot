from bs4 import BeautifulSoup
from modules.net_utils import get_url_status
from modules.bcolors import Bcolors
from sys import exit


def connection_msg(site):
    yield "Attempting to connect to {site}".format(site=site)


def read_first_page(site):
    headers = {'User-Agent': 'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot'}
    attempts_left = 3
    err = " "
    while attempts_left:
        if attempts_left == 3:
            print(next(connection_msg(site)))
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
            exit(msg)


def get_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    b_colors = Bcolors()
    page = read_first_page('https://check.torproject.org/')[0]
    pg = page.find('strong')
    ip_addr = pg.renderContents()

    return b_colors.WARNING + b_colors.BOLD + ip_addr.decode("utf-8") + b_colors.ENDC
