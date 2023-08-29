"""
Module is used for analyzing link relationships
"""
import os

from treelib import Tree, exceptions

from .api import get_node
from .config import get_data_directory
from .log import debug


def formatNode(n):
    return f"{n['url']} {n['status_code']} {n['status']}"


def build_tree_recursive(t, n):

    # this will only be ran on the root node since others will exist before being passed
    parent_id = n["url"]
    if not t.contains(parent_id):
        debug(f"adding id {parent_id}")
        t.create_node(formatNode(n), parent_id)

    # if there are no children, there's nothing to process
    children = n["children"]
    if not children:
        return

    for child in children:
        try:
            child_id = child["url"]
            debug(f"adding child_id {child_id} to parent_id {parent_id}")
            t.create_node(formatNode(child), child_id, parent=parent_id)
        except exceptions.DuplicatedNodeIdError:
            debug(f"found a duplicate url {child_id}")
            continue  # this node has already been processed somewhere else

        build_tree_recursive(t, child)


class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can
    be used to build a tree, examine the number of nodes, check if a node
    exists within a tree, displaying the tree, and downloading the tree. It
    will be expanded in the future to meet further needs.
    """

    def __init__(self, root: str, depth: int):
        self.__build_tree(root, depth)

    def __build_tree(self, url: str, depth: int = 1):
        """
        Builds link tree by traversing through children nodes.

        Returns:
            tree (ete3.Tree): Built tree.
        """
        debug(f"building tree for {url} at {depth} depth")
        n = get_node(url, depth)
        t = Tree()
        build_tree_recursive(t, n)
        self._tree = t
        debug("tree built successfully")

    def save(self, file_name: str):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .txt
        """
        print(f"saving link tree as {file_name}")
        data_directory = get_data_directory()
        file_path = os.path.join(data_directory, file_name)
        try:
            self._tree.save2file(file_path)
        except Exception as e:
            print(f"failed to save link tree to {file_path}")
            debug(e)
            raise e

        print(f"file saved successfully to {file_path}")

    def show(self):
        """
        Displays image of LinkTree
        """
        self._tree.show()
