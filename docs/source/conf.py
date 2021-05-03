# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

import django

sys.path.insert(0, os.path.abspath('../..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thenewboston_node.project.settings')
django.setup()

# -- Project information -----------------------------------------------------

project = 'thenewboston-node'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.restbuilder',
]

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# -- Options for autodoc -----------------------------------------------------

autodoc_member_order = 'bysource'

autodoc_typehints = 'description'

autodoc_default_options = {
    'members': True,
}
