import urllib.request
from bs4 import BeautifulSoup
from .bcolors import Bcolors


def readPage(site, printIP=0):
    b_colors = Bcolors()
    headers = {'User-Agent':
               'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot'}
    req = urllib.request.Request(site, None, headers)
    attempts_left = 3

    while (attempts_left):

        try:
            response = urllib.request.urlopen(req)
            page = BeautifulSoup(response.read(), 'html.parser')
            if printIP:
                pg = page.find('strong')
                IP = pg.renderContents()
                print(b_colors.WARNING + b_colors.BOLD + IP.decode("utf-8") +
                      b_colors.ENDC)
            return page

        except Exception as e:
            attempts_left -= 1
            error = e

    raise error
