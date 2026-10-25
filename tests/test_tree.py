import unittest

from urwidtrees import SimpleTree, Tree

from .utilities import Node, small_tree


class TestSimpleTree(unittest.TestCase):

    def setUp(self):
        self.tree = small_tree()

    def test_getitem(self):
        self.assertEqual(self.tree[(0, 0, 1)].text, 'a2')
        self.assertIsNone(self.tree[(0, 5)])

    def test_root(self):
        self.assertEqual(self.tree.root, (0,))
        self.assertIsNone(SimpleTree([]).root)

    def test_root_follows_list(self):
        nodes = []
        tree = SimpleTree(nodes)
        self.assertIsNone(tree.root)
        nodes.append((Node('a'), None))
        self.assertEqual(tree.root, (0,))
        self.assertEqual(list(tree.positions()), [(0,)])
        nodes.clear()
        self.assertIsNone(tree.root)

    def test_local_moves(self):
        t = self.tree
        self.assertIsNone(t.parent_position((0,)))
        self.assertEqual(t.parent_position((0, 0, 1)), (0, 0))
        self.assertEqual(t.first_child_position((0,)), (0, 0))
        self.assertEqual(t.last_child_position((0,)), (0, 1))
        self.assertIsNone(t.first_child_position((0, 1)))
        self.assertIsNone(t.last_child_position((0, 1)))
        self.assertEqual(t.next_sibling_position((0, 0)), (0, 1))
        self.assertIsNone(t.next_sibling_position((0, 1)))
        self.assertEqual(t.prev_sibling_position((0, 1)), (0, 0))
        self.assertIsNone(t.prev_sibling_position((0, 0)))

    def test_derived_moves(self):
        t = self.tree
        self.assertEqual(t.depth((0, 0, 1)), 2)
        self.assertTrue(t.is_leaf((0, 1)))
        self.assertFalse(t.is_leaf((0, 0)))
        self.assertEqual(t.first_ancestor((0, 0, 1)), (0,))
        self.assertEqual(t.last_decendant((0,)), (0, 1))
        self.assertEqual(t.last_decendant((0, 0)), (0, 0, 1))
        self.assertEqual(t.last_sibling_position((0, 0)), (0, 1))
        self.assertEqual(t.first_sibling_position((0, 1)), (0, 0))
        self.assertEqual(t.next_position((0, 0, 1)), (0, 1))
        self.assertEqual(t.prev_position((0, 1)), (0, 0, 1))
        self.assertIsNone(t.next_position((0, 1)))
        self.assertIsNone(t.prev_position((0,)))

    def test_positions(self):
        dfo = [(0,), (0, 0), (0, 0, 0), (0, 0, 1), (0, 1)]
        self.assertEqual(list(self.tree.positions()), dfo)
        self.assertEqual(list(self.tree.positions(reverse=True)), dfo[::-1])

    def test_forest(self):
        t = SimpleTree([(Node('x'), None), (Node('y'), [(Node('z'), None)])])
        self.assertEqual(list(t.positions()), [(0,), (1,), (1, 0)])
        self.assertEqual(t.first_ancestor((1, 0)), (1,))


class FlatList(Tree):
    """a Tree that relies on the defaults for parents and children"""
    root = 0

    def __init__(self, widgets):
        self._widgets = widgets

    def __getitem__(self, pos):
        return self._widgets[pos]

    def next_sibling_position(self, pos):
        return pos + 1 if pos + 1 < len(self._widgets) else None

    def prev_sibling_position(self, pos):
        return pos - 1 if pos > 0 else None


class TestTreeDefaults(unittest.TestCase):

    def test_flat_list(self):
        t = FlatList([Node('a'), Node('b'), Node('c')])
        self.assertEqual(list(t.positions()), [0, 1, 2])
        self.assertEqual(list(t.positions(reverse=True)), [2, 1, 0])
        self.assertEqual(t.depth(2), 0)
        self.assertEqual(t.first_ancestor(2), 2)
        self.assertTrue(t.is_leaf(1))
