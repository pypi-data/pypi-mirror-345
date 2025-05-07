"""Configuration file for the Sphinx documentation builder."""

# -- Project information -----------------------------------------------------
import simpipe

project = "simpipe"
copyright = "CTAO, SimPipe developers"  # noqa A001
author = "Gernot Maier"
version = simpipe.__version__
# The full version, including alpha/beta/rc tags.
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_changelog",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["changes"]

# have all links automatically associated with the right domain.
default_role = "py:obj"


# intersphinx allows referencing other packages sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "ctao"

html_theme_options = {
    "navigation_with_keys": False,
    # setup for displaying multiple versions, also see setup in .gitlab-ci.yml
    "switcher": {
        "json_url": "http://cta-computing.gitlab-pages.cta-observatory.org/dpps/simpipe/simpipe/versions.json",
        "version_match": "latest" if ".dev" in version else f"v{version}",
    },
    "navbar_center": ["version-switcher", "navbar-nav"],
    "gitlab_url": "https://gitlab.cta-observatory.org/cta-computing/dpps/simpipe/simpipe",
    "logo": {
        "image_light": "_static/cta.png",
        "image_dark": "_static/cta_dark.png",
        "alt_text": "ctao-logo",
        "text": " | sim<b>pipe</b>",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
