import unittest

from urwidtrees import (ArrowTree, CollapsibleTree, IndentedTree, NestedTree,
                        SimpleTree)

from .utilities import Node, render, render_tree


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


    def test_arrows_skip_empty_subtrees(self):
        """an empty subtree after the last node draws no connector or bar"""
        empty = SimpleTree([])
        tree = NestedTree(ArrowTree(SimpleTree([
            (Node('R'), [(Node('a'), [(Node('a1'), None)]), (empty, None),
                         (SimpleTree([(empty, None)]), None)]),
        ])))
        self.assertEqual(render_tree(tree), ['R', '└─➤a', '   └─➤a1'])
        a1 = ((0, 0, 0),)
        self.assertEqual(render(tree.decorate(a1, Node('m'), False), 8)[0],
                         '      m ')

    def test_arrows_skip_deeply_nested_empty_subtree(self):
        # decoration only: NestedTree navigation still recurses once per
        # nesting level
        empty = SimpleTree([])
        for _ in range(1500):
            empty = SimpleTree([(empty, None)])
        tree = NestedTree(ArrowTree(SimpleTree([
            (Node('R'), [(Node('a'), None), (empty, None)])])))
        self.assertEqual(render(tree.get_decorated(((0, 0),)), 8)[0],
                         '└─➤a    ')

    def test_decoration_two_levels(self):
        inner = ArrowTree(SimpleTree([(Node('x'), [(Node('y'), None)])]))
        middle = ArrowTree(SimpleTree([(inner, None)]))
        outer = ArrowTree(SimpleTree([
            (Node('R'), [(Node('c'), None), (middle, None), (Node('z'), None)]),
        ]))
        self.assertEqual(render_tree(NestedTree(outer), 20), [
            'R',
            '├─➤c',
            '├─➤x',
            '│  └─➤y',
            '└─➤z',
        ])

    def test_decorate_continuation_line(self):
        """is_first=False decorates like the wrapped tree does"""
        arrows = self.tree._tree
        for pos in self.tree.positions():
            with self.subTest(pos=pos):
                line = render(self.tree.decorate(pos, Node('m'), False), 20)
                if len(pos) == 1:
                    expected = render(arrows.decorate(pos[0], Node('m'), False),
                                      20)
                    self.assertEqual(line, expected)
                self.assertNotIn('➤', line[0])


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

    def test_root_subtree(self):
        """one-element positions belong to the outer tree, also when its
        root is a subtree"""
        inner = CollapsibleTree(SimpleTree([(Node('x'), [(Node('y'), None)])]))
        outer = CollapsibleTree(SimpleTree([
            (inner, None), (Node('b'), [(Node('c'), None)])]))
        tree = NestedTree(outer)
        b = ((1,),)
        self.assertTrue(tree.collapsible(b))
        tree.collapse(b)
        self.assertTrue(tree.is_collapsed(b))
        self.assertTrue(outer.is_collapsed((1,)))
        self.assertFalse(inner.is_collapsed((0,)))
        self.assertEqual(list(tree.positions()),
                         [((0,), (0,)), ((0,), (0, 0)), b])
        tree.toggle_collapsed(b)
        self.assertFalse(outer.is_collapsed((1,)))
        tree.collapse(b)
        tree.expand(b)
        self.assertFalse(tree.is_collapsed(b))

    def test_collapse_all_reaches_hidden_subtrees(self):
        inner = CollapsibleTree(SimpleTree([(Node('x'), [(Node('y'), None)])]))
        outer = CollapsibleTree(
            SimpleTree([(Node('R'), [(Node('a'), [(inner, None)])])]),
            is_collapsed=lambda pos: pos == (0, 0))
        tree = NestedTree(outer)
        tree.collapse_all()
        self.assertTrue(inner.is_collapsed((0,)))
        self.assertEqual(list(tree.positions()), [((0,),)])
        tree.expand_all()
        self.assertEqual(len(list(tree.positions())), 4)

    def test_collapse_all_wide(self):
        outer = CollapsibleTree(SimpleTree([(Node('R'), [
            (Node(str(i)), [(Node('c'), None)]) for i in range(1500)])]))
        tree = NestedTree(outer)
        tree.collapse_all()
        self.assertEqual(list(tree.positions()), [((0,),)])
        tree.expand_all()
        self.assertEqual(len(list(tree.positions())), 3001)
