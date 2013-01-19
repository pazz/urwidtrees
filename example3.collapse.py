#!/usr/bin/python
# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

from example1 import stree, palette  # example data
from decoration import CollapsibleIndentedTree, CollapsibleTree  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # Use (subclasses of) the CollapsibleTree wrapper to construct a tree where
    # subtrees are collapsible. Apart from a `Tree`, these take a callable
    # `is_collapsed` that defines initial collapsed-status if a given position.

    # We want all grandchildren collapsed initially
    if_grandchild = lambda pos: stree.depth(pos) > 1

    # We use CollapsibleIndentedTree around the original example tree stree.
    # This uses Indentation to indicate the tree structure and squeezes in
    # text-icons to indicate the collapsed status.
    tree = CollapsibleIndentedTree(stree,
                                   is_collapsed=if_grandchild,
                                   selectable_icons=True,
                                   icon_focussed_att='focus',
                                   # indent=6,
                                   # childbar_offset=1,
                                   # icon_frame_left_char=None,
                                   # icon_frame_right_char=None,
                                   # icon_expanded_char='-',
                                   # icon_collapsed_char='+',
                                   )

    # put the tree into a treebox
    treebox = TreeBox(tree)

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
