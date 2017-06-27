import urllib.request 
from bs4 import BeautifulSoup
from modules.bcolors import bcolors


def readPage(site,printIP=0):

 headers = {'User-Agent': 'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot' }
 req = urllib.request.Request(site,None,headers)
 response = urllib.request.urlopen(req)
 page = BeautifulSoup(response.read(),'html.parser')
 if printIP:
  pg = page.find('strong')
  IP = pg.renderContents()
  print(bcolors.WARNING+bcolors.BOLD+IP.decode("utf-8")+bcolors.ENDC)
 return page