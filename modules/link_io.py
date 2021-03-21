"""
This module is used for reading HTML pages using either bs4.BeautifulSoup objects or url strings
"""
import requests
from bs4 import BeautifulSoup

from .color import color


def print_tor_ip_address():
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    print('Attempting to connect to https://check.torproject.org/')
    response = requests.get('https://check.torproject.org/')
    page = BeautifulSoup(response.text, 'html.parser')
    ip_cont = page.find('strong')
    ip_addr = ip_cont.renderContents()
    ip_string = color(ip_addr.decode("utf-8"), 'yellow')
    print(f'Tor IP Address: {ip_string}')


def display_children(node):
    """
    Static method to display status of child nodes

    Args:
        node (LinkNode): root of children to be displayed
    """
    children = node.get_children()
    sucess_msg = color(f'Links Found - {len(children)}', 'green')
    print(sucess_msg + '\n' + '---------------------------------')
    for child in children:
        display(child)


def display(node):
    """
    Prints the status of a link based on it's connection status

    Args:
        link (str): link to get status of
    """
    try:
        node.load_data()
        title = node.get_name()
        status = node.status
    except Exception:
        title = "NOT FOUND"
        status = color('Unable to reach destination.', 'red')
    status_msg = "%-30s %-20s %-70s" % (title, status, node.get_link())
    print(status_msg)
