import urllib.request
from modules.bcolors import Bcolors
from bs4 import BeautifulSoup



def link_status(web, out_queue, index):
    b_colors = Bcolors()
    out_queue[index] = web + " is_live = False "
    try:
        urllib.request.urlopen(web)
        out_queue[index] = web + " is_live = True "
        print(web)
    except urllib.error.HTTPError:
        print(b_colors.On_Red+web+b_colors.ENDC)


def getLinks(soup, ext, live=0, save=0):

    """Get all onion links from the website"""

    b_colors = Bcolors()
    extensions = []
    if ext:
        for e in ext:
            extensions.append(e)

    if isinstance(type(soup), type(BeautifulSoup)):
        websites = []

        for link in soup.find_all('a'):
            web_link = link.get('href')
            if web_link and ('http' in web_link or 'https' in web_link):

                for exten in extensions:
                    if web_link.endswith(exten):
                        websites.append(web_link)
                else:
                    websites.append(web_link)
        """Pretty print output as below"""
        print(''.join((b_colors.OKGREEN,
              'Websites Found - ', b_colors.ENDC, str(len(websites)))))
        print('-------------------------------')
        return websites

    else:
        raise('Method parameter is not of instance BeautifulSoup')
