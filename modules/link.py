import requests
import requests.exceptions
import validators

from bs4 import BeautifulSoup
from .utils import multi_thread
from .color import color

class LinkNode:

    def __init__(self, link):
        if not self.valid_link(link):
            raise ValueError("Invalid link format.")

        self._children = []
        self._emails = []

        try:
            self.response = requests.get(link)
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.HTTPError, requests.exceptions.ConnectionError, ConnectionError) as err:
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
        if not self._children:
            children = self._node.find_all('a')
            def retrieve_link(child):
                link = child.get('href')
                if link and self.valid_link(link):
                    return link
            self._children = multi_thread(children, retrieve_link)

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
