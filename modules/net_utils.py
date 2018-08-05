import re
import requests


def get_url_status(url, headers=False):
    """
        Uses head request because it uses less bandwith than get and timeout is
        set to 10 seconds and then link is automatically declared as dead.

        Args:
            link: link to be tested
            colors: object containing colors for link

        Return:
            something?: either an int or return value of the connection object's
            get request if successful & zero is failure
    """
    try:
        if headers:
            resp = requests.get(url, headers=headers)
        else:
            resp = requests.get(url)
        resp.raise_for_status()
        return resp
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return 0


def is_url(url):
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z, A-Z]+)(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return 1
    return 0


def is_onion_url(url):
    pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.onion/(.*)"
    regex = re.compile(pattern)
    if regex.match(url):
        return 1
    return 0


def get_urls_from_page(page, email=False, extension=False):
    urls = []
    anchors_on_page = page.find_all('a')
    for anchor_tag in anchors_on_page:
        url = anchor_tag.get('href')
        if extension:
            if url and is_url(url) == 1:
                urls.append(url)
        elif email:
            if url and 'mailto' in url:
                email_addr = url.split(':')
                if len(email_addr) > 1:
                    urls.append(email_addr[1])
        else:
            if url and is_onion_url(url) == 1:
                urls.append(url)

    return urls
