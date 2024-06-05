#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011
# Brett Alistair Kromkamp - brettkromkamp@gmail.com
# Copyright (C) 2012-2017
# Xiaming Chen - chenxm35@gmail.com
# and other contributors.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tree structure in `treelib`.

The :class:`Tree` object defines the tree-like structure based on :class:`Node` objects.
A new tree can be created from scratch without any parameter or a shallow/deep copy of another tree.
When deep=True, a deepcopy operation is performed on feeding tree parameter and more memory
is required to create the tree.
"""
from __future__ import print_function
from __future__ import unicode_literals

try:
    from builtins import str as text
except ImportError:
    from __builtin__ import str as text

import codecs
import json
import sys
import uuid
from copy import deepcopy

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .exceptions import *
from .node import Node

__author__ = 'chenxm'


def python_2_unicode_compatible(klass):
    """
    (slightly modified from: http://django.readthedocs.org/en/latest/_modules/django/utils/encoding.html)

    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if sys.version_info[0] == 2:
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


@python_2_unicode_compatible
class Tree(object):
    """Tree objects are made of Node(s) stored in _nodes dictionary."""

    #: ROOT, DEPTH, WIDTH, ZIGZAG constants :
    (ROOT, DEPTH, WIDTH, ZIGZAG) = list(range(4))
    node_class = Node

    def __contains__(self, identifier):
        return identifier in self.nodes.keys()

    def __init__(self, tree=None, deep=False, node_class=None, identifier=None):
        """Initiate a new tree or copy another tree with a shallow or
        deep copy.
        """
        self._identifier = None
        self._set_identifier(identifier)

        if node_class:
            assert issubclass(node_class, Node)
            self.node_class = node_class

        #: dictionary, identifier: Node object
        self._nodes = {}

        #: Get or set the identifier of the root. This attribute can be accessed and modified
        #: with ``.`` and ``=`` operator respectively.
        self.root = None

        if tree is not None:
            self.root = tree.root
            for nid, node in tree.nodes.items():
                new_node = deepcopy(node) if deep else node
                self._nodes[nid] = new_node
                if tree.identifier != self._identifier:
                    new_node.clone_pointers(tree.identifier, self._identifier)

    def _clone(self, identifier=None, with_tree=False, deep=False):
        """Clone current instance, with or without tree.

        Method intended to be overloaded, to avoid rewriting whole "subtree" and "remove_subtree" methods when
        inheriting from Tree.
        >>> class TreeWithComposition(Tree):
        >>>     def __init__(self, tree_description, tree=None, deep=False, identifier=None):
        >>>         self.tree_description = tree_description
        >>>         super(TreeWithComposition, self).__init__(tree=tree, deep=deep, identifier=identifier)
        >>>
        >>>     def _clone(self, identifier=None, with_tree=False, deep=False):
        >>>         return TreeWithComposition(
        >>>             identifier=identifier,
        >>>             deep=deep,
        >>>             tree=self if with_tree else None,
        >>>             tree_description=self.tree_description
        >>>         )
        >>> my_custom_tree = TreeWithComposition(tree_description="smart tree")
        >>> subtree = my_custom_tree.subtree()
        >>> subtree.tree_description
        "smart tree"
        """
        return self.__class__(identifier=identifier, tree=self if with_tree else None, deep=deep)

    @property
    def identifier(self):
        return self._identifier

    def _set_identifier(self, nid):
        """Initialize self._set_identifier"""
        if nid is None:
            self._identifier = str(uuid.uuid1())
        else:
            self._identifier = nid

    def __getitem__(self, key):
        """Return _nodes[key]"""
        try:
            return self._nodes[key]
        except KeyError:
            raise NodeIDAbsentError("Node '%s' is not in the tree" % key)

    def __len__(self):
        """Return len(_nodes)"""
        return len(self._nodes)

    def __setitem__(self, key, item):
        """Set _nodes[key]"""
        self._nodes.update({key: item})

    def __str__(self):
        self._reader = ""

        def write(line):
            self._reader += line.decode('utf-8') + "\n"

        self.__print_backend(func=write)
        return self._reader

    def __print_backend(self, nid=None, level=ROOT, idhidden=True, filter=None,
                        key=None, reverse=False, line_type='ascii-ex',
                        data_property=None, func=print):
        """
        Another implementation of printing tree using Stack
        Print tree structure in hierarchy style.

        For example:

        .. code-block:: bash

            Root
            |___ C01
            |    |___ C11
            |         |___ C111
            |         |___ C112
            |___ C02
            |___ C03
            |    |___ C31

        A more elegant way to achieve this function using Stack
        structure, for constructing the Nodes Stack push and pop nodes
        with additional level info.

        UPDATE: the @key @reverse is present to sort node at each
        level.
        """
        # Factory for proper get_label() function
        if data_property:
            if idhidden:
                def get_label(node):
                    return getattr(node.data, data_property)
            else:
                def get_label(node):
                    return "%s[%s]" % (getattr(node.data, data_property), node.identifier)
        else:
            if idhidden:
                def get_label(node):
                    return node.tag
            else:
                def get_label(node):
                    return "%s[%s]" % (node.tag, node.identifier)

        # legacy ordering
        if key is None:
            def key(node):
                return node

        # iter with func
        for pre, node in self.__get(nid, level, filter, key, reverse,
                                    line_type):
            label = get_label(node)
            func('{0}{1}'.format(pre, label).encode('utf-8'))

    def __get(self, nid, level, filter_, key, reverse, line_type):
        # default filter
        if filter_ is None:
            def filter_(node):
                return True

        # render characters
        dt = {
            'ascii': ('|', '|-- ', '+-- '),
            'ascii-ex': ('\u2502', '\u251c\u2500\u2500 ', '\u2514\u2500\u2500 '),
            'ascii-exr': ('\u2502', '\u251c\u2500\u2500 ', '\u2570\u2500\u2500 '),
            'ascii-em': ('\u2551', '\u2560\u2550\u2550 ', '\u255a\u2550\u2550 '),
            'ascii-emv': ('\u2551', '\u255f\u2500\u2500 ', '\u2559\u2500\u2500 '),
            'ascii-emh': ('\u2502', '\u255e\u2550\u2550 ', '\u2558\u2550\u2550 '),
        }[line_type]

        return self.__get_iter(nid, level, filter_, key, reverse, dt, [])

    def __get_iter(self, nid, level, filter_, key, reverse, dt, is_last):
        dt_vline, dt_line_box, dt_line_cor = dt

        nid = self.root if (nid is None) else nid
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        node = self[nid]

        if level == self.ROOT:
            yield "", node
        else:
            leading = ''.join(map(lambda x: dt_vline + ' ' * 3
            if not x else ' ' * 4, is_last[0:-1]))
            lasting = dt_line_cor if is_last[-1] else dt_line_box
            yield leading + lasting, node

        if filter_(node) and node.expanded:
            children = [self[i] for i in node.successors(self._identifier) if filter_(self[i])]
            idxlast = len(children) - 1
            if key:
                children.sort(key=key, reverse=reverse)
            elif reverse:
                children = reversed(children)
            level += 1
            for idx, child in enumerate(children):
                is_last.append(idx == idxlast)
                for item in self.__get_iter(child.identifier, level, filter_,
                                            key, reverse, dt, is_last):
                    yield item
                is_last.pop()

    def __update_bpointer(self, nid, parent_id):
        """set self[nid].bpointer"""
        self[nid].set_predecessor(parent_id, self._identifier)

    def __update_fpointer(self, nid, child_id, mode):
        if nid is None:
            return
        else:
            self[nid].update_successors(child_id, mode, tree_id=self._identifier)

    def add_node(self, node, parent=None):
        """
        Add a new node object to the tree and make the parent as the root by default.

        The 'node' parameter refers to an instance of Class::Node.
        """
        if not isinstance(node, self.node_class):
            raise OSError(
                "First parameter must be object of {}".format(self.node_class))

        if node.identifier in self._nodes:
            raise DuplicatedNodeIdError("Can't create node "
                                        "with ID '%s'" % node.identifier)

        pid = parent.identifier if isinstance(
            parent, self.node_class) else parent

        if pid is None:
            if self.root is not None:
                raise MultipleRootError("A tree takes one root merely.")
            else:
                self.root = node.identifier
        elif not self.contains(pid):
            raise NodeIDAbsentError("Parent node '%s' "
                                    "is not in the tree" % pid)

        self._nodes.update({node.identifier: node})
        self.__update_fpointer(pid, node.identifier, self.node_class.ADD)
        self.__update_bpointer(node.identifier, pid)
        node.set_initial_tree_id(self._identifier)

    def all_nodes(self):
        """Return all nodes in a list"""
        return list(self._nodes.values())

    def all_nodes_itr(self):
        """
        Returns all nodes in an iterator.
        Added by William Rusnack
        """
        return self._nodes.values()

    def ancestor(self, nid, level=None):
        """
        For a given id, get ancestor node object at a given level.
        If no level is provided, the parent node is returned.
        """
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        descendant = self[nid]
        ascendant = self[nid].bpointer
        ascendant_level = self.level(ascendant)

        if level is None:
            return ascendant
        elif nid == self.root:
            return self[nid]
        elif level >= self.level(descendant.identifier):
            raise InvalidLevelNumber("Descendant level (level %s) must be greater \
                                      than its ancestor's level (level %s)" % (str(self.level(descendant.identifier)), level))

        while ascendant is not None:
            if ascendant_level == level:
                return self[ascendant]
            else:
                descendant = ascendant
                ascendant = self[descendant].bpointer
                ascendant_level = self.level(ascendant)
        return None

    def children(self, nid):
        """
        Return the children (Node) list of nid.
        Empty list is returned if nid does not exist
        """
        return [self[i] for i in self.is_branch(nid)]

    def contains(self, nid):
        """Check if the tree contains node of given id"""
        return True if nid in self._nodes else False

    def create_node(self, tag=None, identifier=None, parent=None, data=None):
        """
        Create a child node for given @parent node. If ``identifier`` is absent,
        a UUID will be generated automatically.
        """
        node = self.node_class(tag=tag, identifier=identifier, data=data)
        self.add_node(node, parent)
        return node

    def depth(self, node=None):
        """
        Get the maximum level of this tree or the level of the given node.

        @param node Node instance or identifier
        @return int
        @throw NodeIDAbsentError
        """
        ret = 0
        if node is None:
            # Get maximum level of this tree
            leaves = self.leaves()
            for leave in leaves:
                level = self.level(leave.identifier)
                ret = level if level >= ret else ret
        else:
            # Get level of the given node
            if not isinstance(node, self.node_class):
                nid = node
            else:
                nid = node.identifier
            if not self.contains(nid):
                raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)
            ret = self.level(nid)
        return ret

    def expand_tree(self, nid=None, mode=DEPTH, filter=None, key=None,
                    reverse=False, sorting=True):
        """
        Python generator to traverse the tree (or a subtree) with optional
        node filtering and sorting.

        Loosely based on an algorithm from 'Essential LISP' by John R. Anderson,
        Albert T. Corbett, and Brian J. Reiser, page 239-241.

        :param nid: Node identifier from which tree traversal will start.
            If None tree root will be used
        :param mode: Traversal mode, may be either DEPTH, WIDTH or ZIGZAG
        :param filter: the @filter function is performed on Node object during
            traversing. In this manner, the traversing will NOT visit the node
            whose condition does not pass the filter and its children.
        :param key: the @key and @reverse are present to sort nodes at each
            level. If @key is None sorting is performed on node tag.
        :param reverse: if True reverse sorting
        :param sorting: if True perform node sorting, if False return
            nodes in original insertion order. In latter case @key and
            @reverse parameters are ignored.
        :return: Node IDs that satisfy the conditions
        :rtype: generator object
        """
        nid = self.root if nid is None else nid
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        filter = (lambda x: True) if (filter is None) else filter
        if filter(self[nid]):
            yield nid
            queue = [self[i] for i in self[nid].successors(self._identifier) if filter(self[i])]
            if mode in [self.DEPTH, self.WIDTH]:
                if sorting:
                    queue.sort(key=key, reverse=reverse)
                while queue:
                    yield queue[0].identifier
                    expansion = [self[i] for i in queue[0].successors(self._identifier)
                                 if filter(self[i])]
                    if sorting:
                        expansion.sort(key=key, reverse=reverse)
                    if mode is self.DEPTH:
                        queue = expansion + queue[1:]  # depth-first
                    elif mode is self.WIDTH:
                        queue = queue[1:] + expansion  # width-first

            elif mode is self.ZIGZAG:
                # Suggested by Ilya Kuprik (ilya-spy@ynadex.ru).
                stack_fw = []
                queue.reverse()
                stack = stack_bw = queue
                direction = False
                while stack:
                    expansion = [self[i] for i in stack[0].successors(self._identifier)
                                 if filter(self[i])]
                    yield stack.pop(0).identifier
                    if direction:
                        expansion.reverse()
                        stack_bw = expansion + stack_bw
                    else:
                        stack_fw = expansion + stack_fw
                    if not stack:
                        direction = not direction
                        stack = stack_fw if direction else stack_bw

            else:
                raise ValueError(
                    "Traversal mode '{}' is not supported".format(mode))

    def filter_nodes(self, func):
        """
        Filters all nodes by function.

        :param func: is passed one node as an argument and that node is included if function returns true,
        :return: a filter iterator of the node in python 3 or a list of the nodes in python 2.

        Added by William Rusnack.
        """
        return filter(func, self.all_nodes_itr())

    def get_node(self, nid):
        """
        Get the object of the node with ID of ``nid``.

        An alternative way is using '[]' operation on the tree. But small difference exists between them:
        ``get_node()`` will return None if ``nid`` is absent, whereas '[]' will raise ``KeyError``.
        """
        if nid is None or not self.contains(nid):
            return None
        return self._nodes[nid]

    def is_branch(self, nid):
        """
        Return the children (ID) list of nid.
        Empty list is returned if nid does not exist
        """
        if nid is None:
            raise OSError("First parameter can't be None")
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        try:
            fpointer = self[nid].successors(self._identifier)
        except KeyError:
            fpointer = []
        return fpointer

    def leaves(self, nid=None):
        """Get leaves of the whole tree or a subtree."""
        leaves = []
        if nid is None:
            for node in self._nodes.values():
                if node.is_leaf(self._identifier):
                    leaves.append(node)
        else:
            for node in self.expand_tree(nid):
                if self[node].is_leaf(self._identifier):
                    leaves.append(self[node])
        return leaves

    def level(self, nid, filter=None):
        """
        Get the node level in this tree.
        The level is an integer starting with '0' at the root.
        In other words, the root lives at level '0';

        Update: @filter params is added to calculate level passing
        exclusive nodes.
        """
        return len([n for n in self.rsearch(nid, filter)]) - 1

    def link_past_node(self, nid):
        """
        Delete a node by linking past it.

        For example, if we have `a -> b -> c` and delete node b, we are left
        with `a -> c`.
        """
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)
        if self.root == nid:
            raise LinkPastRootNodeError("Cannot link past the root node, "
                                        "delete it with remove_node()")
        # Get the parent of the node we are linking past
        parent = self[self[nid].predecessor(self._identifier)]
        # Set the children of the node to the parent
        for child in self[nid].successors(self._identifier):
            self[child].set_predecessor(parent.identifier, self._identifier)
        # Link the children to the parent
        for id_ in self[nid].successors(self._identifier) or []:
            parent.update_successors(id_, tree_id=self._identifier)
        # Delete the node
        parent.update_successors(nid, mode=parent.DELETE, tree_id=self._identifier)
        del self._nodes[nid]

    def move_node(self, source, destination):
        """
        Move node @source from its parent to another parent @destination.
        """
        if not self.contains(source) or not self.contains(destination):
            raise NodeIDAbsentError
        elif self.is_ancestor(source, destination):
            raise LoopError

        parent = self[source].predecessor(self._identifier)
        self.__update_fpointer(parent, source, self.node_class.DELETE)
        self.__update_fpointer(destination, source, self.node_class.ADD)
        self.__update_bpointer(source, destination)

    def is_ancestor(self, ancestor, grandchild):
        """
        Check if the @ancestor the preceding nodes of @grandchild.

        :param ancestor: the node identifier
        :param grandchild: the node identifier
        :return: True or False
        """
        parent = self[grandchild].predecessor(self._identifier)
        child = grandchild
        while parent is not None:
            if parent == ancestor:
                return True
            else:
                child = self[child].predecessor(self._identifier)
                parent = self[child].predecessor(self._identifier)
        return False

    @property
    def nodes(self):
        """Return a dict form of nodes in a tree: {id: node_instance}."""
        return self._nodes

    def parent(self, nid):
        """Get parent :class:`Node` object of given id."""
        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        pid = self[nid].predecessor(self._identifier)
        if pid is None or not self.contains(pid):
            return None

        return self[pid]

    def merge(self, nid, new_tree, deep=False):
        """Patch @new_tree on current tree by pasting new_tree root children on current tree @nid node.

        Consider the following tree:
        >>> current.show()
        root
        ├── A
        └── B
        >>> new_tree.show()
        root2
        ├── C
        └── D
            └── D1
        Merging new_tree on B node:
        >>>current.merge('B', new_tree)
        >>>current.show()
        root
        ├── A
        └── B
            ├── C
            └── D
                └── D1

        Note: if current tree is empty and nid is None, the new_tree root will be used as root on current tree. In all
        other cases new_tree root is not pasted.
        """
        if new_tree.root is None:
            return

        if nid is None:
            if self.root is None:
                new_tree_root = new_tree[new_tree.root]
                self.add_node(new_tree_root)
                nid = new_tree.root
            else:
                raise ValueError('Must define "nid" under which new tree is merged.')
        for child in new_tree.children(new_tree.root):
            self.paste(nid=nid, new_tree=new_tree.subtree(child.identifier), deep=deep)

    def paste(self, nid, new_tree, deep=False):
        """
        Paste a @new_tree to the original one by linking the root
        of new tree to given node (nid).

        Update: add @deep copy of pasted tree.
        """
        assert isinstance(new_tree, Tree)

        if new_tree.root is None:
            return

        if nid is None:
            raise ValueError('Must define "nid" under which new tree is pasted.')

        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        set_joint = set(new_tree._nodes) & set(self._nodes)  # joint keys
        if set_joint:
            raise ValueError('Duplicated nodes %s exists.' % list(map(text, set_joint)))

        for cid, node in new_tree.nodes.items():
            if deep:
                node = deepcopy(new_tree[node])
            self._nodes.update({cid: node})
            node.clone_pointers(new_tree.identifier, self._identifier)

        self.__update_bpointer(new_tree.root, nid)
        self.__update_fpointer(nid, new_tree.root, self.node_class.ADD)

    def paths_to_leaves(self):
        """
        Use this function to get the identifiers allowing to go from the root
        nodes to each leaf.

        :return: a list of list of identifiers, root being not omitted.

        For example:

        .. code-block:: python

            Harry
            |___ Bill
            |___ Jane
            |    |___ Diane
            |         |___ George
            |              |___ Jill
            |         |___ Mary
            |    |___ Mark

        Expected result:

        .. code-block:: python

            [['harry', 'jane', 'diane', 'mary'],
             ['harry', 'jane', 'mark'],
             ['harry', 'jane', 'diane', 'george', 'jill'],
             ['harry', 'bill']]

        """
        res = []

        for leaf in self.leaves():
            res.append([nid for nid in self.rsearch(leaf.identifier)][::-1])

        return res

    def remove_node(self, identifier):
        """Remove a node indicated by 'identifier' with all its successors.
        Return the number of removed nodes.
        """
        if not self.contains(identifier):
            raise NodeIDAbsentError("Node '%s' "
                                    "is not in the tree" % identifier)

        parent = self[identifier].predecessor(self._identifier)

        # Remove node and its children
        removed = list(self.expand_tree(identifier))

        for id_ in removed:
            if id_ == self.root:
                self.root = None
            self.__update_bpointer(id_, None)
            for cid in self[id_].successors(self._identifier) or []:
                self.__update_fpointer(id_, cid, self.node_class.DELETE)

        # Update parent info
        self.__update_fpointer(parent, identifier, self.node_class.DELETE)
        self.__update_bpointer(identifier, None)

        for id_ in removed:
            self.nodes.pop(id_)
        return len(removed)

    def remove_subtree(self, nid, identifier=None):
        """
        Get a subtree with ``nid`` being the root. If nid is None, an
        empty tree is returned.

        For the original tree, this method is similar to
        `remove_node(self,nid)`, because given node and its children
        are removed from the original tree in both methods.
        For the returned value and performance, these two methods are
        different:

            * `remove_node` returns the number of deleted nodes;
            * `remove_subtree` returns a subtree of deleted nodes;

        You are always suggested to use `remove_node` if your only to
        delete nodes from a tree, as the other one need memory
        allocation to store the new tree.

        :return: a :class:`Tree` object.
        """
        st = self._clone(identifier)
        if nid is None:
            return st

        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)
        st.root = nid

        # in original tree, the removed nid will be unreferenced from its parents children
        parent = self[nid].predecessor(self._identifier)

        removed = list(self.expand_tree(nid))
        for id_ in removed:
            if id_ == self.root:
                self.root = None
            st._nodes.update({id_: self._nodes.pop(id_)})
            st[id_].clone_pointers(self._identifier, st.identifier)
            st[id_].reset_pointers(self._identifier)
            if id_ == nid:
                st[id_].set_predecessor(None, st.identifier)
        self.__update_fpointer(parent, nid, self.node_class.DELETE)
        return st

    def rsearch(self, nid, filter=None):
        """
        Traverse the tree branch along the branch from nid to its
        ancestors (until root).

        :param filter: the function of one variable to act on the :class:`Node` object.
        """
        if nid is None:
            return

        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        filter = (lambda x: True) if (filter is None) else filter

        current = nid
        while current is not None:
            if filter(self[current]):
                yield current
            # subtree() hasn't update the bpointer
            current = self[current].predecessor(self._identifier) if self.root != current else None

    def save2file(self, filename, nid=None, level=ROOT, idhidden=True,
                  filter=None, key=None, reverse=False, line_type='ascii-ex', data_property=None):
        """
        Save the tree into file for offline analysis.
        """

        def _write_line(line, f):
            f.write(line + b'\n')

        handler = lambda x: _write_line(x, open(filename, 'ab'))

        self.__print_backend(nid, level, idhidden, filter,
                             key, reverse, line_type, data_property, func=handler)

    def show(self, nid=None, level=ROOT, idhidden=True, filter=None,
             key=None, reverse=False, line_type='ascii-ex', data_property=None, stdout=True):
        """
        Print the tree structure in hierarchy style.

        You have three ways to output your tree data, i.e., stdout with ``show()``,
        plain text file with ``save2file()``, and json string with ``to_json()``. The
        former two use the same backend to generate a string of tree structure in a
        text graph.

        * Version >= 1.2.7a*: you can also specify the ``line_type`` parameter, such as 'ascii' (default), 'ascii-ex', 'ascii-exr', 'ascii-em', 'ascii-emv', 'ascii-emh') to the change graphical form.

        :param nid: the reference node to start expanding.
        :param level: the node level in the tree (root as level 0).
        :param idhidden: whether hiding the node ID when printing.
        :param filter: the function of one variable to act on the :class:`Node` object.
            When this parameter is specified, the traversing will not continue to following
            children of node whose condition does not pass the filter.
        :param key: the ``key`` param for sorting :class:`Node` objects in the same level.
        :param reverse: the ``reverse`` param for sorting :class:`Node` objects in the same level.
        :param line_type:
        :param data_property: the property on the node data object to be printed.
        :return: None
        """
        self._reader = ""

        def write(line):
            self._reader += line.decode('utf-8') + "\n"

        try:
            self.__print_backend(nid, level, idhidden, filter,
                                 key, reverse, line_type, data_property, func=write)
        except NodeIDAbsentError:
            print('Tree is empty')

        if stdout:
            print(self._reader)
        else:
            return self._reader

    def siblings(self, nid):
        """
        Return the siblings of given @nid.

        If @nid is root or there are no siblings, an empty list is returned.
        """
        siblings = []

        if nid != self.root:
            pid = self[nid].predecessor(self._identifier)
            siblings = [self[i] for i in self[pid].successors(self._identifier) if i != nid]

        return siblings

    def size(self, level=None):
        """
        Get the number of nodes of the whole tree if @level is not
        given. Otherwise, the total number of nodes at specific level
        is returned.

        @param level The level number in the tree. It must be between
        [0, tree.depth].

        Otherwise, InvalidLevelNumber exception will be raised.
        """
        if level is None:
            return len(self._nodes)
        else:
            try:
                level = int(level)
                return len([node for node in self.all_nodes_itr() if self.level(node.identifier) == level])
            except:
                raise TypeError(
                    "level should be an integer instead of '%s'" % type(level))

    def subtree(self, nid, identifier=None):
        """
        Return a shallow COPY of subtree with nid being the new root.
        If nid is None, return an empty tree.
        If you are looking for a deepcopy, please create a new tree
        with this shallow copy, e.g.,

        .. code-block:: python

            new_tree = Tree(t.subtree(t.root), deep=True)

        This line creates a deep copy of the entire tree.
        """
        st = self._clone(identifier)
        if nid is None:
            return st

        if not self.contains(nid):
            raise NodeIDAbsentError("Node '%s' is not in the tree" % nid)

        st.root = nid
        for node_n in self.expand_tree(nid):
            st._nodes.update({self[node_n].identifier: self[node_n]})
            # define nodes parent/children in this tree
            # all pointers are the same as copied tree, except the root
            st[node_n].clone_pointers(self._identifier, st.identifier)
            if node_n == nid:
                # reset root parent for the new tree
                st[node_n].set_predecessor(None, st.identifier)
        return st

    def update_node(self, nid, **attrs):
        """
        Update node's attributes.

        :param nid: the identifier of modified node
        :param attrs: attribute pairs recognized by Node object
        :return: None
        """
        cn = self[nid]
        for attr, val in attrs.items():
            if attr == 'identifier':
                # Updating node id meets following contraints:
                # * Update node identifier property
                # * Update parent's followers
                # * Update children's parents
                # * Update tree registration of var _nodes
                # * Update tree root if necessary
                cn = self._nodes.pop(nid)
                setattr(cn, 'identifier', val)
                self._nodes[val] = cn

                if cn.predecessor(self._identifier) is not None:
                    self[cn.predecessor(self._identifier)].update_successors(
                        nid, mode=self.node_class.REPLACE, replace=val,
                        tree_id=self._identifier
                    )

                for fp in cn.successors(self._identifier):
                    self[fp].set_predecessor(val, self._identifier)

                if self.root == nid:
                    self.root = val
            else:
                setattr(cn, attr, val)

    def to_dict(self, nid=None, key=None, sort=True, reverse=False, with_data=False):
        """Transform the whole tree into a dict."""

        nid = self.root if (nid is None) else nid
        ntag = self[nid].tag
        tree_dict = {ntag: {"children": []}}
        if with_data:
            tree_dict[ntag]["data"] = self[nid].data

        if self[nid].expanded:
            queue = [self[i] for i in self[nid].successors(self._identifier)]
            key = (lambda x: x) if (key is None) else key
            if sort:
                queue.sort(key=key, reverse=reverse)

            for elem in queue:
                tree_dict[ntag]["children"].append(
                    self.to_dict(elem.identifier, with_data=with_data, sort=sort, reverse=reverse))
            if len(tree_dict[ntag]["children"]) == 0:
                tree_dict = self[nid].tag if not with_data else \
                    {ntag: {"data": self[nid].data}}
            return tree_dict

    def to_json(self, with_data=False, sort=True, reverse=False):
        """To format the tree in JSON format."""
        return json.dumps(self.to_dict(with_data=with_data, sort=sort, reverse=reverse))

    def to_graphviz(self, filename=None, shape='circle', graph='digraph'):
        """Exports the tree in the dot format of the graphviz software"""
        nodes, connections = [], []
        if self.nodes:

            for n in self.expand_tree(mode=self.WIDTH):
                nid = self[n].identifier
                state = '"{0}" [label="{1}", shape={2}]'.format(
                    nid, self[n].tag, shape)
                nodes.append(state)

                for c in self.children(nid):
                    cid = c.identifier
                    connections.append('"{0}" -> "{1}"'.format(nid, cid))

        # write nodes and connections to dot format
        is_plain_file = filename is not None
        if is_plain_file:
            f = codecs.open(filename, 'w', 'utf-8')
        else:
            f = StringIO()

        f.write(graph + ' tree {\n')
        for n in nodes:
            f.write('\t' + n + '\n')

        if len(connections) > 0:
            f.write('\n')

        for c in connections:
            f.write('\t' + c + '\n')

        f.write('}')

        if not is_plain_file:
            print(f.getvalue())

        f.close()
