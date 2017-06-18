import urllib.request 
from bs4 import BeautifulSoup


def readPage(site):

 headers = {'User-Agent': 'JAMES CAMPBELL jamescampbell.us SEARCH BOT! I FOUND YOU!!!!' }
 req = urllib.request.Request(site,None,headers)
 response = urllib.request.urlopen(req)
 page = BeautifulSoup(response.read(),'html.parser')
 print (page.find_all('strong'))
 return page