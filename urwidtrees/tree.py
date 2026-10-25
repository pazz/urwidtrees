# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.


class Tree(object):
    """
    Base class for a tree strucures that can be displayed by :class:`TreeBox`
    widgets. An instance defines a structure by defining local transformations
    on positions. That is, by overwriting

     * `next_sibling_position`
     * `prev_sibling_position`
     * `parent_position`
     * `first_child_position`
     * `last_child_position`

    that compute the next position in the respective direction. Also, they need
    to implement method `__getitem__` that returns a :class:`Widget` for a
    given position.

    The type of objects used as positions may vary in subclasses and is
    deliberately unspecified for the base class.

    This base class already implements methods based on the local
    transformations above. These include :meth:`depth`, :meth:`last_decendant`
    and :meth:`[next|prev]_position <next_position>` that computes
    next/previous positions in depth-first order.
    """
    root = None

    def _next_of_kin(self, pos):
        """
        looks up the next sibling of the closest ancestor with not-None next
        siblings.
        """
        parent = self.parent_position(pos)
        while parent is not None:
            candidate = self.next_sibling_position(parent)
            if candidate is not None:
                return candidate
            parent = self.parent_position(parent)
        return None

    @staticmethod
    def _last_in_direction(starting_pos, direction):
        """
        move in the tree in given direction and return the last position.

        :param starting_pos: position to start at
        :param direction: callable that transforms a position into a position.
        """
        cur_pos = None
        next_pos = starting_pos
        while next_pos is not None:
            cur_pos = next_pos
            next_pos = direction(cur_pos)
        return cur_pos

    def depth(self, pos):
        """determine depth of node at pos"""
        depth = 0
        pos = self.parent_position(pos)
        while pos is not None:
            depth += 1
            pos = self.parent_position(pos)
        return depth

    def is_leaf(self, pos):
        """checks if given position has no children"""
        return self.first_child_position(pos) is None

    def first_ancestor(self, pos):
        """
        position of pos's ancestor with depth 0. Usually, this should return
        the root node, but a :class:`Tree` might represent a forrest - have
        multiple nodes without parent.
        """
        return self._last_in_direction(pos, self.parent_position)

    def last_decendant(self, pos):
        """position of last (in DFO) descendant of pos"""
        return self._last_in_direction(pos, self.last_child_position)

    def last_sibling_position(self, pos):
        """position of last sibling of pos"""
        return self._last_in_direction(pos, self.next_sibling_position)

    def first_sibling_position(self, pos):
        """position of first sibling of pos"""
        return self._last_in_direction(pos, self.prev_sibling_position)

    def next_position(self, pos):
        """returns the next position in depth-first order"""
        if pos is None:
            return None
        candidate = self.first_child_position(pos)
        if candidate is None:
            candidate = self.next_sibling_position(pos)
        if candidate is None:
            candidate = self._next_of_kin(pos)
        return candidate

    def prev_position(self, pos):
        """returns the previous position in depth-first order"""
        if pos is None:
            return None
        prevsib = self.prev_sibling_position(pos)  # is None if first
        if prevsib is not None:
            return self.last_decendant(prevsib)
        return self.parent_position(pos)

    def positions(self, reverse=False):
        """returns a generator that walks the positions of this tree in DFO"""
        if reverse:
            current = self.last_decendant(self.last_sibling_position(self.root))
            step = self.prev_position
        else:
            current, step = self.root, self.next_position
        while current is not None:
            yield current
            current = step(current)

    ####################################################################
    # End of high-level helper implementation. The following need to be
    # overwritten by subclasses
    ####################################################################
    def parent_position(self, pos):
        """returns the position of the parent node of the node at `pos`
        or `None` if none exists."""
        return None

    def first_child_position(self, pos):
        """returns the position of the first child of the node at `pos`,
        or `None` if none exists."""
        return None

    def last_child_position(self, pos):
        """returns the position of the last child of the node at `pos`,
        or `None` if none exists."""
        return None

    def next_sibling_position(self, pos):
        """returns the position of the next sibling of the node at `pos`,
        or `None` if none exists."""
        return None

    def prev_sibling_position(self, pos):
        """returns the position of the previous sibling of the node at `pos`,
        or `None` if none exists."""
        return None


class SimpleTree(Tree):
    """
    Walks on a given fixed acyclic structure given as a list of nodes; every
    node is a tuple `(content, children)`, where `content` is a `urwid.Widget`
    to be displayed at that position and `children` is either `None` or a list
    of nodes.

    Positions are lists of integers determining a path from the root node with
    position `(0,)`.
    """
    def __init__(self, treelist):
        self._treelist = treelist
        self._root = None

    @property
    def root(self):
        """
        `(0,)`, or None while the tree is empty; a position assigned to
        `root` takes precedence (assigning None restores the default)
        """
        if self._root is not None:
            return self._root
        return (0,) if self._treelist else None

    @root.setter
    def root(self, pos):
        self._root = pos

    # a few local helper methods
    def _get_substructure(self, pos):
        """look up node-tuple for `pos`; default to None if nonexistent"""
        treelist = self._treelist
        for index in pos[:-1]:
            treelist = treelist[index][1]
        try:
            return treelist[pos[-1]]
        except (IndexError, TypeError):
            return None

    def _get_node(self, pos):
        """look up widget at `pos`; default to None if nonexistent"""
        subtree = None if pos is None else self._get_substructure(pos)
        return None if subtree is None else subtree[0]

    def _confirm_pos(self, pos):
        """pos if it holds a widget, else None"""
        return pos if self._get_node(pos) is not None else None

    # Tree API
    def __getitem__(self, pos):
        return self._get_node(pos)

    @staticmethod
    def parent_position(pos):
        parent = None
        if pos is not None and len(pos) > 1:
            parent = pos[:-1]
        return parent

    def first_child_position(self, pos):
        return self._confirm_pos(pos + (0,))

    def last_child_position(self, pos):
        candidate = None
        subtree = self._get_substructure(pos)
        if subtree is not None:
            children = subtree[1]
            if children:
                candidate = pos + (len(children) - 1,)
        return candidate

    def next_sibling_position(self, pos):
        return self._confirm_pos(pos[:-1] + (pos[-1] + 1,))

    @staticmethod
    def prev_sibling_position(pos):
        return pos[:-1] + (pos[-1] - 1,) if (pos[-1] > 0) else None

    # optimizations
    @staticmethod
    def depth(pos):
        """more performant implementation due to specific structure of pos"""
        return len(pos) - 1
