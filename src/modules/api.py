"""
API Module

Provides access to external services using API wrappers
"""
import requests


class GoTor:
    """
    An API wrapper for the goTor service
    """
    def __init__(self, address='localhost', port='8081'):
        self._address = address
        self._port = port
        self._base_url = f'http://{address}:{port}'

    def _format_url(self, endpoint):
        return f'{self._base_url}{endpoint}'

    def get_ip(self):
        """
        Returns the IP address of the current Tor client the service is using.
        """
        url = self._format_url('/ip')
        resp = requests.get(url)
        return resp.text

    def get_node(self, link, depth):
        """
        Returns the LinkTree for the given link at the specified depth.

        Args:
            link (str): link to be used as a root node.
            depth (int): depth of the tree
        """
        url = self._format_url(f'/tree?link={link}&depth={depth}')
        resp = requests.get(url)
        return resp.json()

    def get_emails(self, link):
        """
        Returns the mailto links found on the page.

        Args:
            link (str): the page to pull the emails from.
        """
        url = self._format_url(f'/emails?link={link}')
        resp = requests.get(url)
        return resp.json()
