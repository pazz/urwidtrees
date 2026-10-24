import unittest

from urwidtrees import ArrowTree, NestedTree, SimpleTree

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
