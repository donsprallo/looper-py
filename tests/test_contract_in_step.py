"""The copy of the contract this library builds against is the one looper-core serves.

The schema here is a copy, because this library must not import looper-core.
A copy can fall behind, and a field that moved on one side only is not an
import error but a value read into the wrong field. So when a looper-core
checkout sits beside this one, the two files have to be identical.

Without a neighbouring checkout there is nothing to compare against, and the
test says so rather than failing. Point ``LOOPER_CORE`` at a checkout
elsewhere to compare against that one.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OURS = PROJECT_ROOT / "src" / "looper" / "infrastructure" / "contract" / "looper_inspector.proto"
SCHEMA_IN_CORE = Path("src/looper_core/presentation/inspector/schema/looper_inspector.proto")


def core_checkout() -> Path:
    """Where looper-core is checked out."""
    return Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))


def normalised(path: Path) -> str:
    """A file's text with its line endings made the same."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_the_schema_is_the_one_looper_core_serves() -> None:
    served = core_checkout() / SCHEMA_IN_CORE
    if not served.exists():
        pytest.skip(f"no looper-core checkout at {served}")

    assert normalised(OURS) == normalised(served), (
        f"{OURS.name} differs from {served}; copy it over and run scripts/generate_contract.py"
    )
