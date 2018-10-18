import re

import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from .color import color

class LinkNode:

    def __init__(self, link, *, tld=False):

        if tld:
            if not self.valid_link(link):
                raise ValueError("Invalid link format.")
        elif not self.valid_tor_link(link):
            raise ValueError("Invalid tor link format.")

        self.tld = tld
        self._children = []
        self._emails = []

        try:
            self.response = requests.get(link)
            self._node = BeautifulSoup(self.response.text, 'html.parser')
            self.name = self._node.title.string
            self.status = color(link, 'green')
        except (HTTPError, ConnectionError) as err:
            raise err

    def get_emails(self):
        if len(self._emails) > 0:
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
        if len(self._children) > 0:
            return self._children

        children = self._node.find_all('a')
        child_nodes = list()
        for child in children:
            link = child.get('href')
            general_link = self.tld and link and self.valid_link(link)
            tor_link = link and self.valid_tor_link(link)
            if general_link or tor_link:
                child_nodes.append(link)

        self._children = child_nodes
        return child_nodes


    @staticmethod
    def valid_link(link):
        pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.([a-z, A-Z]+)(.*)"
        regex = re.compile(pattern)
        if regex.match(link):
            return True
        return False

    @staticmethod
    def valid_tor_link(link):
        pattern = r"^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.onion/(.*)"
        regex = re.compile(pattern)
        if regex.match(link):
            return True
        return False
