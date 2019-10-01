"""

This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods

"""
import requests
import requests.exceptions
import validators
import re
from bs4 import BeautifulSoup
from .utils import multi_thread
from .color import color

def get_emails(node):
    """Finds all emails associated with node

    Args:
        node (LinkNode): node used to get emails from
    Returns:
        emails (list): list of emails
    """
    emails = []
    response = node.response.text
    mails = re.findall(r'[\w\.-]+@[\w\.-]+', response)
    for email in mails:
        if LinkNode.valid_email(email):
            emails.append(email)
    return emails


def get_links(node):
    """Finds all links associated with node

    Args:
        node (LinkNode): node used to get links from
    Returns:
        links (list): list of links
    """
    links = []
    for child in node.children:
        link = child.get('href')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


def get_images(node):
    """Finds all images associated with node

    Args:
        node (LinkNode): node used to get links from
    Returns:
        links (list): list of links
    """
    links = []
    for child in node.children:
        link = child.get('src')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


class LinkNode:
    """Represents link node in a link tree

    Attributes:
        link (str): link to be used as node
    """

    def __init__(self, link):
        # If link has invalid form, throw an error
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self._children = []
        self._emails = []
        self._links = []
        self._images = []

        # Attempts to connect to link, throws an error if link is unreachable
        try:
            self.response = requests.get(link)
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                ConnectionError) as err:
            raise err

        self._node = BeautifulSoup(self.response.text, 'html.parser')
        self.uri = link
        if not self._node.title:
            self.name = "TITLE NOT FOUND"
            self.status = color(link, 'yellow')
        else:
            self.name = self._node.title.string
            self.status = color(link, 'green')

    @property
    def emails(self):
        """
        Getter for node emails
        """
        if not self._emails:
            self._emails = get_emails(self)
        return self._emails

    @property
    def links(self):
        """
        Getter for node links
        """
        if not self._links:
            self._links = get_links(self)
        return self._links

    @property
    def links(self):
        """
        Getter for node images
        """
        if not self._images:
            self._images = get_images(self)
        return self._images

    @property
    def children(self):
        """
        Getter for node children
        """
        if not self._children:
            self._children = self._node.find_all('a')
        return self._children

    @staticmethod
    def valid_email(email):
        """Static method used to validate emails"""
        if validators.email(email):
            return True
        return False

    @staticmethod
    def valid_link(link):
        """Static method used to validate links"""
        if validators.url(link):
            return True
        return False
