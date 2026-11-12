"""Sphinx configuration for the looper-py handbook.

The handbook is written for the people who use the library: what it can
answer about a firmware, how to ask, and what the answers mean. The pages
are Markdown, read by MyST; the API reference is drawn from the docstrings.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from docutils import nodes
from sphinx.application import Sphinx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "looper-py"
release = "0.3.0"
language = "en"

# No attribution in the footer: the build carries no author or copyright.
html_show_copyright = False

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.mermaid",
    "sphinx_design",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]
# Let cross document links point at a heading.
myst_heading_anchors = 3

autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
# The "Attributes:" of a dataclass become a field list of its class, rather
# than entries of their own beside the ones autodoc writes for the fields.
napoleon_use_ivar = True
typehints_use_signature_return = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# looper-gui documents itself in a build of its own. These
# are the only places that say where those builds are published; the
# defaults assume all of them are deployed side by side.
RS_DOCS = os.environ.get("LOOPER_GUI_DOCS", "../looper-gui")
# The tutorial, the installation of the whole system, the first test, the
# licence and the manual of what a simulation is are written once, in looper-docs.
LEARN_DOCS = os.environ.get("LOOPER_LEARN_DOCS", "../looper-docs")
extlinks = {
    "rs": (f"{RS_DOCS}/%s", "%s"),
    "learn": (f"{LEARN_DOCS}/%s", "%s"),
}
extlinks_detect_hardcoded_links = True


# The defaults above are relative to the root of this handbook, where the
# builds sit side by side. A link is written into a page, though, and from a
# page one folder down it takes one more "../" to reach the same neighbour.
# An absolute URL, as a deployment sets through the variables, is left alone.
RELATIVE_HANDBOOKS = tuple(
    base.removesuffix("%s")
    for base, _caption in extlinks.values()
    if "://" not in base and not base.startswith("/")
)


def _relative_to_page(_app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Prefix each link to a neighbouring handbook with one ``../`` per folder."""
    prefix = "../" * docname.count("/")
    if not prefix:
        return
    for reference in doctree.findall(nodes.reference):
        uri = reference.get("refuri", "")
        if uri.startswith(RELATIVE_HANDBOOKS):
            reference["refuri"] = prefix + uri


def setup(app: Sphinx) -> None:
    """Correct the links once every link of a page is resolved."""
    app.connect("doctree-resolved", _relative_to_page)


# Prompts and output are not copied with the code.
copybutton_prompt_text = r"\$ |>>> "
copybutton_prompt_is_regexp = True

html_theme = "furo"
html_title = "looper-py"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
exclude_patterns = ["_build", "draw_figures.py"]
