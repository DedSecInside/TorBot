import sys
import os
sys.path.append(os.path.abspath('../'))
import urllib.request 
from modules.bcolors import bcolors
import bs4

"""Get all onion links from the website"""
def getLinks(soup,ext):
    _soup_instance = bs4.BeautifulSoup
    extensions = []
    if ext:
        for e in ext:
            extensions.append(e)  
    if isinstance(type(soup), type(_soup_instance)):
        websites = []
        for link in soup.find_all('a'):
            web_link = link.get('href')
            if web_link != None:
                if ('http' in web_link or 'https' in web_link):
                    if ext:
                        for exten in extensions:
                            if web_link.endswith(exten):
                                websites.append(web_link)
                    else:
                        websites.append(web_link)            
            else:
                pass
        """Pretty print output as below"""
        print ('') 
        print (bcolors.OKGREEN+'Websites Found - '+bcolors.ENDC+str(len(websites)))
        print ('-------------------------------')
        for web in websites:
            flag=1
            try:
                urllib.request.urlopen(web)    
            except urllib.error.HTTPError as e:
                if e.code:
                    print(bcolors.On_Red+web+bcolors.ENDC)
                    flag=0  
            if flag:
                print(web)          
        return websites
    else:
        raise('Method parameter is not of instance bs4.BeautifulSoup')
