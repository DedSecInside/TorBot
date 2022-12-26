"""
API Module

Provides access to external services using API wrappers
"""
import requests

from .log import debug
from .config import host, port

base_url: str = f'http://{host}:{port}'


def get_node(link: str, depth: int):
    """
    Returns the LinkTree for the given link at the specified depth.
    """
    endpoint = f'/tree?link={link}&depth={depth}'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = requests.get(url)
    data = resp.json()
    debug(f'retrieved {data}')
    return data


def get_ip():
    """
    Returns the IP address of the current Tor client the service is using.
    """
    endpoint = '/ip'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = requests.get(url)
    debug(f'retrieved {resp.text}')
    return resp.text


def get_emails(link: str):
    """
    Returns the mailto links found on the page.
    """
    endpoint = f'/emails?link={link}'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = requests.get(url)
    data = resp.json()
    debug(f'retrieved {data}')
    return data


def get_phone(link: str):
    """
    Returns the tel links found on the page.
    """
    endpoint = f'/phone?link={link}'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = requests.get(url)
    data = resp.json()
    debug(f'retrieved {data}')
    return data


def get_web_content(link: str):
    """
    Returns the HTML content of the page.
    """
    endpoint = f'/content?link={link}'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = requests.get(url)
    debug(f'retrieved {resp.text}')
    return resp.text
