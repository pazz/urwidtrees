Containers
----------

.. module:: urwidtrees.widgets

:class:`TreeBox` is essentially a :class:`urwid.ListBox` that displays a given :class:`~urwidtrees.tree.Tree`.
Per default no decoration is used and the widgets of the tree are simply displayed line by line in
depth first order. :class:`TreeBox`'s constructor accepts a `focus` parameter to specify the initially
focussed position. Internally, it uses a :class:`TreeListWalker` to linearize the tree to a list.

:class:`TreeListWalker` serve as adapter between :class:`~urwidtrees.tree.Tree` and :class:`urwid.ListWalker` APIs:
They implement the ListWalker API using the data from a given `Tree` in depth-first order.
As such, one can directly pass on a :class:`TreeListWalker` to an :class:`urwid.ListBox` if one doesn't want
to use tree-based focus movement or key bindings for collapsing subtrees.

API
===

.. autoclass:: urwidtrees.widgets.TreeBox
  :members:

.. autoclass:: urwidtrees.widgets.TreeListWalker
  :members:
