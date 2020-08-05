"""
This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods.
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
        node (LinkNode): Node used to get emails from.

    Returns:
        emails (list): List of emails.
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
        node (LinkNode): Node used to get links from.

    Returns:
        links (list): List of links.
    """
    links = []
    for child in node.children:
        link = child.get('href')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


def get_json_data(node):
    """Finds all link title associated with node

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        titles (list): List of Titles.
    """
    json = []
    for child in node.children:
        link = child.get('href')
        title = "Not Available"
        if link and LinkNode.valid_link(link):
            node = LinkNode(link)
            title = node.name
        json.append({"link":link,"title":title})
    return json    


def get_images(node):
    """Finds all images associated with node.

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        links (list): List of links.
    """
    links = []
    for child in node.children:
        link = child.get('src')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


def get_metadata(node):
    """Collect response headers.

        Args:
            node (LinkNode): Node used to get metadata from.

        Returns:
            metadata (dict): Dictionary with metadata.
        """
    return node.response.headers


class LinkNode:
    """Represents link node in a link tree."""

    def __init__(self, link):
        """Initialises LinkNode object.

        Args:
            link (str): URL used to initialise node.
        """
        # If link has invalid form, throw an error
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self._children = []
        self._emails = []
        self._links = []
        self._images = []
        self._json_data = []
        self._metadata = {}

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
    def json_data(self):
        """
        Getter for node titles
        """
        if not self._json_data:
            self._json_data = get_json_data(self)
        return self._json_data    

    @property
    def links(self):
        """
        Getter for node links
        """
        if not self._links:
            self._links = get_links(self)
        return self._links

    @property
    def images(self):
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

    @property
    def metadata(self):
        """
        Getter for node metadata
        """
        if not self._metadata:
            self._metadata = get_metadata(self)
        return self._metadata

    @staticmethod
    def valid_email(email):
        """Static method used to validate emails.

        Args:
            email (str): Email string to be validated.

        Returns:
            (bool): True if email string is valid, else false.
        """
        if validators.email(email):
            return True
        return False

    @staticmethod
    def valid_link(link):
        """Static method used to validate links

        Args:
            link (str): URL string to be validated.

        Returns:
            (bool): True if URL string is valid, else false.
        """
        if validators.url(link):
            return True
        return False
