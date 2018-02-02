import urllib.request
from bs4 import BeautifulSoup
from modules.bcolors import Bcolors


def readPage(site):
    headers = {'User-Agent':
               'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot'}
    req = urllib.request.Request(site, None, headers)
    attempts_left = 3

    while (attempts_left):
        try:
            response = urllib.request.urlopen(req)
            page = BeautifulSoup(response.read(), 'html.parser')
            return page
        except Exception as e:
            attempts_left -= 1
            error = e

    raise error


def get_ip():
    """Returns users tor ip address

    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and return
    """

    b_colors = Bcolors()
    page = readPage('https://check.torproject.org/')
    pg = page.find('strong')
    ip_addr = pg.renderContents()

    return b_colors.WARNING+b_colors.BOLD+ip_addr.decode("utf-8")+b_colors.ENDC
