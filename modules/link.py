"""

This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods

"""
import requests
import requests.exceptions
import validators

from bs4 import BeautifulSoup
from .utils import multi_thread
from .color import color

def get_emails(node):
    """Finds all emails associated with node

    Args:
        node (LinkNode)
    """
    email_nodes = []
    for child in node.children:
        link = child.get('href')
        if link and 'mailto' in link:
            email_addr = link.split(':')
            if LinkNode.valid_email(email_addr[1]) and len(email_addr) > 1:
                email_nodes.append(email_addr[1])
    return email_nodes


def get_links(node):
    def retrieve_link(child):
        link = child.get('href')
        if LinkNode.valid_link(link) and link:
            return link
        return None

    return multi_thread(node.children, retrieve_link)


class LinkNode:
    """Represents link node in a link tree

    Attributes:
        link (str): link to be used as node
    """

    def __init__(self, link):
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self._children = []
        self._emails = []
        self._links = []

        try:
            self.response = requests.get(link)
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                ConnectionError) as err:
            raise err

        self._node = BeautifulSoup(self.response.text, 'html.parser')
        if not self._node.title:
            self.name = "TITLE NOT FOUND"
            self.status = color(link, 'yellow')
        else:
            self.name = self._node.title.string
            self.status = color(link, 'green')

    @property
    def emails(self):
        if not self._emails:
            self._emails = get_emails(self)
        return self._emails

    @property
    def links(self):
        if not self._links:
            self._links = get_links(self)
        return self._links

    @property
    def children(self):
        if not self._children:
            self._children = self._node.find_all('a')
        return self._children

    @staticmethod
    def valid_email(email):
        if validators.email(email):
            return True
        return False

    @staticmethod
    def valid_link(link):
        if validators.url(link):
            return True
        return False
