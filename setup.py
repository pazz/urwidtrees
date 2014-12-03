#!/usr/bin/env python

from distutils.core import setup
import urwidtrees


setup(name='urwidtrees',
      version=urwidtrees.__version__,
      description=urwidtrees.__description__,
      author=urwidtrees.__author__,
      author_email=urwidtrees.__author_email__,
      url=urwidtrees.__url__,
      license=urwidtrees.__copyright__,
      packages=['urwidtrees'],
      requires=['urwid (>=1.1.0)'],
      provides='urwidtrees',
     )
