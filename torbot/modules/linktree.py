"""
Module is used for analyzing link relationships
"""
import os
import httpx
import validators
import logging

from treelib import Tree, exceptions, Node
from bs4 import BeautifulSoup

from .nlp.main import classify


class Link(Node):
    def __init__(self, title: str, url: str, status: int, classification: str, accuracy: float):
        self.identifier = url
        self.tag = title
        self.status = status
        self.classification = classification
        self.accuracy = accuracy


def parse_links(html: str) -> list[str]:
    """
    Finds all anchor tags and parses the href attribute.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a')
    return [tag['href'] for tag in tags if tag.has_attr('href') and validators.url(tag['href'])]


def append_node(tree: Tree, id: str, parent_id: str | None) -> None:
    """
    Creates a node for a tree using the given ID which corresponds to a URL.
    If the parent_id is None, this will be considered a root node.
    """
    resp = httpx.get(id, proxies='socks5://127.0.0.1:9050')
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.text.strip() if soup.title is not None else id
    try:
        [classification, accuracy] = classify(resp.text)
        data = Link(title, id, resp.status_code, classification, accuracy)
        tree.create_node(title, identifier=id, parent=parent_id, data=data)
    except exceptions.DuplicatedNodeIdError:
        logging.debug(f"found a duplicate URL {id}")


def build_tree(tree: Tree, url: str, depth: int) -> None:
    """
    Builds a tree from the root to the given depth.
    """
    if depth > 0:
        depth -= 1
        resp = httpx.get(url, proxies='socks5://127.0.0.1:9050')
        children = parse_links(resp.text)
        for child in children:
            append_node(tree, id=child, parent_id=url)
            build_tree(tree, child, depth)


def save(tree: Tree, file_name: str) -> None:
    """
    Saves the tree to the current working directory under the given file name.
    """
    tree.save2file(os.path.join(os.getcwd(), file_name))


def show(tree: Tree) -> None:
    """
    Prints the tree
    """
    tree.show()
