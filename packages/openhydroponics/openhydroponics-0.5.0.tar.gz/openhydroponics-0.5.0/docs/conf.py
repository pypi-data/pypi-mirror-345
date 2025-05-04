# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OpenHydroponics"
copyright = '2024, Micke Prag'
author = 'Micke Prag'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "jupyter_sphinx",
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx.ext.graphviz",
    "sphinx_click",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

add_module_names = True
modindex_common_prefix = ["openhydroponics"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_context = {}
html_theme = "sphinx_material"
html_static_path = ['_static']
html_title = "Start"

html_theme_options = {
    "repo_url": "https://gitlab.com/openhydroponics/sw/openhydroponics",
    "repo_type": "gitlab",
    "repo_name": "OpenHydroponics GitLab",
    "html_minify": True,
    "css_minify": True,
    "nav_title": "OpenHydroponics",
    "globaltoc_depth": 3,
    "globaltoc_collapse": False,
    "nav_links": [
        {
            "href": "https://lectronz.com/stores/mickeprag",
            "internal": False,
            "title": "Store",
        },
    ],
}

html_sidebars = {
    "**": [
        "globaltoc.html",
        "localtoc.html",
        "searchbox.html",
    ]
}
