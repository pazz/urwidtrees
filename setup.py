#!/usr/bin/env python
from distutils.core import setup


__productname__ = 'urwidtrees'
__version__ = '1.0.2k1'
__copyright__ = "Copyright (C) 2015 Patrick Totzke"
__author__ = "Patrick Totzke"
__author_email__ = "patricktotzke@gmail.com"
__description__ = "Tree widgets for urwid"
__url__ = "https://github.com/pazz/urwidtrees"
__license__ = "Licensed under the GNU GPL v3+."


setup(
    name='urwidtrees',
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__copyright__,
    packages=['urwidtrees'],
    install_requires=['urwid>=1.1.0'],
)
