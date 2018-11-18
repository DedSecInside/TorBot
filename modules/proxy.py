"""
Module contains onion proxy related code
"""
import requests

proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

session = requests.session()
session.proxies = proxies

def set_proxy(host, port):
    """
    Sets host and port for tor proxies being used when performing
    irequests to onion domains.

    Args:
        host (string): host name or IP Address
        port (string): port number
    """
    global proxies  #Allows us to modify global variable directly
    global session
    proxies = {
        'http': 'socks5h://' + host + ':' + port,
        'https': 'socks5h://' + host + ':' + port
    }
    session.proxies = proxies

def proxy_get(url, headers=None):
    """
    Peforms GET request using socks5 proxy

    Args:
        url (string): url to retreive
        headers (dict): mapping of headers for requests
    """
    if headers:
        return session.get(url, headers=headers)

    return session.get(url)


def proxy_head(url, timeout=10, headers=None):
    """
    Peforms HEAD request using socks5 proxy

    Args:
        url (string): url to retreive
        headers (dict): mapping of headers for requests
    """
    if headers:
        return session.head(url, timeout=timeout, headers=headers)

    return session.head(url, timeout=timeout)
