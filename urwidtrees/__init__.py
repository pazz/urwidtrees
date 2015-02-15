__productname__ = 'urwidtrees'
__version__ = '1.0'
__copyright__ = "Copyright (C) 2015 Patrick Totzke"
__author__ = "Patrick Totzke"
__author_email__ = "patricktotzke@gmail.com"
__description__ = "Tree widgets for urwid"
__url__ = "https://github.com/pazz/urwidtrees"
__license__ = "Licensed under the GNU GPL v3+."

from .tree import Tree, SimpleTree
from .decoration import DecoratedTree, CollapsibleTree
from .decoration import IndentedTree, CollapsibleIndentedTree
from .decoration import ArrowTree, CollapsibleArrowTree
from .nested import NestedTree
from .widgets import TreeBox
