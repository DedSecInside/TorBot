from modules.bcolors import Bcolors
from bs4 import BeautifulSoup
from modules.savefile import saveJson


"""Get all emails from the website"""


def getMails(soup, save=0):
    b_colors = Bcolors()
    _soup_instance = BeautifulSoup
    if isinstance(type(soup), type(_soup_instance)):
        emails = []
        for link in soup.find_all('a'):
            email_link = link.get('href')
            if email_link is not None:
                if 'mailto' in email_link:
                    """Split email address on"""
                    email_addr = email_link.split(':')
                    emails.append(email_addr[1])
            else:
                pass
        """Pretty print output as below"""
        print ('')
        print (b_colors.OKGREEN+'Mails Found - '+b_colors.ENDC+str(len(emails)))
        print ('-------------------------------')
        for mail in emails:
            print (mail)
        if save:
            saveJson("Extracted-Mail-IDs", emails)
        return ''
    else:
        msg = ''.join((b_colors.FAIL,
                       'Method parameter is not of instance BeautifulSoup',
                       b_colors.ENDC))
        raise(msg)
