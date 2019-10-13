"""
This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods.
"""
import re
import validators

from bs4 import BeautifulSoup

from .color import color

async def get_emails(node):
    """Finds all emails associated with node

    Args:
        node (LinkNode): Node used to get emails from.

    Returns:
        emails (list): List of emails.
    """
    emails = []
    document = await node.getDocument()
    mails = re.findall(r'[\w\.-]+@[\w\.-]+', document.getText())
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
    for child in await node.children:
        link = child.get('href')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links


async def get_images(node):
    """Finds all images associated with node.

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        links (list): List of links.
    """
    links = []
    for child in await node.children:
        link = child.get('src')
        if link and LinkNode.valid_link(link):
            links.append(link)
    return links

async def get_name(node):
    doc = await node.getDocument()
    if doc.title:
        return doc.title.string
    else:
        return LinkNode.DEFAULT_NAME

async def get_status(node):
    doc = await node.getDocument()
    if not doc.title and not node._status:
        return LinkNode.DEFAULT_STATUS(node.uri)
    elif not node._status:
        return color(node.uri, 'green')


async def get_metadata(node):
    """Collect response headers.

        Args:
            node (LinkNode): Node used to get metadata from.

        Returns:
            headers (CIMultiDictProxy): Dictionary with metadata.
        """

    doc, response = await node.getDocument(True)
    return response.headers

async def get_children(node):
    doc = await node.getDocument()
    return doc.find_all('a')

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
        self._document = None
        self._status = None
        self._uri = link

    async def getDocument(self, get_response=False):
       if not self._document:
            response = await self._session.get(self.uri, compress=True)
            self._document = BeautifulSoup(await response.text('ISO-8859-1'), 'html.parser')
       if get_response:
           return self._document, response
       return self._document

    @property
    async def emails(self):
        """
        Getter for node emails
        """
        if not self._emails:
            self._emails = await get_emails(self)
        return self._emails

    @property
    async def name(self):
        if not self._name:
            return await get_name(self)
        return self._name

    @property
    def uri(self):
        return self._uri

    @property
    def session(self):
        return self._session

    @property
    async def status(self):
        doc = await self.getDocument()
        if not self._status:
            self._status = await get_status(self)
        return self._status

    @property
    async def links(self):
        """
        Getter for node links
        """
        if not self._links:
            self._links = await get_links(self)
        return self._links

    @property
    async def images(self):
        """
        Getter for node images
        """
        if not self._images:
            self._images = await get_images(self)
        return self._images

    @property
    async def children(self):
        """
        Getter for node children
        """
        if not self._children:
            self._children = await get_children(self)
        return self._children

    @property
    async def metadata(self):
        """
        Getter for node metadata
        """
        if not self._metadata:
            self._metadata = await get_metadata(self)
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
