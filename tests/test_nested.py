import unittest

from urwidtrees import (ArrowTree, CollapsibleTree, IndentedTree, NestedTree,
                        SimpleTree)

from .utilities import Node, render_tree


def nested_tree():
    """an ArrowTree with another ArrowTree as its middle child"""
    inner = ArrowTree(SimpleTree([(Node('x'), [(Node('y'), None)])]))
    outer = ArrowTree(SimpleTree([
        (Node('R'), [(Node('c'), None), (inner, None), (Node('z'), None)]),
    ]))
    return NestedTree(outer)


DFO = [((0,),), ((0, 0),), ((0, 1), (0,)), ((0, 1), (0, 0)), ((0, 2),)]


class TestNestedTree(unittest.TestCase):

    def setUp(self):
        self.tree = nested_tree()

    def test_positions(self):
        self.assertEqual(list(self.tree.positions()), DFO)
        self.assertEqual(list(self.tree.positions(reverse=True)), DFO[::-1])

    def test_getitem(self):
        self.assertEqual(self.tree[((0, 1), (0, 0))].text, 'y')

    def test_moves_across_trees(self):
        t = self.tree
        self.assertEqual(t.next_sibling_position(((0, 0),)), ((0, 1), (0,)))
        self.assertEqual(t.prev_sibling_position(((0, 2),)), ((0, 1), (0,)))
        self.assertEqual(t.parent_position(((0, 1), (0,))), ((0,),))
        self.assertEqual(t.parent_position(((0, 1), (0, 0))), ((0, 1), (0,)))
        self.assertEqual(t.first_child_position(((0, 1), (0,))),
                         ((0, 1), (0, 0)))

    def test_decoration(self):
        self.assertEqual(render_tree(self.tree, 20), [
            'R',
            '├─➤c',
            '├─➤x',
            '│  └─➤y',
            '└─➤z',
        ])

    def test_indented(self):
        inner = SimpleTree([(Node('x'), [(Node('y'), None)])])
        tree = NestedTree(SimpleTree([
            (Node('R'), [(Node('c'), None), (inner, None)]),
        ]))
        self.assertEqual(render_tree(IndentedTree(tree)),
                         ['R', '  c', '  x', '    y'])


class TestNestedCollapse(unittest.TestCase):

    def setUp(self):
        self.inner = CollapsibleTree(
            SimpleTree([(Node('x'), [(Node('y'), None)])]))
        self.tree = NestedTree(SimpleTree([(Node('R'), [(self.inner, None)])]))
        self.x = ((0, 0), (0,))

    def test_collapse_and_expand(self):
        self.tree.collapse(self.x)
        self.assertTrue(self.tree.is_collapsed(self.x))
        self.assertEqual(list(self.tree.positions()), [((0,),), self.x])
        self.tree.expand(self.x)
        self.assertFalse(self.tree.is_collapsed(self.x))

    def test_toggle_collapsed(self):
        self.tree.toggle_collapsed(self.x)
        self.assertTrue(self.inner.is_collapsed((0,)))
        self.tree.toggle_collapsed(self.x)
        self.assertFalse(self.inner.is_collapsed((0,)))
