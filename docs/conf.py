"""Sphinx configuration for the looper-py handbook.

The handbook is written for the people who use the library: what it can
answer about a firmware, how to ask, and what the answers mean. The pages
are Markdown, read by MyST; the API reference is drawn from the docstrings.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "looper-py"
release = "0.1.0"
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

# looper-core and looper-rs document themselves in builds of their own. These
# are the only places that say where those builds are published; the
# defaults assume all of them are deployed side by side.
CORE_DOCS = os.environ.get("LOOPER_CORE_DOCS", "../looper-core")
RS_DOCS = os.environ.get("LOOPER_RS_DOCS", "../looper-rs")
extlinks = {
    "core": (f"{CORE_DOCS}/%s", "%s"),
    "rs": (f"{RS_DOCS}/%s", "%s"),
}
extlinks_detect_hardcoded_links = True

# Prompts and output are not copied with the code.
copybutton_prompt_text = r"\$ |>>> "
copybutton_prompt_is_regexp = True

html_theme = "furo"
html_title = "looper-py"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
exclude_patterns = ["_build", "draw_figures.py"]
