"""Finding a running looper-srv through its registry entry, and attaching to it.

The test points ``LOOPER_SERVERS_DIR`` at a directory of its own, which the
server it starts inherits, so that the entry is the only one there and does
not show in a person's list. While the server runs it is found as started by
this test; a second client attaches to it through what was found; once it
ends its entry is gone.

Needs a looper-docs checkout beside this one and a C compiler, and skips without them.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"


@pytest.fixture
def registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A registry directory of this test's own, for the server it starts."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    monkeypatch.setenv("LOOPER_SERVERS_DIR", str(tmp_path))
    return tmp_path


def test_a_running_server_is_found_attached_to_and_gone_once_it_ends(registry: Path) -> None:
    with looper.run(DEFINITION, virtual=True, server=server_command()):
        [server] = looper.servers()

        assert (server.started_by, server.owner_pid) == ("test", os.getpid())
        assert server.mode == "simulation"
        assert Path(server.definition_path).name == "looper.toml"
        with looper.connect(server) as second:
            assert second.description.contract_version == server.contract_version

    assert looper.servers(registry) == []
