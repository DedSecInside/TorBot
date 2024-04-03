"""
API Module

Provides access to external services using API wrappers
"""
import httpx
import logging

from bs4 import BeautifulSoup, Tag


logging.getLogger("httpx").setLevel(logging.WARNING)


def get_ip(client: httpx.Client) -> dict:
    """
    Returns the IP address of the current Tor client the service is using.
    """
    resp = client.get("https://check.torproject.org/")
    soup = BeautifulSoup(resp.text, "html.parser")

    # Get the content of check tor project, this contains the header and body
    content = soup.find("div", {"class": "content"})
    if not content:
        raise Exception("unable to find content to parse IP.")

    # parse the header
    header_tag = content.find("h1")
    if not header_tag:
        raise Exception("unable to find header")
    if not isinstance(header_tag, Tag):
        raise Exception("invalid header found")
    header = header_tag.get_text().strip()

    # parse the main content containing the IP address
    body_tag = content.find("p")
    if not body_tag:
        raise Exception("unable to find body")
    if not isinstance(body_tag, Tag):
        raise Exception("invalid body found")
    body = body_tag.get_text().strip()

    return {"header": header, "body": body}
