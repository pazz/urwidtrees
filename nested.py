# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.
from tree import Tree
import logging
from decoration import DecoratedTree


class NestedTree(Tree):
    """
    A Tree that wraps around Trees that may contain list walkers or other trees.
    The wrapped tree may contain normal widgets as well. List walkers / subtree
    contents will be expanded into the tree presented by this wrapper.

    This wrapper's positions are tuples of positions of the original and subtrees:
    For example, `(X,Y,Z)` points at position Z in tree/list at position Y in
    tree/list at position X in the original tree.

    NestedTree transparently behaves like a collapsible DecoratedTree.
    """
    @property
    def root(self):
        return (self._tree.root,)

    def __init__(self, tree):
        self._tree = tree

    def _depth(self, tree, pos, outmost_only=True):
        depth = self._tree.depth(pos[1:])
        if not outmost_only:
            entry = self._tree[pos[0]]
            if isinstance(entry, Tree) and len(pos) > 1:
                depth += self._depth(entry, pos[1:], outmost_only=False)
        return depth

    def depth(self, pos, outmost=True):
        return self._depth(self._tree, pos)

    def __getitem__(self, pos):
        return self._lookup_entry(self._tree, pos)

    # DecoratedTree API
    def _get_decorated_entry(self, tree, pos, widget=None, is_first=True):
        entry = tree[pos[0]]
        if len(pos) > 1:
            subtree = entry
            entry = self._get_decorated_entry(
                subtree, pos[1:], widget, is_first)
        else:
            entry = widget or entry
        if isinstance(tree, (DecoratedTree, NestedTree)):  # has decorate-API
            isf = len(pos) < 2
            if not isf:
                isf = (tree[pos[0]].parent_position(pos[1])
                       is None) or not is_first
            entry = tree.decorate(pos[0], entry, is_first=isf)
        return entry

    def get_decorated(self, pos):
        return self._get_decorated_entry(self._tree, pos)

    def decorate(self, pos, widget, is_first=True):
        return self._get_decorated_entry(self._tree, pos, widget, is_first)

    # Collapse API
    # TODO
    def _lookup_entry(self, tree, pos):
        if len(pos) == 0:
            entry = tree[tree.root]
        else:
            entry = tree[pos[0]]
            if len(pos) > 1:
                subtree = entry
                entry = self._lookup_entry(subtree, pos[1:])
                #entry = subtree[subtree.root]
        #if isinstance(entry, Tree):
        #    entry = entry[entry.root]
        return entry

    def is_leaf(self, pos, outmost_only=False):
        return self.first_child_position(pos, outmost_only) is None

    def get_owner(self, pos):
        """returns Tree that manages pos[-1]"""
        return self._lookup_entry(pos[:-1])

    def parent_position(self, pos):
        candidate_pos = None
        if len(pos) > 1:
            subtree_pos = pos[:-1]
            least_pos = pos[-1]
            subtree = self._lookup_entry(self._tree, subtree_pos)
            subparent_pos = subtree.parent_position(least_pos)
            if subparent_pos is not None:
                candidate_pos = subtree_pos + (subparent_pos,)
            else:
                candidate_pos = self.parent_position(subtree_pos)
        else:
            outer_parent = self._tree.parent_position(pos[0])
            if outer_parent is not None:
                candidate_pos = outer_parent,
        return candidate_pos

    def first_child_position(self, pos, outmost_only=False):
        return self._first_child_position(self._tree, pos, outmost_only)

    def _first_child_position(self, tree, pos, outmost_only=False):
        #logging.debug('FIRST CHILD %s %s' % (str(tree), str(pos)))
        childpos = None
        if len(pos) == 0:
            pos = (tree.root,)
        entry = tree[pos[0]]
        if isinstance(entry, Tree) and not outmost_only:
            subchild = self._first_child_position(entry, pos[1:])
            if subchild is not None:
                childpos = (pos[0],) + subchild
        else:
            #logging.debug('FIRST CHILD %s %s' % (str(tree), str(pos)))
            child = tree.first_child_position(pos[0])
            #logging.debug('FIRST CHILD %s' % (str(child)))
            if child is not None:
                entry = tree[child]
                #logging.debug('entry %s' % (str(entry)))
                if isinstance(entry, Tree):
                    childpos = (child,) + (entry.root,)
                else:
                    childpos = child,
        return childpos

    def last_child_position(self, pos, outmost_only=False):
        return self._last_child_position(self._tree, pos, outmost_only)

    def _last_child_position(self, tree, pos, outmost_only=False):
        childpos = None
        if len(pos) == 0:
            pos = (tree.root,)
        entry = tree[pos[0]]
        if isinstance(entry, Tree) and not outmost_only:
            subchild = self._last_child_position(entry, pos[1:])
            if subchild is not None:
                childpos = (pos[0],) + subchild
        else:
            subchild = tree.last_child_position(pos[0])
            if subchild is not None:
                childpos = subchild,
        return childpos

    def _next_sibling_position(self, tree, pos):
        #logging.debug("next sub in %s for %s" % (tree,str(pos)))
        candidate = None
        if len(pos) > 1:
            subtree = tree[pos[0]]
            #logging.debug("subtree is %s" % subtree)
            subsibling_pos = self._next_sibling_position(subtree, pos[1:])
            #logging.debug("subsibling at %s in %s is %s" % (str(pos[1:]), subtree, subsibling_pos))
            if subsibling_pos is not None:
                candidate = pos[:1] + subsibling_pos
            elif subtree.parent_position(pos[1]) is None:
                #logging.debug("get next sib at %s is %s" % (str(pos[0]), tree))
                # go to outer tree sibline if inner pos has depth 0
                next_sib = tree.next_sibling_position(pos[0])
                #logging.debug("next sibling at %s is %s" % (str(pos[0]), str(next_sib)))
                if next_sib is not None:
                    candidate = next_sib,
        else:
            next_sib = tree.next_sibling_position(pos[0])
            #logging.debug("next outer sib is %s" % (str(next_sib)))
            if next_sib is not None:
                candidate = next_sib,
        if candidate is not None:
            entry = self._lookup_entry(tree, candidate)
            if isinstance(entry, Tree):
                #logging.debug('ENTRY IS TREE! %s' % str(candidate))
                candidate = candidate + (entry.root,)
        return candidate

    def next_sibling_position(self, pos):
        return self._next_sibling_position(self._tree, pos)

    def _prev_sibling_position(self, tree, pos):
        #candidate = tree.prev_sibling_position(pos[0])
        candidate = None
        if len(pos) > 1:
            subtree = self._tree[pos[0]]
            subsibling_pos = self._prev_sibling_position(subtree, pos[1:])
            if subsibling_pos is not None:
                candidate = pos[:1] + subsibling_pos
            elif subtree.parent_position(pos[1]) is None:
                prev_sib = tree.prev_sibling_position(pos[0])
                if prev_sib is not None:
                    candidate = prev_sib,
        else:
            prev_sib = tree.prev_sibling_position(pos[0])
            if prev_sib is not None:
                candidate = prev_sib,
        if candidate is not None:
            entry = self._lookup_entry(tree, candidate)
            if isinstance(entry, Tree):
                #logging.debug('ENTRY IS TREE! %s' % str(candidate))
                candidate = candidate + (entry.root,)
        return candidate

    def prev_sibling_position(self, pos):
        return self._prev_sibling_position(self._tree, pos)
