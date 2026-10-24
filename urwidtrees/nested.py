# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.
from .tree import Tree
from .decoration import DecoratedTree, CollapseMixin


class NestedTree(Tree):
    """
    A Tree that wraps around Trees that may contain list walkers or other
    trees.  The wrapped tree may contain normal widgets as well. List walkers
    and subtree contents will be expanded into the tree presented by this
    wrapper.

    This wrapper's positions are tuples of positions of the original and
    subtrees: For example, `(X,Y,Z)` points at position Z in tree/list at
    position Y in tree/list at position X in the original tree.

    A node holding a subtree may have children of its own, which the
    subtree covers. With `interpret_covered`, they are shown as further
    children of the subtree's first root, after the root's own children;
    an empty subtree hides them.

    NestedTree transparently behaves like a collapsible DecoratedTree.
    """
    @property
    def root(self):
        if self._tree.root is None:
            return None
        return self._sanitize_position((self._tree.root,))

    def _sanitize_position(self, pos, last=False):
        """
        Ensure a position tuple until the result does not
        point to a :class:`Tree` any more, entering subtrees at their first
        root, or at their last root if `last` is set. An empty subtree takes
        no place, so a position pointing at one moves on to its next
        sibling, or its previous one if `last` is set.
        """
        skip = self._prev_sibling_position if last else \
            self._next_sibling_position
        while pos is not None:
            entry = self[pos]
            if not isinstance(entry, Tree):
                return pos
            root = entry.root
            if root is None:
                pos = skip(pos)
            else:
                if last:
                    root = entry.last_sibling_position(root)
                pos = pos + (root,)
        return None

    def __init__(self, tree, interpret_covered=False):
        self._tree = tree
        self._interpret_covered = interpret_covered

    def _lookup_entry(self, tree, pos):
        entry = tree[pos[0]]
        if len(pos) > 1 and isinstance(entry, Tree):
            subtree = entry
            entry = self._lookup_entry(subtree, pos[1:])
        return entry

    def depth(self, pos):
        """
        depth of the node at pos, counting the levels of the outer tree and
        of every subtree on the way: a subtree's roots take the depth of
        the node that holds the subtree
        """
        tree, depth = self._tree, 0
        for local in pos:
            depth += tree.depth(local)
            tree = tree[local]
        return depth

    def __getitem__(self, pos):
        return self._lookup_entry(self._tree, pos)

    # DecoratedTree API
    def _get_decorated_entry(self, tree, pos, widget=None, is_first=True):
        entry = tree[pos[0]]
        if entry is None:
            return None
        if len(pos) > 1 and isinstance(entry, Tree):
            subtree = entry
            entry = self._get_decorated_entry(
                subtree, pos[1:], widget, is_first)
        else:
            entry = widget or entry
        if isinstance(tree, (DecoratedTree, NestedTree)):  # has decorate-API
            isf = len(pos) < 2
            if not isf and isinstance(tree[pos[0]], Tree):
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
        return self._trees(pos)[-1]

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
            subtree.toggle_collapsed(pos[-1])

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

    ################################################
    # Tree API
    ################################################
    def parent_position(self, pos):
        candidate_pos = self._parent_position(self._tree, pos)
        # return sanitized path (ensure it points to content, not a subtree)
        return self._sanitize_position(candidate_pos)

    def _parent_position(self, tree, pos):
        candidate_pos = None
        if len(pos) > 1:
            # get the deepest subtree
            subtree_pos = pos[:-1]
            subtree = self._lookup_entry(tree, subtree_pos)
            # get parent for our position in this subtree
            least_pos = pos[-1]
            subparent_pos = subtree.parent_position(least_pos)
            if subparent_pos is not None:
                # in case there is one, we are done, the position we look for
                # is the path up to the subtree plus the local parent position.
                candidate_pos = subtree_pos + (subparent_pos,)
            else:
                # otherwise we recur and look for subtree's parent in the next
                # outer tree
                candidate_pos = self._parent_position(self._tree, subtree_pos)
        else:
            # there is only one position in the path, we return its parent in
            # the outmost tree
            outer_parent = self._tree.parent_position(pos[0])
            if outer_parent is not None:
                # result needs to be valid position (tuple of local positions)
                candidate_pos = outer_parent,
        return candidate_pos

    # Children of a position: those of its node in the innermost tree, and,
    # with interpret_covered, those of the node holding that tree in the
    # next outer tree, as long as the position is the first root of the
    # inner tree, and so on outwards. Siblings run through the same lists.

    def _trees(self, pos):
        """the tree each local position in pos belongs to"""
        trees = [self._tree]
        for local in pos[:-1]:
            trees.append(trees[-1][local])
        return trees

    def _child_levels(self, pos, trees, level):
        """
        nesting levels, from `level` outwards, whose children of the local
        position at that level make up the children of pos, in order
        """
        for i in range(level, -1, -1):
            yield i
            if (not self._interpret_covered
                    or trees[i].parent_position(pos[i]) is not None
                    or trees[i].prev_sibling_position(pos[i]) is not None):
                return

    def _first_child(self, pos, trees, levels):
        for i in levels:
            child = trees[i].first_child_position(pos[i])
            if child is not None:
                return pos[:i] + (child,)
        return None

    def _last_child(self, pos, trees, levels):
        for i in reversed(list(levels)):
            child = trees[i].last_child_position(pos[i])
            if child is not None:
                return pos[:i] + (child,)
        return None

    def first_child_position(self, pos, outmost_only=False):
        if outmost_only:
            child = self._first_child(pos[:1], [self._tree], [0])
        else:
            trees = self._trees(pos)
            levels = self._child_levels(pos, trees, len(pos) - 1)
            child = self._first_child(pos, trees, levels)
        return self._sanitize_position(child)

    def last_child_position(self, pos, outmost_only=False):
        if outmost_only:
            child = self._last_child(pos[:1], [self._tree], [0])
        else:
            trees = self._trees(pos)
            levels = self._child_levels(pos, trees, len(pos) - 1)
            child = self._last_child(pos, trees, levels)
        return self._sanitize_position(child, last=True)

    def _next_sibling_position(self, pos):
        trees = self._trees(pos)
        for i in range(len(pos) - 1, -1, -1):
            sibling = trees[i].next_sibling_position(pos[i])
            if sibling is not None:
                return pos[:i] + (sibling,)
            parent = trees[i].parent_position(pos[i])
            if parent is not None:
                # last child at this level: children at outer levels follow
                parent_pos = pos[:i] + (parent,)
                levels = self._child_levels(parent_pos, trees, i)
                next(levels)
                return self._first_child(parent_pos, trees, levels)
            # a root of its tree: continue with the node holding the tree
        return None

    def next_sibling_position(self, pos):
        return self._sanitize_position(self._next_sibling_position(pos))

    def _prev_sibling_position(self, pos):
        trees = self._trees(pos)
        for i in range(len(pos) - 1, -1, -1):
            sibling = trees[i].prev_sibling_position(pos[i])
            if sibling is not None:
                return pos[:i] + (sibling,)
            parent = trees[i].parent_position(pos[i])
            if parent is not None:
                if not self._interpret_covered:
                    return None
                # first child at this level: if the parent holds a subtree,
                # children at inner levels come first
                root = self._sanitize_position(pos[:i] + (parent,))
                root_trees = self._trees(root)
                levels = [j for j in self._child_levels(
                    root, root_trees, len(root) - 1) if j > i]
                return self._last_child(root, root_trees, levels)
            # a root of its tree: continue with the node holding the tree
        return None

    def prev_sibling_position(self, pos):
        return self._sanitize_position(self._prev_sibling_position(pos),
                                       last=True)

    def last_decendant(self, pos):
        def lastd(pos):
            c = self.last_child_position(pos)
            if c is not None:
                c = self.last_sibling_position(c)
            return c
        return self._last_in_direction(pos, lastd)
