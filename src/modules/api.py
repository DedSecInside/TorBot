"""
API Module

Provides access to external services using API wrappers
"""
import requests


class GoTor:
    """
    An API wrapper for the goTor service
    """

    @staticmethod
    def get_node(link, depth, address='localhost', port='8081'):
        """
        Returns the LinkTree for the given link at the specified depth.

        Args:
            link (str): link to be used as a root node.
            depth (int): depth of the tree
            address (str): network address
            port (str): network port
        """
        url = f'http://{address}:{port}/tree?link={link}&depth={depth}'
        resp = requests.get(url)
        return resp.json()
        

    @staticmethod
    def get_ip(address='localhost', port='8081'):
        """
        Returns the IP address of the current Tor client the service is using.

        Args:
            address (str): network address
            port (str): network port
        """
        url = f'http://{address}:{port}/ip'
        resp = requests.get(url)
        return resp.text

    @staticmethod
    def get_emails(link, address='localhost', port='8081'):
        """
        Returns the mailto links found on the page.

        Args:
            link (str): the page to pull the emails from.
            address (str): network address
            port (str): network port
        """
        url = f'http://{address}:{port}/emails?link={link}'
        resp = requests.get(url)
        return resp.json()
