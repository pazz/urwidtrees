import unittest

import urwid

from urwidtrees import (ArrowTree, CollapsibleArrowTree, CollapsibleTree,
                        SimpleTree, TreeBox)

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

    def test_refresh_moves_focus_out_of_collapsed_subtree(self):
        tree = CollapsibleTree(small_tree())
        box = TreeBox(tree, focus=(0, 0, 1))
        render(box, 10, 6)
        tree.collapse((0, 0))
        tree.collapse((0,))
        box.refresh()
        self.assertEqual(box.get_focus()[1], (0,))
        self.assertEqual(render(box, 10, 6)[0].rstrip(), 'r')
        self.assertEqual(self.press(box, 'down'), (0,))

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
