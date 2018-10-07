import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node

from modules import getweblinks, pagereader

def build_tree(link, tld, stop=None, rec=0, to_visit=None, tree=None):
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
        tree = Tree(name=link)
        html_content = pagereader.read_page(link)
        soup = BeautifulSoup(html_content, 'html.parser')
        to_visit = getweblinks.get_urls_from_page(soup, extension=tld)

    t = Tree(name=tree.name)

    if rec == stop:
        # If recursion is 0 then t will be root
        return t if rec == 0 else tree

    children_to_visit = list()
    for url in to_visit:
        parent = t.add_child(name=url)
        try:
            resp = requests.get(url)
        except (HTTPError, ConnectionError):
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        urls = getweblinks.get_urls_from_page(soup, extension=tld)
        # No need to find children if we aren't going to visit them
        if stop != rec + 1:
            for child_url in urls:
                parent.add_child(name=child_url)
                children_to_visit.append(child_url)
    child = tree.add_child(t)
    rec += 1

    # If we've reached stop depth then return tree
    return t if stop == rec else build_tree(to_visit, tld, stop, rec, child)

def show_graph(link, extension):
    tree = build_tree(link, tld=extension, stop=1)
    style = TreeStyle()
    style.show_leaf_name = False
    def my_layout(node):
        node_style = TextFace(node.name, tight_text=True)
        add_face_to_node(node_style, node, column=0, position='branch-bottom')
    style.layout_fn = my_layout
    file_name = input("File Name (.pdf/.svg./.png): ")
    tree.render(file_name, tree_style=style)
