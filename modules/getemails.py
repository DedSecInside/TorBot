import sys
import os
sys.path.append(os.path.abspath('../'))
from modules.bcolors import Bcolors
from modules.savefile import saveJson
import bs4

__all__ = ['getMails']

"""Get all emails from the website"""

def getMails(soup,save=0):
    _soup_instance = bs4.BeautifulSoup
    if isinstance(type(soup), type(_soup_instance)):
        emails = []
        for link in soup.find_all('a'):
            email_link = link.get('href')
            if email_link != None:
                if 'mailto' in email_link:
                    """Split email address on"""
                    email_addr = email_link.split(':')
                    emails.append(email_addr[1])
            else:
                pass
        """Pretty print output as below"""
        print ('') 
        print (Bcolors.OKGREEN+'Mails Found - '+Bcolors.ENDC+str(len(emails)))
        print ('-------------------------------')
        for mail in emails:
            print (mail)
        if save:
            saveJson("Extracted-Mail-IDs",emails)
        return ''
    else:
        raise(Bcolors.FAIL+'Method parameter is not of instance bs4.BeautifulSoup'+Bcolors.ENDC)
