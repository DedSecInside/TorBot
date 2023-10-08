"""
API Module

Provides access to external services using API wrappers
"""
import httpx
import logging

from treelib import Tree
from bs4 import BeautifulSoup, Tag

from .config import host, port
from .linktree import append_node, build_tree

base_url: str = f'http://{host}:{port}'

logging.getLogger("httpx").setLevel(logging.WARNING)

def get_node(url: str, depth: int):
    """
    Returns the LinkTree for the given link at the specified depth.
    """
    tree = Tree()
    append_node(tree, id=url, parent_id=None)
    build_tree(tree, url, depth)
    return tree


def get_ip() -> dict:
    """
    Returns the IP address of the current Tor client the service is using.
    """
    resp = httpx.get("https://check.torproject.org/", proxies='socks5://127.0.0.1:9050')
    soup = BeautifulSoup(resp.text, features='html.parser')

    # Get the content of check tor project, this contains the header and body
    content = soup.find("div", {"class": "content"})
    if not content:
        raise Exception("unable to find content to parse IP.")

    # parse the header
    header_tag = content.find("h1")
    if not header_tag:
        raise Exception("unable to find header")
    if not isinstance(header_tag, Tag):
        raise Exception("invalid header found")
    header = header_tag.get_text().strip()

    # parse the main content containing the IP address
    body_tag = content.find("p")
    if not body_tag:
        raise Exception("unable to find body")
    if not isinstance(body_tag, Tag):
        raise Exception("invalid body found")
    body = body_tag.get_text().strip()

    return {"header": header, "body": body}


def get_emails(link: str):
    """
    Returns the mailto links found on the page.
    """
    endpoint = f'/emails?link={link}'
    url = base_url + endpoint
    resp = httpx.get(url)
    data = resp.json()
    return data


def get_phone(link: str):
    """
    Returns the tel links found on the page.
    """
    endpoint = f'/phone?link={link}'
    url = base_url + endpoint
    resp = httpx.get(url)
    data = resp.json()
    return data


def get_web_content(link: str):
    """
    Returns the HTML content of the page.
    """
    endpoint = f'/content?link={link}'
    url = base_url + endpoint
    debug(f'requesting {url}')
    resp = httpx.get(url)
    debug(f'retrieved {resp.text}')
    return resp.text
