"""
Module is used for analyzing link relationships
"""
import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from .getweblinks import get_urls_from_page
from .pagereader import read


class Node:
    """Represents each webpage, has two attributes- one which has the url of the webpage and the other has the title (if mentioned) of the webpage """
    def __init__(self, title="", link):
        self.title=title 
        self.link=link
        
class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can be used to build a tree,
    examine the number of nodes, if a node exists within a tree, displaying the tree and
    downloading the tree, and will be expanded in the future to meet further needs.

    Attributes:
        root (str): Represents root link
        tld (bool): Decides whether or not to use additional top-level-domains besides .tor
        stop_depth (int): Depth of which to stop searching for links
    """
    def __init__(self, root, tld=False, stop_depth=1):
        self._tree = build_tree(root, tld=tld, stop=stop_depth)

    def __len__(self):
        return len(self._tree)

    def __contains__(self, link):
        return link in self._tree

    def save(self, file_name):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .png, .pdf, .svg

        Args:
            file_name (str): Name of file being saved to
        """
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.render(file_name, tree_style=style)

    def show(self):
        """
        Allows user to quickly view LinkTree
        """
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.show(tree_style=style)

def get_node_children(link, tld):
    """
    Returns children for link node

    Args:
        link (str): link node to get children for
        tld (bool): Additional top-level-domains
    Returns:
        children (list): A list of children from linknode
    """
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        children = get_urls_from_page(soup, tld)
    except (HTTPError, ConnectionError):
        children = []
    return children

def initialize_tree(link, tld):
    """
    Creates root of tree
    Args:
        link (str): link node to be used as root
        tld (bool): Additional top-level-domains
    Returns:
        root (ete3.Tree): root node of tree
        to_visit (list): Children of root node
    """
    root = Tree(name=link)
    html_content = read(link)
    soup = BeautifulSoup(html_content, 'html.parser')
    to_visit = get_urls_from_page(soup, extension=tld)
    return root, to_visit

def build_tree(link, tld, stop=1, *, rec=0, to_visit=None, tree=None):
    """
    Builds tree using Breadth First Search. You can specify stop depth.
    Rec & tree arguments are used for recursion.

    *NOTE: This function uses a GET request for each url found, this can
    be very expensive so avoid if possible try to acquire the urls to
    be traversed and use bfs function.

    Args:
        link (str): root node
        tld (boolean): specifies if all top-level-domains will be allowed or not
        stop (int): stops traversing at this depth if specified
        rec (int): used for recursion
        tree (ete3.Tree): a tree node used for recursion

    Returns:
        tree (ete3.Tree): built tree
    """
    if rec == 0:
        tree, to_visit = initialize_tree(link, tld)

    sub_tree = Tree(name=tree.name)

    if rec == stop:
        # If recursion is 0 then sub_tree will be root
        return sub_tree if rec == 0 else tree

    children_to_visit = list()
    for link_name in to_visit:
        link_node = sub_tree.add_child(name=link_name)
        link_children = get_node_children(link_name, tld)
        # No need to find children if we aren't going to visit them
        if stop != rec + 1:
            for child in link_children:
                link_node.add_child(name=child)
                children_to_visit.append(child)
    rec += 1

    # If we've reached stop depth then return tree
    if stop == rec:
        return sub_tree

    new_tree = tree.add_child(sub_tree)
    return build_tree(to_visit, tld, stop, rec=rec, tree=new_tree)
