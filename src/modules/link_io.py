"""
This module is used for reading HTML pages using either bs4.BeautifulSoup
objects or url strings
"""
import requests
from bs4 import BeautifulSoup

from .color import color
from pprint import pprint


def print_tor_ip_address():
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    print('Attempting to connect to https://check.torproject.org/')
    resp = requests.get(f'http://localhost:8081/ip')
    ip_string = color(resp.text, 'yellow')
    print(f'Tor IP Address: {ip_string}')

def print_node(node):
    """
    Prints the status of a link based on it's connection status
    Args:
        link (str): link to get status of
    """
    try:
        title = node['url']
        if node['status_code'] >= 200 and node['status_code'] < 300:
            status = color(f"{node['status_code']} {node['status']}", 'green')
        elif node['status_code'] >= 300 and node['status_code'] < 400:
            status = color(f"{node['status_code']} {node['status']}", 'yellow')
        else:
            status = color(f"{node['status_code']} {node['status']}", 'red')
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
    resp = requests.get(f'http://localhost:8081/children?link={url}&depth={depth}')
    root = resp.json()
    cascade(root, print_node)

def print_json(url, depth=1):
    resp = requests.get(f'http://localhost:8081/children?link={url}&depth={depth}')
    root = resp.json()
    pprint(root)
    return root

def print_emails(url, depth=1):
    print(url, depth)
