#!/usr/bin/env python
from distutils.core import setup

import urwidtrees

setup(
    name='urwidtrees',
    version=urwidtrees.__version__,
    description="Tree widgets for urwid",
    author="Patrick Totzke",
    author_email="patricktotzke@gmail.com",
    url="https://github.com/pazz/urwidtrees",
    license="Licensed under the GNU GPL v3+.",
    packages=['urwidtrees'],
    install_requires=['urwid>=1.1.0', 'mock'],
    extra_require={
        'docs': [
            'mock',
        ],
    },
)
