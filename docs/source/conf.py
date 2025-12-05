# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import sys
from pathlib import Path
from time import strftime, localtime
sys.path.insert(0, str(Path(__file__).resolve().parents[2]) + "/scripts")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Open Knowledge Explorer'
copyright = f'{int(strftime("%Y", localtime()))}, Research Centre BioBased Economy (Hanze University of Applied Sciences)'
author = 'Jennefer Beenen, Wynand Alkema'
release = '0.1'


# Make sure it prints time in English:
nl_to_en = {
    'januari' : 'January',
    'februari' : 'February',
    'maart' : 'March',
    'april' : 'April',
    'mei' : 'May',
    'juni' : 'June',
    'juli' : 'July',
    'augustus' : 'August',
    'september' : 'September',
    'oktober' : 'October',
    'november' : 'November',
    'december' : 'December',
}

t = strftime("%d %B %Y", localtime())
if t.split(' ')[1] in nl_to_en.keys():
    t = ' '.join([t.split(' ')[0], nl_to_en.get(t.split(' ')[1]), t.split(' ')[2]])
version = t

# Logo
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_theme_options = {
    "logo_only": True,
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    # 'sphinx.ext.viewcode', # Add an 'source' button next to functions and redirects to a page where the code can be viewed.
    'sphinx_copybutton', # Add a button to copy code.
    'sphinx_rtd_theme', # Add esthetics to the HTML.
    'sphinx.ext.autodoc', # Include documentation from docstrings
    'sphinx.ext.duration', # Measure durations of Sphinx processing
    'sphinxemoji.sphinxemoji', # Makes it possible to add emoji's: https://sphinxemojicodes.readthedocs.io/en/stable/
    'sphinx_mdinclude', # Parse Markdown files to a RST file.
    "sphinx_design", # Create dropdown windows. I use this in FAQ section in `background.rst`
    'sphinx.ext.napoleon', # Parse docstrings in Google style.
    'sphinx.ext.doctest', # Test snippets in the documentation.
    'sphinx.ext.autosummary' # Generate autodoc summaries.
]

# If you want a consistent emoji style instead of using the browser's default, you can set it in your conf.py file:
sphinxemoji_style = 'twemoji'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Consider one of the following themes:
# 1) Git book theme (https://sphinx-themes.org/sample-sites/sphinx-book-theme/)
# `pip install sphinx-book-theme`
# html_theme = 'sphinx_book_theme'

# 2) Awesome theme (https://sphinx-themes.org/sample-sites/sphinxawesome-theme/)
# `pip install sphinxawesome-theme`
# html_permalinks_icon = '<span>#</span>'
# html_theme = 'sphinxawesome_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_permalinks = False

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

source_suffix = {
    '.rst': 'restructuredtext',
    #'.txt': 'restructuredtext',
    '.sh': 'restructuredtext',
    '.md': 'markdown',
}
