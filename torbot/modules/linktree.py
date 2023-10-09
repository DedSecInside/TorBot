"""
Module is used for analyzing link relationships
"""
import os
import httpx
import validators
import logging

from treelib import Tree, exceptions, Node
from bs4 import BeautifulSoup

from .config import project_root_directory
from .nlp.main import classify


class LinkNode(Node):
    def __init__(self, title: str, url: str, status: int,
                 classification: str, accuracy: float):
        super().__init__()
        self.identifier = url
        self.tag = title
        self.status = status
        self.classification = classification
        self.accuracy = accuracy

class LinkTree(Tree):
    def __init__(self, url: str, depth: int) -> None:
        super().__init__()
        self._url = url
        self._depth = depth
    
    def load(self) -> None:
        self._append_node(id=self._url, parent_id=None)
        self._build_tree(url=self._url, depth=self._depth)

    def _append_node(self, id: str, parent_id: str | None) -> None:
        """
        Creates a node for a tree using the given ID which corresponds to a URL.
        If the parent_id is None, this will be considered a root node.
        """
        resp = httpx.get(id, proxies='socks5://127.0.0.1:9050')
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.text.strip() if soup.title is not None else id
        try:
            [classification, accuracy] = classify(resp.text)
            data = LinkNode(title, id, resp.status_code, classification, accuracy)
            self.create_node(title, identifier=id, parent=parent_id, data=data)
        except exceptions.DuplicatedNodeIdError:
            logging.debug(f"found a duplicate URL {id}")

    def _build_tree(self,  url: str, depth: int) -> None:
        """
        Builds a tree from the root to the given depth.
        """
        if depth > 0:
            depth -= 1
            resp = httpx.get(url, proxies='socks5://127.0.0.1:9050')
            children = parse_links(resp.text)
            for child in children:
                self._append_node(id=child, parent_id=url)
                self._build_tree(url=child, depth=depth)

    def save(self) -> None:
        """
        Saves the tree to the current working directory under the given file name.
        """
        root_id = self.root
        root_node = self.get_node(root_id)
        self.save2file(os.path.join(project_root_directory, root_node.tag))


def parse_links(html: str) -> list[str]:
    """
    Finds all anchor tags and parses the href attribute.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a')
    return [tag['href'] for tag in tags if tag.has_attr('href') and validators.url(tag['href'])]

