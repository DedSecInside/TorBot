from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from termcolor import cprint

from requests.exceptions import HTTPError
import requests

from .pagereader import read


def execute_all(link, *, display_status=False):
    page, response = read(link, response=True, show_msg=display_status)
    soup = BeautifulSoup(page, 'html.parser')
    validation_functions = [get_robots_txt, get_dot_git, get_dot_svn, get_dot_git]
    for validate_func in validation_functions:
        try:
            validate_func(link)
        except (ConnectionError, HTTPError):
            cprint('Error', 'red')

    display_webpage_description(soup)
    display_headers(response)


def display_headers(response):
    print('''
          RESPONSE HEADERS
          __________________
          ''')
    for key, val in response.headers.items():
        print('*', key, ':', val)


def get_robots_txt(target):
    cprint("[*]Checking for Robots.txt", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    requests.get(target+"/robots.txt")
    cprint(r'blue')


def get_dot_git(target):
    cprint("[*]Checking for .git folder", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.git/")
    status = req.status_code
    if status == 200:
        cprint("Alert!", 'red')
        cprint(".git folder exposed publicly", 'red')
    else:
        cprint("NO .git folder found", 'blue')


def get_dot_svn(target):
    cprint("[*]Checking for .svn folder", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.svn/entries")
    status = req.status_code
    if status == 200:
        cprint("Alert!", 'red')
        cprint(".SVN folder exposed publicly", 'red')
    else:
        cprint("NO .SVN folder found", 'blue')


def get_dot_htaccess(target):
    cprint("[*]Checking for .htaccess", 'yellow')
    url = target
    target = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    req = requests.get(target+"/.htaccess")
    statcode = req.status_code
    if statcode == 403:
        cprint("403 Forbidden", 'blue')
    elif statcode == 200:
        cprint("Alert!!", 'blue')
        cprint(".htaccess file found!", 'blue')
    else:
        cprint("Status code", 'blue')
        cprint(statcode)


def display_webpage_description(soup):
    cprint("[*]Checking for description meta tag", 'yellow')
    metatags = soup.find_all('meta')
    for meta in metatags:
        if meta.has_attr('name'):
            attributes = meta.attrs
            if attributes['name'] == 'description':
                cprint("Page description: " + attributes['content'])
