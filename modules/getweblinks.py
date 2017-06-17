"""Get all onion links from the website"""
def getlinks(soup):
    websites = []
    for link in soup.find_all('a'):
        email_link = link.get('href')
        if email_link != None:
            if 'http' in email_link:
                websites.append(email_link)
        else:
            pass
    """Pretty print output as below"""
    print ('') 
    print ('Websites Found - '+str(len(websites)))
    print ('-------------------------------')
    for web in websites:
        print (web)
    return ''       