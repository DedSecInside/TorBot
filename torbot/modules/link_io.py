"""
This module is used for reading HTML pages using either bs4.BeautifulSoup
objects or url strings
"""

from pprint import pprint
from typing import Any

from .linktree import LinkTree
from .api import get_web_content, get_node, get_emails, get_phone, get_ip
from .color import color
from .nlp.main import classify


def print_tor_ip_address():
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    print('Attempting to connect to https://check.torproject.org/')
    ip_string = color(get_ip(), 'yellow')
    print(f'Tor IP Address: {ip_string}')


def print_node(node: LinkTree, classify_page: bool):
    """
    Prints the status of a link based on it's connection status
    """
    try:
        title = node['url']
        status_text = f"{node['status_code']} {node['status']}"
        if classify_page:
            classification = classify(get_web_content(node['url']))
            status_text += f" {classification}"
        if node['status_code'] >= 200 and node['status_code'] < 300:
            status = color(status_text, 'green')
        elif node['status_code'] >= 300 and node['status_code'] < 400:
            status = color(status_text, 'yellow')
        else:
            status = color(status_text, 'red')
    except Exception:
        title = "NOT FOUND"
        status = color('Unable to reach destination.', 'red')

    status_msg = "%-60s %-20s" % (title, status)
    print(status_msg)


def cascade(node: LinkTree, work: Any, classify_page: bool):
    work(node, classify_page)
    if node['children']:
        for child in node['children']:
            cascade(child, work, classify_page)


def print_tree(url: str, depth: int = 1, classify_page: bool = False):
    """
    Prints the entire tree in a user friendly fashion
    """
    root = get_node(url, depth)
    cascade(root, print_node, classify_page)


def print_json(url: str, depth: int = 1):
    """
    Prints the JSON representation of a Link node.

    Returns:
        root (dict): Dictionary containing the root node and it's children
    """
    root = get_node(url, depth)
    pprint(root)
    return root


def print_emails(url: str):
    """
    Prints any emails found within the HTML content of this url.

    Returns:
        emails (list): list of emails
    """
    email_list = get_emails(url)
    pprint(email_list)
    return email_list


def print_phones(url: str):
    """
    Prints any phones found within the HTML content of this url.

    Returns:
        phones (list): list of phones
    """
    phone_list = get_phone(url)
    pprint(phone_list)
    return phone_list
