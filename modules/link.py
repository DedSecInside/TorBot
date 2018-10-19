import re

import requests
import requests.exceptions
import validators

from bs4 import BeautifulSoup
from .color import color

class LinkNode:

    def __init__(self, link, *, tld=False):
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self.tld = tld
        self._children = []
        self._emails = []

        try:
            self.response = requests.get(link)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, ConnectionError) as err:
            raise err

        self._node = BeautifulSoup(self.response.text, 'html.parser')
        if not self._node.title:
            self.name = "TITLE NOT FOUND"
            self.status = color(link, 'yellow')
        else:
            self.name = self._node.title.string
            self.status = color(link, 'green')

    def get_emails(self):
        if self._emails:
            return self._emails

        children = self._node.find_all('a')
        email_nodes = []
        for child in children:
            link = child.get('href')
            if link and 'mailto' in link:
                email_addr = link.split(':')
                if self.valid_email(email_addr[1]) and len(email_addr) > 1:
                    email_nodes.append(email_addr[1])
        self._emails = email_nodes
        return email_nodes

    def get_children(self):
        if self._children:
            return self._children

        children = self._node.find_all('a')
        child_nodes = []
        for child in children:
            link = child.get('href')
            if link and self.valid_link(link):
                child_nodes.append(link)

        self._children = child_nodes
        return child_nodes

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
