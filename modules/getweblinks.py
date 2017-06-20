import bs4
from modules.pagereader import readPage
import socks

"""Get all onion links from the website"""
def getLinks(soup):
    _soup_instance = bs4.BeautifulSoup
    extensions = ['.onion','.onion/']
    if isinstance(type(soup), type(_soup_instance)):
        websites = []
        for link in soup.find_all('a'):
            email_link = link.get('href')
            if email_link != None:
                if 'http' in email_link:
                    for extension in extensions:
                        if email_link.endswith(extension):
                            websites.append(email_link)
            else:
                pass
        """Pretty print output as below"""
        print ('') 
        print ('Websites Found - '+str(len(websites)))
        print ('-------------------------------')
        for web in websites:
            print (web)
        #return ''
        return websites
    else:
        raise('Method parameter is not of instance bs4.BeautifulSoup')
