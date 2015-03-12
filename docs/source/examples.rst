Examples
--------

Minimal example
===============

Simplest example rendering::

      [-] item 1
              sub item 1
              sub item 2
          item 2

.. literalinclude:: ../examples/example0.py
   :language: python
   :linenos:


Basic use
=========

.. literalinclude:: ../examples/example1.py
   :language: python
   :linenos:


Decoration
==========

.. literalinclude:: ../examples/example2.arrows.py
   :language: python
   :linenos:


Collapsible subtrees
====================

.. literalinclude:: ../examples/example3.collapse.py
   :language: python
   :linenos:


Custom Trees: Walking the filesystem
====================================

.. literalinclude:: ../examples/example4.filesystem.py
   :language: python
   :linenos:


Nesting Trees
==============

.. literalinclude:: ../examples/example5.nested.py
   :language: python
   :linenos:


Dynamic List
============

Update the tree after it's initially build.

Shows something like::

    root
    ├─➤PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
    │  64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.039 ms
    │
    ├─➤64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.053 ms
    │
    └─➤64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.064 ms

.. literalinclude:: ../examples/example6.append.py
   :language: python
   :linenos:
