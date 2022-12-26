"""
Module is used for analyzing link relationships
"""

from ete3 import Tree

from .api import get_node
from .utils import join_local_path
from .log import info


class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can
    be used to build a tree, examine the number of nodes, check if a node
    exists within a tree, displaying the tree, and downloading the tree. It
    will be expanded in the future to meet further needs.
    """

    def __init__(self, root: str, depth: int):
        self._tree = self.__build_tree(root, depth)

    def __append_node(self, parent_tree, node):
        """
        Appends the node and it's children to the parent tree
        """
        child_tree = Tree(name=node['url'])
        parent_tree.add_child(child_tree)
        if node['children']:
            for child in node['children']:
                self.__append_node(child_tree, child)

    def __build_tree(self, url: str, depth: int = 1):
        """
        Builds link tree by traversing through children nodes.

        Returns:
            tree (ete3.Tree): Built tree.
        """
        info(f"building tree for {url} at {depth}")
        root = get_node(url, depth)
        root_tree = Tree(name=root['url'])
        if root['children']:
            for child in root['children']:
                self.__append_node(root_tree, child)
        info(f"tree built {root_tree}")
        return root_tree

    def __len__(self):
        return len(self._tree)

    def __contains__(self, link):
        return self._tree.search_nodes(name=link)

    @property
    def children(self):
        """
        Returns the number of children within the LinkTree
        """
        return self._tree.get_children()

    def save(self, file_name: str):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .png, .pdf, .svg
        """
        file_path = join_local_path(file_name)
        self._tree.render(file_path)

    def show(self):
        """
        Displays image of LinkTree
        """
        self._tree.show()
