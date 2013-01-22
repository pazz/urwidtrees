#!/usr/bin/python
# Copyright (C) 2013  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.

import urwid
from tree import SimpleTree
from widgets import TreeBox


# define some colours
palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
    ('bars', 'dark blue', 'light gray', ''),
    ('arrowtip', 'light blue', 'light gray', ''),
    ('connectors', 'light red', 'light gray', ''),
]

# define a test tree in the format accepted by SimpleTree. Essentially, a
# tree is given as (nodewidget, [list, of, subtrees]). SimpleTree accepts
# lists of such trees.


def construct_example_tree(selectable_nodes=True, children=2):
    class FocusableText(urwid.WidgetWrap):
        """Selectable Text used for nodes in our example"""
        def __init__(self, txt):
            t = urwid.Text(txt)
            w = urwid.AttrMap(t, 'body', 'focus')
            urwid.WidgetWrap.__init__(self, w)

        def selectable(self):
            return selectable_nodes

        def keypress(self, size, key):
            return key

    # define root node
    tree = (FocusableText('ROOT'), [])

    # define some children
    c = g = gg = 0  # counter
    for i in range(children):
        subtree = (FocusableText('Child %d' % c), [])
        # and grandchildren..
        for j in range(children):
            subsubtree = (FocusableText('Grandchild %d' % g), [])
            for k in range(children):
                leaf = (FocusableText('Grand Grandchild %d' % gg), None)
                subsubtree[1].append(leaf)
                gg += 1  # inc grand-grandchild counter
            subtree[1].append(subsubtree)
            g += 1  # inc grandchild counter
        tree[1].append(subtree)
        c += 1
    return tree

# define a list of trees to be passed on to SimpleTree
forrest = [construct_example_tree(children=4)]

# stick out test tree into a SimpleTree
stree = SimpleTree(forrest)

if __name__ == "__main__":
    # put the tree into a treebox
    treebox = TreeBox(stree)

    # add some decoration
    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
