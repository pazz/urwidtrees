Structure
---------

.. module:: urwidtrees.tree

:class:`Tree` objects define a tree structure by implementing the local movement methods

    * :meth:`~Tree.parent_position`
    * :meth:`~Tree.first_child_position`
    * :meth:`~Tree.last_child_position`
    * :meth:`~Tree.next_sibling_position`
    * :meth:`~Tree.prev_sibling_position`

Each of which takes and returns a `position` object of arbitrary type (fixed for the Tree)
as done in urwids ListWalker API. Apart from this, a Tree is assumed to define a dedicated
position `tree.root` that is used as fallback initially focussed element,
and define the :meth:`__getitem__` method to return its content (usually a Widget) for a given position.

Note that :class:`Tree` only defines a tree structure, it does not necessarily have any decoration around
its contained Widgets.

There is a ready made subclass called :class:`SimpleTree` that offers the tree API for a given 
nested tuple structure. If you write your own classes its a good idea to subclass :class:`Tree`
and just overwrite the above mentioned methods as the base class already offers a number of
derivative methods.


API
===

.. autoclass:: urwidtrees.tree.Tree
   :members:


.. autoclass:: urwidtrees.tree.SimpleTree
   :members:
