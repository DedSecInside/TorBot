#from bs4 import BeautifulSoup
import bs4

"""Get all emails from the website"""

def getMails(soup):
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
        print ('Mails Found - '+str(len(emails)))
        print ('-------------------------------')
        for mail in emails:
            print (mail)
        return ''
    else:
        raise('Method parameter is not of instance bs4.BeautifulSoup')
