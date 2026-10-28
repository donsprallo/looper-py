"""The dependency rules, read from the imports.

The domain imports the standard library and itself. The application adds
the domain. Neither knows gRPC or the infrastructure, and nothing anywhere
imports looper-core: the boundary to it is a process.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "looper"


def imports_of(path: Path) -> set[str]:
    """Every module a file imports, by its full name."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.add(node.module)
    return found


def sources_of(layer: str) -> list[Path]:
    """The Python files of one layer."""
    return sorted((PACKAGE / layer).rglob("*.py"))


@pytest.mark.parametrize("path", sources_of("domain"), ids=lambda path: path.name)
def test_the_domain_reaches_for_nothing_outside_itself(path: Path) -> None:
    outside = {
        name
        for name in imports_of(path)
        if name.startswith("looper") and not name.startswith("looper.domain")
    }
    assert not outside, f"{path.name} imports {sorted(outside)}"
    assert not {name for name in imports_of(path) if name.split(".")[0] in {"grpc", "google"}}


@pytest.mark.parametrize("path", sources_of("application"), ids=lambda path: path.name)
def test_the_application_knows_neither_grpc_nor_the_infrastructure(path: Path) -> None:
    forbidden = {
        name
        for name in imports_of(path)
        if name.split(".")[0] in {"grpc", "google"} or name.startswith("looper.infrastructure")
    }
    assert not forbidden, f"{path.name} imports {sorted(forbidden)}"


@pytest.mark.parametrize("path", sorted(PACKAGE.rglob("*.py")), ids=lambda path: path.name)
def test_nothing_imports_looper_core(path: Path) -> None:
    assert not {name for name in imports_of(path) if name.startswith("looper_core")}
