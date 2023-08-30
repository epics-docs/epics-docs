# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'EPICS Documentation'
copyright = '2019, EPICS Controls.'
author = 'EPICS'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'hoverxref.extension',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    "sphinx_reredirects",
    # Markdown parser
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.*']

# Intersphinx links to subprojects
intersphinx_mapping = {
    'how-tos': ('https://docs.epics-controls.org/projects/how-tos/en/latest', None),
}
hoverxref_intersphinx = [
    'how-tos',
]
hoverxref_intersphinx_types = {
    'how-tos': 'modal',
}

# Enabled Markdown extensions.
# See here for what they do:
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "tasklist",
]

# Allows auto-generated header anchors:
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#auto-generated-header-anchors
myst_heading_anchors = 4


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

master_doc = 'index'

html_theme_options = {
    'logo_only': True,
}
html_logo = "images/EPICS_white_logo_v02.png"


# -- Redirections specifications ---------------------------------------------

# Specify redirections from the <docs.epics-controls.org> architecture
# (before 08/2023 EPICS documentathon), to the new <docs.epics-controls.org>
# (after 08/2023 EPICS documentathon).
# Also see https://documatt.gitlab.io/sphinx-reredirects/usage.html
redirects = {
    "guides/EPICS_Intro": "../getting-started/EPICS_Intro.html",
    
    "guides/EPICS_Process_Database_Concepts":
        "../process-database/EPICS_Process_Database_Concepts.html",
    
    "specs/specs":
        "../index.html",
    
    "specs/ca_protocol":
        "../internal/ca_protocol.html",
    
    "specs/Normative-Types-Specification":
        "../pv-access/Normative-Types-Specification.html",
    
    "specs/IOCInit":
        "../internal/IOCInit.html",
    
    "appdevguide/EPICSBuildFacility":
        "../build-system/specifications.html",

    "specs/EPICSBuildFacility":
        "../build-system/specifications.html",
    
    "software/base":
        "../index.html",
    
    "software/HowToWorkWithTheEpicsRepository":
        "../contributing/HowToWorkWithTheEpicsRepository.html",
    
    #"appdevguide/*": "appdevguide/*",
    
    "software/modules":
        "../index.html",
}
