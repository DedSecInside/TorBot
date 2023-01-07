"""
Module is used for analyzing link relationships
"""
from treelib import Node, Tree, exceptions

from .api import get_node
from .utils import join_local_path
from .log import info, debug

def formatNode(n):
    return f"{n['url']} {n['status_code']} {n['status']}"

def build_tree_recursive(t, n):

    # this will only be ran on the root node since others will exist before being passed
    if not t.contains(n["url"]):
        debug(f"adding root node {n}")
        t.create_node(formatNode(n), n["url"])

    # if there are no children, there's nothing to process
    if not n["children"]:
        return

    for child in n["children"]: 
        id = child["url"]
        parent_id = n["url"]
        try:
            debug(f"adding node {child}")
            debug(f"parent_id {parent_id}")
            t.create_node(formatNode(child), child["url"], parent=n["url"])
        except exceptions.DuplicatedNodeIdError:
            debug(f"found a duplicate url {child['url']}")
            continue # this node has already been processed somewhere else 

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
        debug(f"building tree for {root} at {depth} depth")
        n = get_node(url, depth)
        t = Tree()
        build_tree_recursive(t, n)
        self._tree = t; 
        debug("tree built successfully")

    def save(self, file_name: str):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .png, .pdf, .svg
        """
        debug(f"saving link tree as {file_name}")
        file_path = join_local_path(file_name)
        self._tree.save2file(file_path)
        debug(f"file saved successfully to {file_path}")

    def show(self):
        """
        Displays image of LinkTree
        """
        self._tree.show()
