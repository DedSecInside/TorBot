"""
API Module

Provides access to external services using API wrappers
"""
import requests
from .utils import host, port

base_url = f'http://{host}:{port}'

def get_node(link, depth):
    """
    Returns the LinkTree for the given link at the specified depth.

    Args:
        link (str): link to be used as a root node.
        depth (int): depth of the tree
    """
    endpoint = f'/tree?link={link}&depth={depth}'
    url = base_url + endpoint
    resp = requests.get(url)
    return resp.json()

def get_ip():
    """
    Returns the IP address of the current Tor client the service is using.
    """
    endpoint = '/ip'
    url = base_url + endpoint
    resp = requests.get(url)
    return resp.text

def get_emails(link):
    """
    Returns the mailto links found on the page.

    Args:
        link (str): the page to pull the emails from.
    """
    endpoint = f'/emails?link={link}'
    url = base_url + endpoint
    resp = requests.get(url)
    return resp.json()

def get_phone(link):
    """
    Returns the tel links found on the page.

    Args:
        link (str): the page to pull the phones from.
    """
    endpoint = f'/phone?link={link}'
    url = base_url + endpoint
    resp = requests.get(url)
    return resp.json()

def get_web_content(link):
    """
    Returns the HTML content of the page.

    Args:
        link (str): the page to pull the content from.
    """
    endpoint = f'/content?link={link}'
    url = base_url + endpoint
    resp = requests.get(url)
    return resp.text