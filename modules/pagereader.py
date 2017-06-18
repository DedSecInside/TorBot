import urllib.request 
from bs4 import BeautifulSoup


def readPage(site):
    response = urllib.request.urlopen(site)
    page = BeautifulSoup(response.read(),'html.parser')
    print (page.find_all('input'))
    return page