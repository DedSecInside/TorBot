"""
This module is used for reading HTML pages using either bs4.BeautifulSoup
objects or url strings
"""

import aiohttp
from display_status import display_status

from bs4 import BeautifulSoup

from .link import LinkNode
from .color import color


class LinkIO:
    """
    Class to interact with and interrogate links.
    """
    @staticmethod
    async def display_children(root):
        """
        Static method to display status of child nodes.

        Args:
            root (LinkNode): root of children to be displayed.
        """
        root_children = await root.links
        sucess_msg = color(f'Links Found - {len(root_children)}', 'green')
        print(sucess_msg + '\n' + '---------------------------------')

        display_status.display(*root_children)

    @staticmethod
    async def read(link, *,
        response=False,
        show_msg=False,
        headers=None,
        schemes=None,
        session=None):
        """
        Attempts to retrieve HTML from link.

        Args:
            link (str): Link to read.
            response (bool): Determines if response is returned.
            show_msg (bool): Determines if message is displayed for connection.
            headers (dict): Header for request, defaults to None.
            schemes (list): Different schemes to attempt to use.

        Returns:
            str: HTML from page.
            requests.Response (optional): Response returned from requests.
        """
        headers = {'User-Agent': 'XXXX-XXXXX-XXXX'} if not headers else headers
        # Attempts to connect directly to site if no scheme is passed
        if not schemes:
            if show_msg:
                print(f'Attempting to connect to {link}')
            if LinkNode.valid_link(link):
                return LinkNode(link, session)

        schemes = ['https://', 'http://'] if not schemes else schemes
        # Attempt to use different schemes until one is successful
        for scheme in schemes:
            uri = scheme + link
            if show_msg:
                print(f'Attempting to connect to {link}')
            if LinkNode.valid_link(uri):
                return LinkNode(uri, session)

        raise ConnectionError

    @staticmethod
    async def display(link, session):
        """
        Prints the status of a link based on it's connection status.

        Args:
            link (str): Link to return status of.
        """
        if LinkNode.valid_link(link):
            try:
                node = LinkNode(link, session)
                title = await node.name
                link_status = await node.status
            except Exception as err:
                title = 'Not Found'
                link_status = color(link, 'red')

        status_msg = "%-80s %-30s" % (link_status, title)
        print(status_msg)

    @staticmethod
    async def display_ip(session):
        """
        Uses https://check.torproject.org/ to determine if you
        are using Tor which is then scraped and displayed.
        """
        link = await LinkIO.read('https://check.torproject.org/', show_msg=True, session=session)
        document = await link.getDocument()
        ip_cont = document.find('strong')
        ip_addr = ip_cont.renderContents()
        ip_string = color(ip_addr.decode("utf-8"), 'yellow')
        print(f'Tor IP Address: {ip_string}')
