"""
This module is used for reading HTML pages using either bs4.BeautifulSoup
objects or url strings
"""
import requests
from bs4 import BeautifulSoup

from .api import GoTor
from .color import color
from pprint import pprint


def print_tor_ip_address():
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    print('Attempting to connect to https://check.torproject.org/')
    ip_string = color(GoTor.get_ip(), 'yellow')
    print(f'Tor IP Address: {ip_string}')


def print_node(node):
    """
    Prints the status of a link based on it's connection status
    Args:
        link (str): link to get status of
    """
    try:
        title = node['url']
        status_text = f"{node['status_code']} {node['status']}"
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


def cascade(node, work):
    work(node)
    if node['children']:
        for child in node['children']:
            cascade(child, work)


def print_tree(url, depth=1):
    root = GoTor.get_node(url, depth)
    cascade(root, print_node)


def print_json(url, depth=1):
    root = GoTor.get_node(url, depth)
    pprint(root)
    return root
