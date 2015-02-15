Decoration
----------

.. module:: urwidtrees.decoration

Is done by using (subclasses of) :class:`DecoratedTree`. Objects of this type
wrap around a given `Tree` and themselves behave like a (possibly altered) tree.
Per default, `DecoratedTree` just passes every method on to its underlying tree.
Decoration is done *not* by overwriting `__getitem__`, but by offering two additional
methods

  * :meth:`DecoratedTree.get_decorated`
  * :meth:`DecoratedTree.decorate`.

`get_decorated(pos)` returns the (decorated) content of the original tree at the given position.
`decorate(pos, widget,..)` decorates the given widget assuming its placed at a given position.
The former is trivially based on the latter, Containers that display `Tree`'s use `get_decorated`
instead of :meth:`__getitem__` when working on `DecoratedTree`'s.

The reason for this slightly odd design choice is that first it makes it easy to read
the original content of a decorated tree: You simply use `dtree[pos]`.
Secondly, this makes it possible to recursively add line decoration when nesting (decorated) Trees.

The module `decoration` offers a few readily usable :class:`DecoratedTree` subclasses that implement
decoration by indentation, arrow shapes and subtree collapsing:
:class:`CollapsibleTree`,
:class:`IndentedTree`,
:class:`CollapsibleIndentedTree`,
:class:`ArrowTree` and
:class:`CollapsibleArrowTree`.
Each can be further customized by constructor parameters.


API
===

.. automodule:: urwidtrees.decoration
   :members:

