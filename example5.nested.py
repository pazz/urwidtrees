#!/usr/bin/python
# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

from example1 import palette, construct_example_tree, FocusableText  # example data
from widgets import TreeBox
from tree import SimpleTree
from nested import NestedTree
from decoration import ArrowTree, CollapsibleArrowTree
import urwid
import logging


if __name__ == "__main__":
    # Take some Arrow decorated Tree that we later stick inside another tree.
    innertree = ArrowTree(construct_example_tree(),
                          arrow_hbar_char=u'\u2550',
                          arrow_vbar_char=u'\u2551',
                          arrow_tip_char=u'\u25B7',
                          arrow_connector_tchar=u'\u2560',
                          arrow_connector_lchar=u'\u255A')
    # Some collapsible, arrow decorated tree with extra indent
    anotherinnertree = CollapsibleArrowTree(construct_example_tree(),
                                            indent=10)

    # A SimpleTree, that contains the two above
    outertree = SimpleTree(
        [
            (FocusableText('ROOT'),
             [
                 (FocusableText('Child One'), None),
                 (FocusableText('Child Two'), None),
                 (innertree, None),
                 (FocusableText('Child Three'), None),
                 (anotherinnertree, None),
             ]
             )
        ]
    )  # end SimpleTree constructor

    # add some Arrow decoration
    outertree = ArrowTree(outertree)
    # wrap the whole thing into a Nested Tree
    outertree = NestedTree(outertree)

    # put it into a treebox and run
    treebox = TreeBox(outertree)
    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
