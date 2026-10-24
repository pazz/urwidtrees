import urwid

from urwidtrees import SimpleTree


class Node(urwid.Text):
    """selectable Text, so that a ListBox can move its focus onto it"""
    _selectable = True

    def keypress(self, size, key):
        return key


def small_tree():
    """
    r
    +-- a
    |   +-- a1
    |   +-- a2
    +-- b
    """
    return SimpleTree([
        (Node('r'), [
            (Node('a'), [(Node('a1'), None), (Node('a2'), None)]),
            (Node('b'), None),
        ]),
    ])


def render(widget, *size):
    return [line.decode() for line in widget.render(size).text]


def render_tree(tree, width=16):
    """first rendered line of every decorated position, in DFO"""
    return [render(tree.get_decorated(pos), width)[0].rstrip()
            for pos in tree.positions()]
