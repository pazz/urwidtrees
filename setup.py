#!/usr/bin/env python
from setuptools import setup


# this loads the version string into __version__
with open('urwidtrees/version.py') as f:
    exec(f.read())

# use the readme as long_description for pypi
with open('README.md') as f:
    readme = f.read()

setup(
    name='urwidtrees',
    version=__version__,
    description="Tree widgets for urwid",
    long_description=readme,
    author="Patrick Totzke",
    author_email="patricktotzke@gmail.com",
    url="https://github.com/pazz/urwidtrees",
    license="Licensed under the GNU GPL v3+.",
    packages=['urwidtrees'],
    install_requires=['urwid>=1.1.0', 'mock'],
    extras_require={
        'docs': [
            'mock',
        ],
    }
)

