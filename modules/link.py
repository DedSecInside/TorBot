"""

This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods

"""
import requests

from bs4 import BeautifulSoup
from .color import color
from .validators import validate_email, validate_link

def get_children(node):
    children = []
    for anchor_tag in node._node.find_all('a'):
        link = anchor_tag.get('href')
        if validate_link(link):
            child_node = LinkNode(link)
            children.append(child_node)
    return children

def get_emails(node):
    """Finds all emails associated with node

    Args:
        node (LinkNode): node used to get emails from
    Returns:
        emails (list): list of emails
    """
    emails = []
    for anchor_tag in node._node.find_all('a'):
        link = anchor_tag.get('href')
        if link and 'mailto' in link:
            email_addr = link.split(':')
            if validate_email(email_addr[1]) and len(email_addr) > 1:
                emails.append(email_addr[1])
    return emails

class LinkNode:
    """Represents link node in a link tree

    Attributes:
        link (str): link to be used as node
    """
    def __init__(self, link):
        # If link has invalid form, throw an error
        if not validate_link(link):
            raise ValueError("Invalid link format.")
        self._loaded = False
        self._link = link
        self._emails = []
        self._links = []

    def load_data(self):
        if self._loaded:
            return

        response = requests.get(self._link)
        status = str(response.status_code)
        try:
            response.raise_for_status()
            self._node = BeautifulSoup(response.text, 'html.parser')
            self.status = color(status, 'green')
            self._name = self._node.title.string
        except:
            self._node = None
            self.status = color(status, 'yellow')
            self._name = 'TITLE NOT FOUND'


        self._emails = get_emails(self)
        self._children = get_children(self)
        self._loaded = True

    def get_link(self):
        return self._link

    def get_name(self):
        if not self._loaded:
            raise Exception("node is not loaded")
        return self._name
    
    def get_children(self):
        if not self._loaded:
            raise Exception("node is not loaded")
        return self._children

    def get_emails(self):
        if not self._loaded:
            raise Exception("node is not loaded")
        return self._emails