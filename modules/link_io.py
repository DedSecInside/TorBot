"""
This module is used for reading HTML pages using either bs4.BeautifulSoup objects or url strings
"""
import requests.exceptions
from bs4 import BeautifulSoup

from .link import LinkNode
from .utils import multi_thread
from .color import color

class LinkIO:
    """
    This class is only used to interact with links
    """
    @staticmethod
    def display_children(root):
        """
        Static method to display status of child nodes

        Args:
            root (LinkNode): root of children to be displayed
        """
        sucess_msg = color(f'Links Found - {len(root.links)}', 'green')
        print(sucess_msg + '\n' + '---------------------------------')
        multi_thread(root.links, LinkIO.display)

    @staticmethod
    def read(link, *, response=False, show_msg=False, headers=None, schemes=None):
        """
        Attempts to retrieve HTML from link

        Args:
            link (str): link to read
            response (bool): determines if response is returned.
            show_msg(bool): determines if message is displayed for connection
            headers (dict): header for request, defaults to None
            schemes (list): differenct schemes to attempt to use
        Returns:
            str: html from page
            requests.Response (optional): response returned from requests

        """
        headers = {'User-Agent': 'XXXX-XXXXX-XXXX'} if not headers else headers
        # Attempts to connect directly to site if no scheme is passed
        if not schemes:
            if show_msg:
                print(f'Attempting to connect to {link}')
            if LinkNode.valid_link(link):
                node = LinkNode(link)
                if response:
                    return node.response.text, node.response
                return node.response.text

        schemes = ['https://', 'http://'] if not schemes else schemes
        # Attempt to use different schemes until one is successful
        for scheme in schemes:
            temp_url = scheme + link
            if show_msg:
                print(f'Attempting to connect to {link}')
            if LinkNode.valid_link(temp_url):
                node = LinkNode(temp_url)
                if response:
                    return node.response.text, node.response
                return node.response.text
        raise ConnectionError

    @staticmethod
    def display(link):
        """
        Prints the status of a link based on it's connection status

        Args:
            link (str): link to get status of
        """
        if LinkNode.valid_link(link):
            try:
                node = LinkNode(link)
                title = node.name
                link_status = node.status
            except (requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    ConnectionError):
                title = 'Not Found'
                link_status = color(link, 'red')

        status_msg = "%-80s %-30s" % (link_status, title)
        print(status_msg)


    @staticmethod
    def display_ip():
        """
        https://check.torproject.org/ tells you if you are using tor and it
        displays your IP address which we scape and display
        """

        page = LinkIO.read('https://check.torproject.org/', show_msg=True)
        page = BeautifulSoup(page, 'html.parser')
        ip_cont = page.find('strong')
        ip_addr = ip_cont.renderContents()
        ip_string = color(ip_addr.decode("utf-8"), 'yellow')
        print(f'Tor IP Address: {ip_string}')
