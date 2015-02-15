Urwidtrees
==========

.. module:: urwidtrees

This is a Widget Container API for the :mod:`urwid` toolkit.
It uses a MVC approach and allows to build trees of widgets.
Its design goals are

* clear separation classes that define, decorate and display trees of widgets
* representation of trees by local operations on node positions
* easy to use default implementation for simple trees
* Collapses are considered decoration

Generally, tree structures are defined by subclassing :class:`~urwidtrees.tree.Tree` and
overwriting local position movements. For most purposes however, using a
:class:`~urwidtrees.tree.SimpleTree` will do.
The choice to define trees by overwriting local position movements allows to
easily define potentially infinite tree structures. See `example4` for how to
walk local file systems.

Trees of widgets are rendered by :class:`~urwidtrees.tree.TreeBox` widgets.
These are based on urwids :class:`~urwid.ListBox` widget and
display trees such that siblings grow vertically and children horizontally.
TreeBoxes handle key presses to move in the tree and collapse/expand subtrees if possible.

.. toctree::
   :maxdepth: 1

   structure
   containers
   decoration
   examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
