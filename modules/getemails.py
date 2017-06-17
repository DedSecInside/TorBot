"""Get all emails from the website"""

def getmails(soup):
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
