# urwidtrees documentation build configuration file

import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

# build the API docs without urwid installed, as on readthedocs.org
autodoc_mock_imports = ['urwid']

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

project = 'urwidtrees'
author = copyright = 'Patrick Totzke'

namespace = {}
with open('../../urwidtrees/version.py') as f:
    exec(f.read(), namespace)
version = release = namespace['__version__']

pygments_style = 'sphinx'

html_theme = 'default'

intersphinx_mapping = {
    'urwid': ('https://urwid.readthedocs.io/en/latest/', None)
}
