"""
Module is used for analyzing link relationships
"""
from requests.exceptions import HTTPError

from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from .link import LinkNode
from .utils import multi_thread

class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can be used to build a tree,
    examine the number of nodes, check if a node exists within a tree, displaying the tree, and
    downloading the tree. It will be expanded in the future to meet further needs.

    Attributes:
        root (str): Represents root link.
        tld (bool): Decides whether or not to use additional top-level-domains besides .tor.
        stop_depth (int): Depth of which to stop searching for links.
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


def initialize_tree(root_node):
    """
    Creates root of tree
    Args:
        link (str): Link node to be used as root.
        tld (bool): Additional top-level-domains.

    Returns:
        root (ete3.Tree): Root node of tree.
        to_visit (list): Children of root node.
    """
    root = Tree(name=root_node.name)
    children = root_node.links
    return root, children


def build_tree(link=None, *, stop=1, rec=0, to_visit=None, tree=None):
    """
    Builds tree using Breadth First Search. You can specify stop depth.
    Rec & tree arguments are used for recursion.

    *NOTE: This function uses a GET request for each url found, this can
    be very expensive so avoid if possible try to acquire the urls to
    be traversed and use bfs function.

    Args:
        link (str): Root node.
        tld (boolean): Specifies if all top-level-domains will be allowed or not.
        stop (int): Stops traversing at this depth if specified.
        rec (int): Used for recursion.
        tree (ete3.Tree): Tree node used for recursion.

    Returns:
        tree (ete3.Tree): Built tree.
    """
    if rec == 0:
        tree, to_visit = initialize_tree(link)

    sub_tree = Tree(name=tree.name)

    if rec == stop:
        # If recursion is 0 then sub_tree will be root
        return sub_tree if rec == 0 else tree

    children_to_visit = list()
    for link in to_visit:
        try:
            node = LinkNode(link)
        except (ValueError, ConnectionError, HTTPError):
            return None
        link_node = sub_tree.add_child(name=node.name)
        link_children = node.links
        for child in link_children:
            link_node.add_child(name=child)
            children_to_visit.append(child)

    rec += 1

    # If we've reached stop depth then return tree
    if stop == rec:
        return sub_tree

    new_tree = tree.add_child(sub_tree)
    return build_tree(to_visit=children_to_visit, stop=stop, rec=rec, tree=new_tree)
