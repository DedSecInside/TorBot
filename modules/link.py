import re

import requests
import validators
from requests.exceptions import HTTPError

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
        except (HTTPError, ConnectionError) as err:
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

        emails = []
        children = self.get_children()
        for child in children:
            link = child.get('href')
            if link and 'mailto' in link:
                email_addr = link.split(':')
                if len(email_addr) > 1:
                    emails.append(email_addr[1])

        self._emails = emails
        return emails

    def get_children(self):
        if self._children:
            return self._children

        children = self._node.find_all('a')
        child_nodes = list()
        for child in children:
            link = child.get('href')
            if link and self.valid_link(link):
                child_nodes.append(link)

        self._children = child_nodes
        return child_nodes


    @staticmethod
    def valid_link(link):
        if validators.url(link):
            return True
        return False
