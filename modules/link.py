"""
This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods.
"""
import re
import requests
import requests.exceptions
import validators

from bs4 import BeautifulSoup
from enum import Enum

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


async def get_links(node):
    """Finds all links associated with node

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        links (list): List of links.
    """
    links = []
    children = await node.children
    for child in children:
        link = child.get('href')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


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
    DEFAULT_NAME = 'TITLE NOT FOUND'
    DEFAULT_STATUS = lambda uri: color(uri, 'yellow')

    def __init__(self, link, session):
        """Initialises LinkNode object.

        Args:
            link (str): URL used to initialise node.
        """
        self._session = session
        # If link has invalid form, throw an error
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self._children = []
        self._emails = []
        self._links = []
        self._images = []
        self._metadata = {}
        self._name = None
        self._text = None
        self._node = None
        self._uri = link

    @property
    async def status(self):
        n = await self.node
        if not n.title and not self._status:
            self._status = self.DEFAULT_STATUS(self.uri)
        elif not self._status:
            self._status = color(self.uri, 'green')
        return self._status

    @property
    def uri(self):
        return self._uri

    @property
    async def text(self):
        if not self._text:
            n = await self.node
            self._text = n.getText()
        return self._text


    @property
    async def node(self):
       if not self._node:
           try:
                async with self._session.get(self.uri) as response:
                    self._node = BeautifulSoup(await response.text('ISO-8859-1'), 'html.parser')
                    return self._node
           except Exception as err:
               return None

    @property
    def name(self):
        if not self._name:
            self._name = self.DEFAULT_NAME
        else:
            self._name = self.node.title.string

        return self._name

    @property
    def session(self):
        return self._session

    @property
    def emails(self):
        """
        Getter for node emails
        """
        if not self._emails:
            self._emails = get_emails(self)
        return self._emails

    @property
    async def links(self):
        """
        Getter for node links
        """
        if not self._links:
            self._links = await get_links(self)
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
    async def children(self):
        """
        Getter for node children
        """
        if not self._children:
            n = await self.node
            self._children = n.find_all('a')
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
