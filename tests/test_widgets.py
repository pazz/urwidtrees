import gc
import unittest
import weakref

import urwid

from urwidtrees import (ArrowTree, CollapsibleArrowTree, CollapsibleTree,
                        SimpleTree, TreeBox)
from urwidtrees.widgets import TreeListWalker

from .test_tree import FlatList
from .utilities import Node, render, small_tree

SIZE = (20, 6)


class TestTreeBox(unittest.TestCase):

    def press(self, box, *keys):
        for key in keys:
            box.keypress(SIZE, key)
        return box.get_focus()[1]

    def test_initial_focus(self):
        self.assertEqual(TreeBox(small_tree()).get_focus()[1], (0,))
        box = TreeBox(small_tree(), focus=(0, 1))
        self.assertEqual(box.get_focus()[1], (0, 1))

    def test_list_movement(self):
        box = TreeBox(small_tree())
        self.assertEqual(self.press(box, 'down', 'down'), (0, 0, 0))
        self.assertEqual(self.press(box, 'up'), (0, 0))

    def test_tree_movement(self):
        box = TreeBox(small_tree())
        self.assertEqual(self.press(box, 'right'), (0, 0))
        self.assertEqual(self.press(box, ']'), (0, 1))
        self.assertEqual(self.press(box, '['), (0, 0))
        self.assertEqual(self.press(box, 'left'), (0,))
        # no parent: focus stays
        self.assertEqual(self.press(box, 'left'), (0,))

    def test_focus_methods(self):
        box = TreeBox(small_tree())
        box.focus_last_child()
        self.assertEqual(box.get_focus()[1], (0, 1))
        box.focus_prev()
        self.assertEqual(box.get_focus()[1], (0, 0, 1))
        box.focus_next()
        self.assertEqual(box.get_focus()[1], (0, 1))

    def test_unhandled_key_is_returned(self):
        self.assertEqual(TreeBox(small_tree()).keypress(SIZE, 'x'), 'x')

    def test_tree_key_without_effect_is_returned(self):
        box = TreeBox(small_tree())
        for key in ['left', '[', ']', '-', '+', 'C', 'E']:
            self.assertEqual(box.keypress(SIZE, key), key)
        self.assertIsNone(box.keypress(SIZE, 'right'))
        self.assertIsNone(box.keypress(SIZE, 'right'))
        self.assertEqual(box.keypress(SIZE, 'right'), 'right')
        for key in ['-', '+', 'C', 'E']:
            tree = CollapsibleTree(small_tree())
            tree.collapse((0, 0))
            box = TreeBox(tree)
            self.assertIsNone(box.keypress(SIZE, key))

    def test_collapse_keys(self):
        box = TreeBox(CollapsibleTree(small_tree()))
        self.press(box, 'right', '-', 'down')
        self.assertEqual(box.get_focus()[1], (0, 1))
        self.press(box, 'up', '+', 'down')
        self.assertEqual(box.get_focus()[1], (0, 0, 0))
        self.press(box, 'C')
        self.assertEqual(box.get_focus()[1], (0,))
        self.assertEqual(self.press(box, 'down'), (0,))
        self.assertEqual(self.press(box, 'E', 'down'), (0, 0))

    def test_collapse_ignored_without_collapse_api(self):
        box = TreeBox(small_tree())
        self.assertEqual(self.press(box, 'right', '-', 'down'), (0, 0, 0))

    def test_render(self):
        box = TreeBox(ArrowTree(small_tree()))
        self.assertEqual([line.rstrip() for line in render(box, 10, 6)[:5]], [
            'r', '├─➤a', '│  ├─➤a1', '│  └─➤a2', '└─➤b',
        ])

    def test_refresh_redraws_cached_lines(self):
        tree = CollapsibleArrowTree(small_tree())
        box = TreeBox(tree)
        self.assertEqual(render(box, 10, 6)[1].rstrip(), '├[-]➤a')
        tree.collapse((0, 0))
        box.refresh()
        self.assertEqual(render(box, 10, 6)[1].rstrip(), '├[+]➤a')

    def test_keys_reach_the_focused_row_once(self):
        received = []

        class Row(Node):
            def keypress(self, size, key):
                received.append(key)
                return key

        box = TreeBox(SimpleTree([(Row('r'), [(Row('a'), None)])]))
        for key in ['x', 'down', 'right']:
            box.keypress(SIZE, key)
        self.assertEqual(received, ['x', 'down', 'right'])

    def test_edit_rows(self):
        edit = urwid.Edit('', '')
        box = TreeBox(SimpleTree([(edit, None)]))
        for key in ['x', 'y', 'left', 'z']:
            box.keypress(SIZE, key)
        self.assertEqual(edit.edit_text, 'xzy')

    def test_tree_key_scrolls_focus_into_view(self):
        children = [(Node('c%d' % i), None) for i in range(30)]
        box = TreeBox(SimpleTree([(Node('r'), children)]))
        render(box, 10, 6)
        self.press(box, 'right', *[']'] * 20)
        self.assertEqual(render(box, 10, 6)[-1].rstrip(), 'c20')


class TestTreeListWalker(unittest.TestCase):

    def test_cache_per_walker(self):
        tree = ArrowTree(small_tree())
        first, second = TreeListWalker(tree), TreeListWalker(tree)
        line = first[(0, 1)]
        second.clear_cache()
        self.assertIs(first[(0, 1)], line)
        first.clear_cache()
        self.assertIsNot(first[(0, 1)], line)

    def test_walker_is_freed(self):
        walker = TreeListWalker(small_tree())
        walker[(0,)]
        ref = weakref.ref(walker)
        del walker
        gc.collect()
        self.assertIsNone(ref())

    def test_falsy_focus(self):
        class Countdown(FlatList):
            """positions 2, 1, 0 in this order"""
            root = 2
            next_sibling_position = FlatList.prev_sibling_position

        walker = TreeListWalker(Countdown([Node('a'), Node('b'), Node('c')]),
                                focus=0)
        self.assertEqual(walker.get_focus()[1], 0)
