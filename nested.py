# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.
from tree import Tree
import logging
from decoration import DecoratedTree, CollapseMixin


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
        root = (self._tree.root,)
        rcontent = self._tree[self._tree.root]
        if isinstance(rcontent, Tree):
            root = root + (rcontent.root,)
        return root

    def __init__(self, tree):
        self._tree = tree

    def _lookup_entry(self, tree, pos):
        if len(pos) == 0:
            entry = tree[tree.root]
        else:
            entry = tree[pos[0]]
            if len(pos) > 1 and isinstance(entry, Tree):
                subtree = entry
                entry = self._lookup_entry(subtree, pos[1:])
        return entry

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
        #logging.debug('DECORATED: %s %s %s' % (tree,str(pos), widget))
        entry = tree[pos[0]]
        if len(pos) > 1 and isinstance(entry, Tree):
            subtree = entry
            entry = self._get_decorated_entry(
                subtree, pos[1:], widget, is_first)
        else:
            entry = widget or entry
        if isinstance(tree, (DecoratedTree, NestedTree)):  # has decorate-API
            isf = len(pos) < 2
            if not isf and isinstance(tree[pos[0]],Tree):
                isf = (tree[pos[0]].parent_position(pos[1])
                       is None) or not is_first
            entry = tree.decorate(pos[0], entry, is_first=isf)
        return entry

    def get_decorated(self, pos):
        return self._get_decorated_entry(self._tree, pos)

    def decorate(self, pos, widget, is_first=True):
        return self._get_decorated_entry(self._tree, pos, widget, is_first)

    # Collapse API
    def _get_subtree_for(self, pos):
        """returns Tree that manages pos[-1]"""
        res = self._tree
        candidate = self._lookup_entry(self._tree, pos[:-1])
        if isinstance(candidate, Tree):
            res = candidate
        return res

    def collapsible(self, pos):
        res = False
        subtree = self._get_subtree_for(pos)
        if isinstance(subtree, (CollapseMixin, NestedTree)):
            res = subtree.collapsible(pos[-1])
        return res

    def is_collapsed(self, pos):
        res = False
        subtree = self._get_subtree_for(pos)
        if isinstance(subtree, (CollapseMixin, NestedTree)):
            res = subtree.is_collapsed(pos[-1])
        return res

    def toggle_collapsed(self, pos):
        subtree = self._get_subtree_for(pos)
        if isinstance(subtree, (CollapseMixin, NestedTree)):
            subtree.toggle_collapsed(pos)

    def collapse(self, pos):
        subtree = self._get_subtree_for(pos)
        if isinstance(subtree, (CollapseMixin, NestedTree)):
            subtree.collapse(pos[-1])

    def collapse_all(self):
        self._collapse_all(self._tree, self.root)

    def _collapse_all(self, tree, pos=None):
        if pos is not None:
            if isinstance(tree, (CollapseMixin, NestedTree)):
                tree.expand_all()

            if len(pos) > 1:
                self._collapse_all(tree[pos[0]], pos[1:])
            nextpos = tree.next_position(pos[0])
            if nextpos is not None:
                nentry = tree[nextpos]
                if isinstance(nentry, Tree):
                    self._collapse_all(nentry, (nentry.root,))
                self._collapse_all(tree, (nextpos,))
            if isinstance(tree, (CollapseMixin, NestedTree)):
                tree.collapse_all()

    def expand(self, pos):
        subtree = self._get_subtree_for(pos)
        if isinstance(subtree, (CollapseMixin, NestedTree)):
            subtree.expand(pos[-1])

    def expand_all(self):
        self._expand_all(self._tree, self.root)

    def _expand_all(self, tree, pos=None):
        if pos is not None:
            if isinstance(tree, (CollapseMixin, NestedTree)):
                tree.expand_all()
            if len(pos) > 1:
                self._expand_all(tree[pos[0]], pos[1:])
            nextpos = tree.next_position(pos[0])
            if nextpos is not None:
                nentry = tree[nextpos]
                if isinstance(nentry, Tree):
                    self._expand_all(nentry, (nentry.root,))
                self._expand_all(tree, (nextpos,))
            if isinstance(tree, (CollapseMixin, NestedTree)):
                tree.expand_all()

    def is_leaf(self, pos, outmost_only=False):
        return self.first_child_position(pos, outmost_only) is None

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
                entry = self._tree[outer_parent]
                if isinstance(entry, Tree):
                    candidate_pos = candidate_pos + (entry.root,)
        return candidate_pos

    def first_child_position(self, pos, outmost_only=False):
        return self._first_child_position(self._tree, pos, outmost_only)

    def _first_child_position(self, tree, pos, outmost_only=False):
        childpos = None
        entry = tree[pos[0]]
        if isinstance(entry, Tree) and not outmost_only:
            subchild = self._first_child_position(entry, pos[1:])
            if subchild is not None:
                childpos = (pos[0],) + subchild
                return childpos
            elif entry.parent_position(pos[1]) is not None:
                return None

        child = tree.first_child_position(pos[0])
        if child is not None:
            entry = tree[child]
            if isinstance(entry, Tree):
                childpos = (child,) + (entry.root,)
            else:
                childpos = child,
        return childpos

    def last_child_position(self, pos, outmost_only=False):
        return self._last_child_position(self._tree, pos, outmost_only)

    def _last_child_position(self, tree, pos, outmost_only=False):
        childpos = None
        entry = tree[pos[0]]
        if isinstance(entry, Tree) and not outmost_only:
            subchild = self._last_child_position(entry, pos[1:])
            if subchild is not None:
                childpos = (pos[0],) + subchild
                return childpos
            elif len(pos)>1:
                if entry.parent_position(pos[1]) is not None:
                    return None
        child = tree.last_child_position(pos[0])
        if child is not None:
            entry = tree[child]
            if isinstance(entry, Tree):
                childpos = (child,) + (entry.root,)
            else:
                childpos = child,
        return childpos

    def _next_sibling_position(self, tree, pos):
        candidate = None
        if len(pos) > 1:
            subtree = tree[pos[0]]
            subsibling_pos = self._next_sibling_position(subtree, pos[1:])
            if subsibling_pos is not None:
                candidate = pos[:1] + subsibling_pos
            elif subtree.parent_position(pos[1]) is None:
                # go to outer tree sibline if inner pos has depth 0
                next_sib = tree.next_sibling_position(pos[0])
                if next_sib is not None:
                    candidate = next_sib,
                    entry = tree[next_sib]
                    if isinstance(entry, Tree):
                        candidate = candidate + (entry.root,)
        else:
            next_sib = tree.next_sibling_position(pos[0])
            if next_sib is not None:
                candidate = next_sib,
        if candidate is not None:
            entry = self._lookup_entry(tree, candidate)
            if isinstance(entry, Tree):
                candidate = candidate + (entry.root,)
        return candidate

    def next_sibling_position(self, pos):
        return self._next_sibling_position(self._tree, pos)

    def _prev_sibling_position(self, tree, pos):
        candidate = None
        if len(pos) > 1:
            subtree = tree[pos[0]]
            subsibling_pos = self._prev_sibling_position(subtree, pos[1:])
            if subsibling_pos is not None:
                candidate = pos[:1] + subsibling_pos
            elif subtree.parent_position(pos[1]) is None:
                prev_sib = tree.prev_sibling_position(pos[0])
                if prev_sib is not None:
                    candidate = prev_sib,
                    entry = tree[prev_sib]
                    if isinstance(entry, Tree):
                        candidate = candidate + (entry.root,)
        else:
            prev_sib = tree.prev_sibling_position(pos[0])
            if prev_sib is not None:
                candidate = prev_sib,
            if candidate is not None:
                entry = self._lookup_entry(tree, candidate)
                if isinstance(entry, Tree):
                    candidate = candidate + (entry.root,)
        return candidate

    def prev_sibling_position(self, pos):
        return self._prev_sibling_position(self._tree, pos)
