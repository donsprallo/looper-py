"""The copy of the contract this library builds against is the original in looper-srv.

The schema here is a copy, because this library must not import a server.
A copy can fall behind, and a field that moved on one side only is not an
import error but a value read into the wrong field. So when a looper-srv
checkout sits beside this one, the two files have to be identical. looper-srv
owns the contract since step 1.4 of its plan; looper-core keeps a checked copy
of its own.

Without a neighbouring checkout there is nothing to compare against, and the
test says so rather than failing. Point ``LOOPER_SRV`` at a checkout
elsewhere to compare against that one.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OURS = PROJECT_ROOT / "src" / "looper" / "infrastructure" / "contract" / "looper_inspector.proto"
SCHEMA_IN_SRV = Path("proto/looper_inspector.proto")


def srv_checkout() -> Path:
    """Where looper-srv is checked out."""
    return Path(os.environ.get("LOOPER_SRV", PROJECT_ROOT.parent / "looper-srv"))


def normalised(path: Path) -> str:
    """A file's text with its line endings made the same."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_the_schema_is_the_original_in_looper_srv() -> None:
    original = srv_checkout() / SCHEMA_IN_SRV
    if not original.exists():
        pytest.skip(f"no looper-srv checkout at {original}")

    assert normalised(OURS) == normalised(original), (
        f"{OURS.name} differs from {original}; copy it over and run scripts/generate_contract.py"
    )
