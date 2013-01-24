try:
    import functools.lru_cache as lru_cache
except:
    import lru_cache as lru_cache

from tree import Tree, SimpleTree
from decoration import DecoratedTree, CollapsibleTree, IndentedTree, CollapsibleIndentedTree, ArrowTree, CollapsibleArrowTree
from nested import NestedTree
from widgets import TreeBox
