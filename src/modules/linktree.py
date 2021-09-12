"""
Module is used for analyzing link relationships
"""
from ete3 import faces, Tree, TreeStyle, TextFace
from .utils import join_local_path
from .api import GoTor

def default_layout(node):
    """
    Default layout for node
    """
    node_style = TextFace(node.name, tight_text=True)
    faces.add_face_to_node(node_style, node, column=0, position='branch-bottom')


default_style = TreeStyle()
default_style.show_leaf_name = False
default_style.layout_fn = default_layout

class LinkTree:
    """
    This is a class that represents a tree of links within TorBot. This can
    be used to build a tree, examine the number of nodes, check if a node
    exists within a tree, displaying the tree, and downloading the tree. It
    will be expanded in the future to meet further needs.

    Attributes:
        root (str): root node
        depth (int): depth of tree
    """
    def __init__(self, root, depth):
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

    def __build_tree(self, url, depth=1):
        """
        Builds link tree by traversing through children nodes.

        Args:
            url (str): root node of tree
            depth(int): depth of tree

        Returns:
            tree (ete3.Tree): Built tree.
        """
        root = GoTor.get_node(url, depth)
        root_tree = Tree(name=root['url'])
        if root['children']:
            for child in root['children']:
                self.__append_node(root_tree, child)
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

    def save(self, file_name, tree_style=default_style):
        """
        Saves LinkTree to file with given file_name
        Current file types supported are .png, .pdf, .svg

        Args:
            file_name (str): Name of file being saved to
            tree_style (TreeStyle): Styling of downloaded tree
        """
        self._tree.layout_fn = default_layout
        file_path = join_local_path(file_name)
        self._tree.render(file_path, tree_style=tree_style)

    def show(self, tree_style=default_style):
        """
        Displays image of LinkTree

        Args:
            tree_style (TreeStyle): Styling of downloaded tree
        """
        self._tree.layout_fn = default_layout
        self._tree.show(tree_style=tree_style)

