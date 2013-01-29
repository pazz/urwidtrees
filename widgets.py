# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import urwid
import logging
from urwid import WidgetWrap, ListBox
from urwid import signals
from decoration import DecoratedTree, CollapseMixin
from nested import NestedTree
from lru_cache import lru_cache

# The following are used to check dynamically if a tree offers sub-APIs
def implementsDecorateAPI(tree):
    """determines if given tree offers line decoration"""
    return isinstance(tree, (DecoratedTree, NestedTree))


def implementsCollapseAPI(tree):
    """determines if given tree can collapse positions"""
    res = False
    if isinstance(tree, (CollapseMixin, NestedTree)):
        res = True
    return res

class TreeListWalker(urwid.ListWalker):
    """
    ListWalker to walk through a class:`Tree`.

    This translates a :class:`Tree` into a :class:`urwid.ListWalker` that is
    digestible by :class:`urwid.ListBox`.
    """
    def __init__(self, tree, focus=None):
        """
        :param tree: the tree of widgets to be displayed
        :type tree: Tree
        :param focus: position of node to be focussed initially.
            This has to be a valid position in the Tree.
            It defaults to the value of `Tree.root`.
        """
        self._tree = tree
        self._focus = focus or tree.root
        self.root = tree.root

    @lru_cache()
    def __getitem__(self, pos):
        if implementsDecorateAPI(self._tree):
            entry = self._tree.get_decorated(pos)
        else:
            entry = self._tree[pos]
        return entry

    def _get(self, pos):
        """loads widget at given position; handling invalid arguments"""
        res = None, None
        if pos is not None:
            try:
                res = self[pos], pos
            except (IndexError, KeyError):
                pass
        return res

    # List Walker API.
    def get_focus(self):
        return self._get(self._focus)

    def set_focus(self, pos):
        self._focus = pos

    def get_next(self, pos):
        return self._get(self._tree.next_position(pos))

    def get_prev(self, pos):
        return self._get(self._tree.prev_position(pos))

    def positions(self, reverse=False):
        if reverse:
            pos = self._tree.last_sibling_position(self._tree.root)
            pos = self._tree.last_decendant(pos)
            while pos is not None:
                yield pos
                widget, pos = self.get_prev(pos)
        else:
            pos = self._tree.root
            while pos is not None:
                yield pos
                widget, pos = self.get_next(pos)
    # end of List Walker API

    def clear_cache(self):
        self.__getitem__.cache_clear()


class TreeBox(WidgetWrap):
    """
    A widget representing something in a nested tree display.
    This is essentially a ListBox with the ability to move the focus based on
    directions in the Tree.

    TreeBox interprets `left/right` as well as page `up/down` to move the focus
    to parent/first child and next/previous sibling respectively. All other
    keys are passed to the underlying ListBox.
    """
    _selectable = True

    def __init__(self, tree, focus=None):
        """
        :param tree: tree of widgets to be displayed.
        :type tree: Tree
        """
        self._tree = tree
        self._walker = TreeListWalker(tree)
        self._outer_list = ListBox(self._walker)
        if focus is not None:
            self._outer_list.set_focus(focus)
        self.__super.__init__(self._outer_list)

    # Widget API
    def get_focus(self):
        return self._outer_list.get_focus()

    def set_focus(self, pos):
        return self._outer_list.set_focus(pos)

    def keypress(self, size, key):
        key = self._outer_list.keypress(size, key)
        if key in ['left', 'right', '[', ']', '-', '+', 'C', 'E',]:
            if key == 'left':
                self.focus_parent()
            elif key == 'right':
                self.focus_first_child()
            elif key == '[':
                self.focus_prev_sibling()
            elif key == ']':
                self.focus_next_sibling()
            elif key == '-':
                self.collapse_focussed()
            elif key == '+':
                self.expand_focussed()
            elif key == 'C':
                self.collapse_all()
            elif key == 'E':
                self.expand_all()
            # This is a hack around ListBox misbehaving:
            # it seems impossible to set the focus without calling keypress as
            # otherwise the change becomes visible only after the next render()
            return self._outer_list.keypress(size, None)
        else:
            return self._outer_list.keypress(size, key)

    # Collapse operations
    def collapse_focussed(self):
        if implementsCollapseAPI(self._tree):
            w, focuspos = self.get_focus()
            self._tree.collapse(focuspos)
            self._walker.clear_cache()
            signals.emit_signal(self._walker, "modified")

    def expand_focussed(self):
        if implementsCollapseAPI(self._tree):
            w, focuspos = self.get_focus()
            self._tree.expand(focuspos)
            self._walker.clear_cache()
            signals.emit_signal(self._walker, "modified")

    def collapse_all(self):
        if implementsCollapseAPI(self._tree):
            self._tree.collapse_all()
            self.set_focus(self._tree.root)
            self._walker.clear_cache()
            signals.emit_signal(self._walker, "modified")

    def expand_all(self):
        if implementsCollapseAPI(self._tree):
            self._tree.expand_all()
            self._walker.clear_cache()
            signals.emit_signal(self._walker, "modified")

    # Tree based focus movement
    def focus_parent(self):
        w, focuspos = self.get_focus()
        parent = self._tree.parent_position(focuspos)
        if parent is not None:
            self.set_focus(parent)

    def focus_first_child(self):
        w, focuspos = self.get_focus()
        child = self._tree.first_child_position(focuspos)
        if child is not None:
            self.set_focus(child)

    def focus_last_child(self):
        w, focuspos = self.get_focus()
        child = self._tree.last_child_position(focuspos)
        if child is not None:
            self.set_focus(child)

    def focus_next_sibling(self):
        w, focuspos = self.get_focus()
        sib = self._tree.next_sibling_position(focuspos)
        if sib is not None:
            self.set_focus(sib)

    def focus_prev_sibling(self):
        w, focuspos = self.get_focus()
        sib = self._tree.prev_sibling_position(focuspos)
        if sib is not None:
            self.set_focus(sib)
