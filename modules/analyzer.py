"""
Module is used for analyzing link relationships
"""
import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from modules import getweblinks, pagereader

class LinkTree:
    def __init__(self, root, tld=False, stop_depth=1):
        self._tree = build_tree(root, tld=tld, stop=stop_depth)

    def __len__(self):
        return len(self._tree)

    def __contains__(self, link):
        return link in self._tree

    def save(self):
        file_name = input("File Name (.t = pdf/.svg./.png): ")
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.render(file_name, tree_style=style)

    def show(self):
        style = TreeStyle()
        style.show_leaf_name = False
        def my_layout(node):
            node_style = TextFace(node.name, tight_text=True)
            add_face_to_node(node_style, node, column=0, position='branch-bottom')
        style.layout_fn = my_layout
        self._tree.show(tree_style=style)

def get_node_children(link, tld):
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        children = getweblinks.get_urls_from_page(soup, tld)
    except (HTTPError, ConnectionError):
        children = []

    return children

def initialize_tree(link, tld):
    root = Tree(name=link)
    html_content = pagereader.read_page(link)
    soup = BeautifulSoup(html_content, 'html.parser')
    to_visit = getweblinks.get_urls_from_page(soup, extension=tld)

    return root, to_visit

def build_tree(link, tld, stop=1, rec=0, to_visit=None, tree=None):
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
    build_tree(to_visit, tld, stop, rec, new_tree)
