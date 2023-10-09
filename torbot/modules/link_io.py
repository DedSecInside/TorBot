"""
This module is used for reading HTML pages using either bs4.BeautifulSoup
objects or url strings
"""
import http.client
import tabulate

from pprint import pprint
from treelib import Tree

from .api import get_node, get_emails, get_phone, get_ip
from .color import color


def print_tor_ip_address() -> None:
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    resp = get_ip()
    print(resp["header"])
    print(color(resp["body"], "yellow"))


def pprint_tree(tree: Tree) -> None:
    """
    Prints the status of a link based on it's connection status
    """
    nodes = tree.all_nodes_itr()
    table_data = []

    def insert(node, color_code):
        status = str(node.data.status)
        code = http.client.responses[node.data.status]
        status_message = f'{status} {code}'
        table_data.append([
            node.tag,
            node.identifier,
            color(status_message, color_code),
            node.data.classification,
        ])

    for node in nodes:
        status_code = node.data.status
        if status_code >= 200 and status_code < 300:
            insert(node, 'green')
        elif status_code >= 300 and status_code < 400:
            insert(node, 'yellow')
        else:
            insert(node, 'red')

    headers = ["Title", "URL", "Status", "Category"]
    table = tabulate.tabulate(table_data, headers=headers)
    print(table)


def print_json(url: str, depth: int = 1):
    """
    Prints the JSON representation of a Link node.

    Returns:
        root (dict): Dictionary containing the root node and it's children
    """
    root = get_node(url, depth)
    print(root.to_json())


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
