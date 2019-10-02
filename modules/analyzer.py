"""
Module is used for analyzing link relationships
"""
from requests.exceptions import HTTPError

from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from .link import LinkNode
from .utils import multi_thread

class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can
    be used to build a tree, examine the number of nodes, check if a node
    exists within a tree, displaying the tree, and downloading the tree. It
    will be expanded in the future to meet further needs.

    Attributes:
        root (LinkNode): root node
        stop_depth (int): Depth of which to stop searching for links
    """
    def __init__(self, root_node, *, stop_depth=1):
        """
        Initialise LinkTree object with root node and depth to search.
        """
        self._tree = build_tree(root_node, stop=stop_depth)

    def __len__(self):
        return len(self._tree)

    def __contains__(self, link):
        return self._tree.search_nodes(name=link)

    def save(self, file_name):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .png, .pdf, .svg

        Args:
            file_name (str): Name of file being saved to.
        """
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            """ Style node for display.

            Args:
                node (object): Node object to be styled.
            """
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.render(file_name, tree_style=style)

    def show(self):
        """Allows user to quickly view LinkTree."""
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            """ Style node for display.

            Args:
                node (object): Node object to be styled.
            """
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.show(tree_style=style)


def build_tree(link=None, depth=0, rec=0):
    """
    Builds link tree by traversing through children nodes.

    Returns:
        tree (ete3.Tree): Built tree.
    """

    tree = Tree(name=link.name)

    if rec_depth == stop_depth:
        return tree
    else:
        rec_depth += 1

    for link in link.links:
        try:
            node = LinkNode(link)
        except (ValueError, ConnectionError, HTTPError):
            return None

        if node.links:
            tree = tree.add_child(build_tree(node, stop_depth, rec_depth))

    return tree
