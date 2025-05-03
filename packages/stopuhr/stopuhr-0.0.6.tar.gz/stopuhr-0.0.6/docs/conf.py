"""Configuration file for the Sphinx documentation builder."""

import os
import sys

sys.path.insert(0, os.path.abspath("../"))

from stopuhr import __version__

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "stopuhr"
copyright = "2025, Tobias Hoelzer"
author = "Tobias Hoelzer"
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_gallery.load_style",
    "sphinx_gallery.gen_gallery",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Sphinx-Gallery configuration
sphinx_gallery_conf = {
    "examples_dirs": ["../examples"],  # Path to your examples folder
    "gallery_dirs": ["auto_examples"],  # Where to save gallery files
    "backreferences_dir": "gen_modules/backreferences",
    "reference_url": {"sphinx-gallery": None},
    "plot_gallery": "True",
    "min_reported_time": 100,  # Time threshold for slow examples
    "filename_pattern": r"\.py",
}

numpydoc_show_class_members = False
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_theme_options = {
    "logo": {
        "text": "stopuhr",
        "image_light": "_static/images/stopuhr-logo.png",
        "image_dark": "_static/images/stopuhr-logo.png",
    },
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": "https://github.com/relativityhd/stopuhr",  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }
    ],
    "icon_links_label": "Quick Links",
}
