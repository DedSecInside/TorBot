"""
This module is used to create a LinkNode that can be consumued by a LinkTree
and contains useful Link methods.
"""
import re
import requests
from bs4 import BeautifulSoup

from .color import color
from .validators import validate_email, validate_link


def get_meta_tags(node):
    """Retrieve all meta elements from HTML object.

    Args:
        soup (BeautifulSoup)

    Returns:
        list: List containing content from meta tags
    """
    meta_tags = node._node.find_all('meta')
    content_list = list()
    for tag in meta_tags:
        content_list.append(tag.attrs)
    return content_list


def get_emails(node):
    """Finds all emails associated with node

    Args:
        node (LinkNode): Node used to get emails from.

    Returns:
        emails (list): List of emails.
    """
    emails = []
    mails = re.findall(r'[\w\.-]+@[\w\.-]+', node._node.get_text())
    for email in mails:
        if validate_email(email):
            emails.append(email)
    return emails


def get_children(node):
    children  = []
    for anchor_tag in node._node.find_all('a'):
        link = anchor_tag.get('href')
        if validate_link(link):
            chlid_node = LinkNode(link)
            children.append(chlid_node)
    return children


def get_json_data(node):
    """Finds all link title associated with node

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        titles (list): List of Titles.
    """
    json = []
    for anchor_tag in node._node.find_all('a'):
        link = anchor_tag.get('href')
        json.append({"link": link, "tag": anchor_tag.get_text()})
    return json    


def get_images(node):
    """Finds all images associated with node.

    Args:
        node (LinkNode): Node used to get links from.

    Returns:
        imageEls (list): A collection of img HTML elements 
    """
    imageEls = []
    for anchor_tag in node._node.find_all('a'):
        image = anchor_tag.get('src')
        if validate_link(image):
            imageEls.append(image)
    return imageEls 


class LinkNode:
    """Represents link node in a link tree."""

    def __init__(self, link):
        """Initialises LinkNode object.

        Args:
            link (str): URL used to initialise node.
        """
        # If link has invalid form, throw an error
        if not validate_link(link):
            raise ValueError("Invalid link format.")

        self._loaded = False
        self._name = link
        self._link = link
        self._meta_tags = []
        self._body = ""

    def load_data(self):
        response = requests.get(self._link)
        status = str(response.status_code)
        try:
            response.raise_for_status()
            self._metadata = response.headers 
            self._node = BeautifulSoup(response.text, 'html.parser')
            self.status = color(status, 'green')
            self._name = self._node.title.string
            self._emails = get_emails(self)
            self._children = get_children(self)
            self._emails = get_emails(self)
            self._images = get_images(self)
            self._json_data = get_json_data(self)
            self._body = self._node.find('body')
        except Exception:
            self._node = None
            self.status = color(status, 'yellow')
            self._name = 'TITLE NOT FOUND'
        finally:
            self._loaded = True

    def get_body(self):
        return self._body

    def get_link(self):
        return self._link

    def get_name(self):
        if not self._loaded:
            self.load_data()
        return self._name

    def get_children(self):
        if not self._loaded:
            self.load_data()
        return self._children

    def get_emails(self):
        if not self._loaded:
            self.load_data()
        return self._emails 
    
    def get_json(self):
        if not self._loaded:
            self.load_data()
        return self._json_data
    
    def get_meta_tags(self):
        if not self._loaded:
            self.load_data()
        return self._meta_tags

    def get_metadata(self):
        if not self._loaded:
            self.load_data()
        return self._metadata
