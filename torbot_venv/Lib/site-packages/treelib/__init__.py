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
treelib - Python 2/3 Tree Implementation

`treelib` is a Python module with two primary classes: Node and Tree.
Tree is a self-contained structure with some nodes and connected by branches.
A tree owns merely a root, while a node (except root) has some children and one parent.

Note: To solve string compatibility between Python 2.x and 3.x, treelib follows
the way of porting Python 3.x to 2/3. That means, all strings are manipulated as
unicode and you do not need u'' prefix anymore. The impacted functions include `str()`,
`show()` and `save2file()` routines.
But if your data contains non-ascii characters and Python 2.x is used,
you have to trigger the compatibility by declaring `unicode_literals` in the code:

.. code-block:: python

   >>> from __future__ import unicode_literals
"""
__version__ = '1.6.1'

from .tree import Tree
from .node import Node
