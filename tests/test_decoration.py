import unittest

import urwid

from urwidtrees import (ArrowTree, CollapsibleArrowTree,
                        CollapsibleIndentedTree, CollapsibleTree,
                        DecoratedTree, IndentedTree)
from urwidtrees.decoration import NoSpaceError

from .utilities import render, render_tree, small_tree

ALL = [(0,), (0, 0), (0, 0, 0), (0, 0, 1), (0, 1)]


class TestDecoratedTree(unittest.TestCase):

    def test_delegates_to_wrapped_tree(self):
        t = DecoratedTree(small_tree())
        self.assertEqual(list(t.positions()), ALL)
        self.assertIs(t.get_decorated((0, 1)), t[(0, 1)])

    def test_accepts_tree_list(self):
        t = DecoratedTree(small_tree()._treelist)
        self.assertEqual(list(t.positions()), ALL)


class TestCollapsibleTree(unittest.TestCase):

    def setUp(self):
        self.tree = CollapsibleTree(small_tree())

    def test_collapse_and_expand(self):
        t = self.tree
        t.collapse((0, 0))
        self.assertTrue(t.is_collapsed((0, 0)))
        self.assertEqual(list(t.positions()), [(0,), (0, 0), (0, 1)])
        t.expand((0, 0))
        self.assertEqual(list(t.positions()), ALL)
        t.toggle_collapsed((0, 0))
        self.assertTrue(t.is_collapsed((0, 0)))

    def test_leaves_do_not_collapse(self):
        self.assertFalse(self.tree.collapsible((0, 1)))
        self.tree.collapse((0, 1))
        self.assertFalse(self.tree.is_collapsed((0, 1)))

    def test_collapse_all(self):
        t = self.tree
        t.collapse_all()
        self.assertEqual(list(t.positions()), [(0,)])
        t.expand_all()
        self.assertEqual(list(t.positions()), ALL)

    def test_initially_collapsed(self):
        t = CollapsibleTree(small_tree(), is_collapsed=lambda pos: pos == (0, 0))
        self.assertEqual(list(t.positions()), [(0,), (0, 0), (0, 1)])
        t.expand((0, 0))
        self.assertEqual(list(t.positions()), ALL)

    def test_is_collapsed_callable_may_return_any_truth_value(self):
        t = CollapsibleTree(small_tree(), is_collapsed={(0, 0): 1}.get)
        self.assertIs(t.is_collapsed((0,)), False)
        self.assertIs(t.is_collapsed((0, 0)), True)
        t.expand((0,))
        t.expand((0, 0))
        self.assertEqual(list(t.positions()), ALL)
        t.collapse((0,))
        self.assertEqual(list(t.positions()), [(0,)])


class TestDecorations(unittest.TestCase):

    def test_indented(self):
        self.assertEqual(render_tree(IndentedTree(small_tree())), [
            'r',
            '  a',
            '    a1',
            '    a2',
            '  b',
        ])

    def test_collapsible_indented(self):
        t = CollapsibleIndentedTree(small_tree())
        self.assertEqual(render_tree(t), [
            '[-] r',
            '    [-] a',
            '            a1',
            '            a2',
            '        b',
        ])
        t.collapse((0, 0))
        self.assertEqual(render_tree(t), [
            '[-] r',
            '    [+] a',
            '        b',
        ])

    def test_collapsible_indented_leaves_need_no_icon_space(self):
        t = CollapsibleIndentedTree(small_tree(), indent=2)
        self.assertEqual(render(t.get_decorated((0, 0, 1)), 16)[0].rstrip(),
                         '      a2')
        with self.assertRaises(NoSpaceError):
            t.get_decorated((0, 0))
        t = CollapsibleIndentedTree(small_tree(), indent=2, icon_offset=3,
                                    icon_collapsed_char=None,
                                    icon_expanded_char=None)
        self.assertEqual(render(t.get_decorated((0, 0)), 16)[0].rstrip(),
                         '    a')

    def test_arrows(self):
        self.assertEqual(render_tree(ArrowTree(small_tree())), [
            'r',
            '├─➤a',
            '│  ├─➤a1',
            '│  └─➤a2',
            '└─➤b',
        ])

    def test_arrows_with_childbar_offset(self):
        t = ArrowTree(small_tree(), childbar_offset=1, indent=4)
        self.assertEqual(render_tree(t), [
            'r',
            '├──➤a',
            '│  ├──➤a1',
            '│  └──➤a2',
            '└──➤b',
        ])
        # continuation lines of multi-line nodes keep the same columns
        rest = [render(t.decorate(p, urwid.Text(t[p].text), is_first=False),
                       16)[0].rstrip() for p in t.positions()]
        self.assertEqual(rest, [
            'r',
            '│   a',
            '│  │   a1',
            '│      a2',
            '    b',
        ])

    def test_collapsible_arrows(self):
        t = CollapsibleArrowTree(small_tree())
        self.assertEqual(render_tree(t), [
            'r',
            '├[-]➤a',
            '│    ├───➤a1',
            '│    └───➤a2',
            '└───➤b',
        ])
        t.collapse((0, 0))
        self.assertEqual(render_tree(t), [
            'r',
            '├[+]➤a',
            '└───➤b',
        ])

    def test_arrows_without_bars(self):
        t = ArrowTree(small_tree(), arrow_hbar_char=None, arrow_vbar_char=None)
        self.assertEqual(render_tree(t), [
            'r',
            '├ ➤a',
            '   ├ ➤a1',
            '   └ ➤a2',
            '└ ➤b',
        ])
        t = CollapsibleArrowTree(small_tree(), icon_offset=2, indent=8,
                                 arrow_hbar_char=None, arrow_vbar_char=None)
        self.assertEqual(render_tree(t, 20)[1:3], [
            '├ [-]  ➤a',
            '        ├      ➤a1',
        ])

    def test_collapsible_arrows_with_icon_offset(self):
        t = CollapsibleArrowTree(small_tree(), icon_offset=2, indent=8)
        self.assertEqual(render_tree(t, 20), [
            'r',
            '├─[-]──➤a',
            '│       ├──────➤a1',
            '│       └──────➤a2',
            '└──────➤b',
        ])

    def test_arrows_without_connectors(self):
        t = ArrowTree(small_tree(), arrow_connector_tchar=None,
                      arrow_connector_lchar=None)
        self.assertEqual(render_tree(t), [
            'r',
            '──➤a',
            '│  ──➤a1',
            '│  ──➤a2',
            '──➤b',
        ])
