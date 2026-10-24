"""
Navigation invariants checked on randomly generated trees.

Every tree is built twice: as the tree under test, and as a flat list of
(widget, parent widget, depth) in depth-first order, which is what the
tree under test should present.
"""
import itertools
import random
import unittest

from urwidtrees import (ArrowTree, CollapsibleArrowTree,
                        CollapsibleIndentedTree, CollapsibleTree,
                        DecoratedTree, IndentedTree, NestedTree, SimpleTree,
                        TreeBox)

from .utilities import Node, render

SEEDS = range(50)


def random_forest(rng, labels, depth=4, width=3, nesting=0,
                  inner_forests=False, root_subtree=False, empty=False,
                  covered=False):
    """
    a random list of `(widget, children)` nodes for `SimpleTree`.
    With `nesting` > 0, some leaves hold a random tree instead of a widget,
    to be expanded by `NestedTree`; subtrees contain further subtrees up to
    `nesting` levels, have several roots only with `inner_forests`, and
    the very first root is a subtree only with `root_subtree`. With
    `empty`, some subtrees are empty, and with `covered`, some leaves that
    hold a subtree have children too.
    """
    forest = []
    for i in range(rng.randint(1, width)):
        allowed = i > 0 or root_subtree
        if nesting and depth > 0 and allowed and rng.random() < 0.3:
            inner = random_forest(rng, labels, depth - 1,
                                  width if inner_forests else 1,
                                  nesting - 1, inner_forests, root_subtree,
                                  empty, covered)
            if empty and rng.random() < 0.3:
                inner = []
            children = None
            if covered and rng.random() < 0.5:
                children = random_forest(rng, labels, depth - 1, width,
                                         nesting, inner_forests, True, empty,
                                         covered)
            forest.append((SimpleTree(inner), children))
            continue
        children = rng.choice([None, []])  # both mean no children
        if depth > 0 and rng.random() < 0.6:
            children = random_forest(rng, labels, depth - 1, width, nesting,
                                     inner_forests, True, empty, covered)
        forest.append((Node(str(next(labels))), children))
    return forest


def flatten(forest, parent=None, depth=0, covered=False):
    """
    (widget, parent widget, depth) for every displayed node in DFO, with
    subtrees expanded in place of the leaf that holds them. With `covered`,
    the children of such a leaf follow those of the subtree's first root.
    """
    for content, children in forest:
        if isinstance(content, SimpleTree):
            inner = content._treelist
            if covered and children and inner:
                (root, kids), *rest = inner
                inner = [(root, (kids or []) + children)] + rest
            yield from flatten(inner, parent, depth, covered)
        else:
            yield content, parent, depth
            yield from flatten(children or [], content, depth + 1, covered)


def parent_steps(tree, pos):
    steps = 0
    while tree.parent_position(pos) is not None:
        pos = tree.parent_position(pos)
        steps += 1
    return steps


def walk(tree, limit, reverse=False):
    """positions in DFO, cut off after `limit` in case the walk loops"""
    return list(itertools.islice(tree.positions(reverse), limit))


class InvariantsMixin:

    def check_navigation(self, tree, expected):
        """local and derived moves agree with each other and with the
        expected DFO list"""
        positions = walk(tree, len(expected) + 1)
        self.assertEqual(walk(tree, len(expected) + 1, reverse=True),
                         positions[::-1])
        self.assertEqual([tree[p] for p in positions],
                         [w for w, _, _ in expected])
        parent_of = {w: p for w, p, _ in expected}
        for p, q in zip(positions, positions[1:]):
            self.assertEqual(tree.next_position(p), q)
            self.assertEqual(tree.prev_position(q), p)
        for p in positions:
            parent = tree.parent_position(p)
            self.assertIs(tree[parent] if parent is not None else None,
                          parent_of[tree[p]])
            first = tree.first_child_position(p)
            last = tree.last_child_position(p)
            self.assertEqual(tree.is_leaf(p), first is None)
            self.assertEqual(first is None, last is None)
            if first is not None:
                self.assertEqual(tree.parent_position(first), p)
                self.assertEqual(tree.parent_position(last), p)
                self.assertIsNone(tree.prev_sibling_position(first))
                self.assertIsNone(tree.next_sibling_position(last))
                self.assertEqual(tree.last_sibling_position(first), last)
                self.assertEqual(tree.first_sibling_position(last), first)
            sibling = tree.next_sibling_position(p)
            if sibling is not None:
                self.assertEqual(tree.prev_sibling_position(sibling), p)
                self.assertEqual(tree.parent_position(sibling), parent)

    def check_depth(self, tree, expected):
        depth_of = {w: d for w, _, d in expected}
        for p in walk(tree, len(expected) + 1):
            self.assertEqual(tree.depth(p), depth_of[tree[p]])
            self.assertEqual(tree.depth(p), parent_steps(tree, p))


class TestSimpleTree(InvariantsMixin, unittest.TestCase):

    def test_navigation_and_depth(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                forest = random_forest(random.Random(seed), itertools.count())
                expected = list(flatten(forest))
                tree = SimpleTree(forest)
                self.check_navigation(tree, expected)
                self.check_depth(tree, expected)

    def test_empty_child_lists(self):
        for forest in [[(Node('r'), [])],
                       [(Node('r'), [(Node('a'), []), (Node('b'), None)])]]:
            with self.subTest(forest=forest):
                self.check_navigation(SimpleTree(forest), list(flatten(forest)))

    # RecursionError, one frame per level in SimpleTree._get_substructure,
    # Tree.depth and ArrowTree._construct_spacer
    @unittest.expectedFailure
    def test_deep_chain(self):
        forest = None
        for i in range(1100):
            forest = [(Node(str(i)), forest)]
        tree = ArrowTree(SimpleTree(forest))
        last = tree.last_decendant(tree.root)
        self.assertEqual(tree.depth(last), 1099)
        render(tree.get_decorated(last), 1200)

    def test_wide_node(self):
        children = [(Node(str(i)), None) for i in range(10000)]
        tree = SimpleTree([(Node('r'), children)])
        self.assertEqual(len(list(tree.positions())), 10001)


DECORATORS = [
    DecoratedTree,
    CollapsibleTree,
    IndentedTree,
    CollapsibleIndentedTree,
    ArrowTree,
    CollapsibleArrowTree,
]


class TestDecoratedTrees(InvariantsMixin, unittest.TestCase):

    def forests(self):
        for seed in SEEDS[:10]:
            yield seed, random_forest(random.Random(seed), itertools.count())

    def test_navigation_and_depth(self):
        for cls in DECORATORS:
            for seed, forest in self.forests():
                with self.subTest(cls=cls.__name__, seed=seed):
                    expected = list(flatten(forest))
                    tree = cls(SimpleTree(forest))
                    self.check_navigation(tree, expected)
                    self.check_depth(tree, expected)

    def test_every_line_renders_its_node(self):
        for cls in DECORATORS:
            for seed, forest in self.forests():
                with self.subTest(cls=cls.__name__, seed=seed):
                    tree = cls(SimpleTree(forest))
                    for p in tree.positions():
                        line = render(tree.get_decorated(p), 80)[0]
                        self.assertTrue(line.rstrip().endswith(tree[p].text))
                        if cls is IndentedTree:
                            self.assertEqual(line.rstrip(), ' ' * 2 * len(p[1:])
                                             + tree[p].text)

    def test_collapse(self):
        """collapsing hides exactly the descendants of collapsed nodes"""
        for seed, forest in self.forests():
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                tree = CollapsibleTree(SimpleTree(forest))
                inner = [p for p in tree.positions() if not tree.is_leaf(p)]
                collapsed = set(rng.sample(inner, len(inner) // 2))
                for p in collapsed:
                    tree.collapse(p)
                visible = [p for p in SimpleTree(forest).positions()
                           if not any(p[:i] in collapsed
                                      for i in range(1, len(p)))]
                self.assertEqual(list(tree.positions()), visible)
                tree.expand_all()
                self.assertEqual(list(tree.positions()),
                                 list(SimpleTree(forest).positions()))


class TestNestedTree(InvariantsMixin, unittest.TestCase):

    def check(self, check, **shape):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                forest = random_forest(random.Random(seed), itertools.count(),
                                       **shape)
                covered = shape.get('covered', False)
                check(NestedTree(SimpleTree(forest), covered),
                      list(flatten(forest, covered=covered)))

    def test_navigation(self):
        self.check(self.check_navigation, nesting=1, inner_forests=True,
                   root_subtree=True)
        self.check(self.check_navigation, nesting=3, inner_forests=True,
                   root_subtree=True)
        self.check(self.check_navigation, nesting=3, inner_forests=True,
                   root_subtree=True, empty=True)

    def test_depth(self):
        self.check(self.check_depth, nesting=1, root_subtree=True)
        self.check(self.check_depth, nesting=3, inner_forests=True,
                   root_subtree=True)
        self.check(self.check_depth, nesting=3, inner_forests=True,
                   root_subtree=True, empty=True)

    def test_covered(self):
        for nesting in [1, 3]:
            for shape in [{}, {'inner_forests': True, 'empty': True}]:
                self.check(self.check_navigation, nesting=nesting,
                           root_subtree=True, covered=True, **shape)
                self.check(self.check_depth, nesting=nesting,
                           root_subtree=True, covered=True, **shape)

    # Known bugs, each on the smallest tree that shows it. Once fixed, the
    # random sweep above should be extended to the shape in question.

    def check_fixed(self, forest):
        tree = NestedTree(SimpleTree(forest))
        self.check_navigation(tree, list(flatten(forest)))

    def test_forest_in_forest_subtree(self):
        inner = SimpleTree([(Node('i1'), None), (Node('i2'), None)])
        middle = SimpleTree([(Node('m1'), None), (inner, None)])
        self.check_fixed([(Node('R'), [(middle, None), (Node('b'), None)])])
        self.check_fixed([(Node('R'), [(Node('c'), None), (middle, None)])])

    def test_forest_subtree(self):
        forest = SimpleTree([(Node('a1'), None), (Node('a2'), None)])
        other = SimpleTree([(Node('b'), None)])
        self.check_fixed([(Node('R'), [(forest, None), (other, None)])])

    def test_two_levels(self):
        inner = SimpleTree([(Node('x'), [(Node('y'), None)])])
        middle = SimpleTree([(inner, None)])
        self.check_fixed([(Node('R'), [(middle, None), (Node('c'), None)])])

    def test_root_two_levels(self):
        inner = SimpleTree([(Node('x'), None)])
        self.check_fixed([(SimpleTree([(inner, None)]), None)])

    def test_empty(self):
        tree = NestedTree(SimpleTree([]))
        self.assertIsNone(tree.root)
        self.assertEqual(list(tree.positions()), [])

    def test_empty_subtrees(self):
        empty = SimpleTree([])
        self.check_fixed([(empty, None), (Node('b'), None)])
        self.check_fixed([(Node('R'), [(empty, None)])])
        self.check_fixed([(Node('R'), [(empty, None), (Node('b'), None),
                                       (empty, None)])])
        middle = SimpleTree([(Node('m'), None), (empty, None)])
        self.check_fixed([(Node('R'), [(middle, None), (Node('c'), None)])])
        self.check_fixed([(Node('R'), [(empty, None)] * 5000
                           + [(Node('b'), None)])])


class TestTreeBox(unittest.TestCase):

    def test_down_and_up_walk_dfo(self):
        for seed in SEEDS[:10]:
            with self.subTest(seed=seed):
                forest = random_forest(random.Random(seed), itertools.count())
                positions = list(SimpleTree(forest).positions())
                box = TreeBox(SimpleTree(forest))
                size = (40, 10)
                seen = [box.get_focus()[1]]
                for _ in positions[1:]:
                    box.keypress(size, 'down')
                    seen.append(box.get_focus()[1])
                self.assertEqual(seen, positions)
                for p in reversed(positions[:-1]):
                    box.keypress(size, 'up')
                    self.assertEqual(box.get_focus()[1], p)

    def test_tree_keys_follow_the_tree(self):
        tree = SimpleTree(random_forest(random.Random(0), itertools.count()))
        moves = {
            'left': tree.parent_position,
            'right': tree.first_child_position,
            '[': tree.prev_sibling_position,
            ']': tree.next_sibling_position,
        }
        for p in tree.positions():
            for key, move in moves.items():
                with self.subTest(pos=p, key=key):
                    box = TreeBox(tree, focus=p)
                    box.keypress((40, 10), key)
                    target = move(p)
                    self.assertEqual(box.get_focus()[1],
                                     p if target is None else target)

    def test_empty_tree(self):
        def empty():
            return CollapsibleTree(SimpleTree([]))
        trees = {
            'tree': empty(),
            'nested': NestedTree(empty()),
            'empty subtree at root': NestedTree(SimpleTree([(empty(), None)])),
        }
        for name, tree in trees.items():
            with self.subTest(tree=name):
                box = TreeBox(tree)
                for key in ['right', 'left', '[', ']', '-', '+', 'C', 'E',
                            'down', 'up']:
                    self.assertIn(box.keypress((20, 5), key), (None, key))
                box.focus_last_child()
                box.focus_next()
                box.focus_prev()
                self.assertIsNone(box.get_focus()[0])

