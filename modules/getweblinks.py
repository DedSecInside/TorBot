import sys
import os
sys.path.append(os.path.abspath('../'))
import urllib.request 
from modules.bcolors import Bcolors
import bs4
import time
import threading
import http

__all__ = ['getLinks']

def link_status(web):
    link_live = False
    try:
        urllib.request.urlopen(web)    
        link_live = True
        print(web)
    except urllib.error.HTTPError as e:
        print(Bcolors.On_Red+web+Bcolors.ENDC)
    except urllib.error.URLError as e:
        print(Bcolors.On_Red+web+Bcolors.ENDC)
    except http.client.RemoteDisconnected as e:
        print(Bcolors.On_Red+web+Bcolors.ENDC)
    return 


"""Get all onion links from the website"""
def getLinks(soup,ext,live=0):
    _soup_instance = bs4.BeautifulSoup
    extensions = []
    if ext:
        for e in ext:
            extensions.append(e) 
    if isinstance(type(soup), type(_soup_instance)):
        websites = []
        start_time = time.time()
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
        print (Bcolors.OKGREEN+'Websites Found - '+Bcolors.ENDC+str(len(websites)))
        print ('-------------------------------')
        if live:
            threads = []
            for web in websites:
                t = threading.Thread(target=link_status, args=(web,))
                threads.append(t)
                t.start()
        else:
            for web in websites:
                print(web)
        return websites           
    else:
        raise('Method parameter is not of instance bs4.BeautifulSoup')
