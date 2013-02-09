#!/usr/bin/python
# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

from example1 import palette, construct_example_tree, FocusableText  # example data
from widgets import TreeBox
from tree import SimpleTree
from nested import NestedTree
from decoration import ArrowTree, CollapsibleArrowTree
import urwid


if __name__ == "__main__":
    # Take some Arrow decorated Tree that we later stick inside another tree.
    innertree = ArrowTree(construct_example_tree())
    # Some collapsible, arrow decorated tree with extra indent
    anotherinnertree = CollapsibleArrowTree(construct_example_tree(),
                                            indent=10)

    # A SimpleTree, that contains the two above
    middletree = SimpleTree(
        [
            (FocusableText('Middle ROOT'),
             [
                 (FocusableText('Mid Child One'), None),
                 (FocusableText('Mid Child Two'), None),
                 (innertree, None),
                 (FocusableText('Mid Child Three'),
                  [
                      (FocusableText('Mid Grandchild One'), None),
                      (FocusableText('Mid Grandchild Two'), None),
                  ]
                  ),
                 (anotherinnertree,
                  [
                      (FocusableText('I will never be seen!'), None),

                  ]),
             ]
             )
        ]
    )  # end SimpleTree constructor
    middletree = ArrowTree(middletree,
                           arrow_hbar_char=u'\u2550',
                           arrow_vbar_char=u'\u2551',
                           arrow_tip_char=u'\u25B7',
                           arrow_connector_tchar=u'\u2560',
                           arrow_connector_lchar=u'\u255A')

    outertree = SimpleTree(
        [
            (FocusableText('Outer ROOT'),
             [
                 (FocusableText('Child One'), None),
                 (middletree, None),
                 (FocusableText('last outer child'), None),
             ]
             )
        ]
    )  # end SimpleTree constructor

    # add some Arrow decoration
    outertree = ArrowTree(outertree)
    # wrap the whole thing into a Nested Tree
    outertree = NestedTree(outertree, True)

    # put it into a treebox and run
    treebox = TreeBox(outertree)
    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
