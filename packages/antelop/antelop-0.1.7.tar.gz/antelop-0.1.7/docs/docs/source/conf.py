# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "Antelop"
copyright = "2023, Rory Bedford"
author = "Rory Bedford"

release = "0.1"
version = "0.1.0"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_tabs.tabs",
    "sphinx_design",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"
html_logo = "images/logo.png"

# -- Options for EPUB output
epub_show_urls = "footnote"

html_theme_options = {
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'version_selector': True,
    'language_selector': True,
}

html_static_path = ['_static']

def setup(app):
    app.add_css_file('custom.css')  # Add your custom CSS

