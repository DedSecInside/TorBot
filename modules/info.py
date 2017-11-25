import urllib.request
from urllib.parse import urlsplit
from termcolor import colored, cprint

__all__ = ['executeAll']


def __init__(self):
    pass




def executeAll(target):
    try:
        self.get_robots_txt(target)
    except:
        cprint("No robots.txt file Found!", "blue")
    try:
        self.get_dot_git(target)
    except:
        cprint("Error !", "red")
    try:
        self.get_dot_svn(target)
    except:
        cprint("Error", "red")
    try:
        self.get_dot_htaccess(target)
    except:
        cprint("Error", "red")




def get_robots_txt(self, target):
    cprint("[*]Checking for Robots.txt", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/robots.txt")
    r = req.text
    cprint(r, 'blue')




def get_dot_git(self, target):
    cprint("[*]Checking for .git folder", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.git/")
    r = req.status_code
    if r == 200:
        cprint("Alert!", 'red')
        cprint(".git folder exposed publicly", 'red')
    else:
        print("NO .git folder found", 'blue')




def get_dot_svn(self, target):
    cprint("[*]Checking for .svn folder", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.svn/entries")
    r = req.status_code
    if r == 200:
        cprint("Alert!", 'red')
        cprint(".SVN folder exposed publicly", 'red')
    else:
        cprint("NO .SVN folder found", 'blue')

def get_dot_htaccess(self, target):
    cprint("[*]Checking for .htaccess", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.htaccess")
    r = req.text
    statcode = req.status_code
    if statcode == 403:
        cprint("403 Forbidden", 'blue')
    elif statcode == 200:
        cprint("Alert!!", 'blue')
        cprint(".htaccess file found!", 'blue')
    else:
        cprint("Status code", 'blue')
        cprint(statcode, 'blue')