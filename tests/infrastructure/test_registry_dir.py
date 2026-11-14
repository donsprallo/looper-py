"""Reading the registry directory looper-srv writes, and telling its servers from gone ones.

The entries here are written as looper-srv writes them; this process stands
in for a running server, so that its pid runs and its start is real.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

import looper
from looper.infrastructure.process_table import OsProcessTable
from looper.infrastructure.registry_dir import RegistryDir, servers_dir


def entry(**changed: object) -> dict[str, object]:
    """An entry with every field, as in looper-srv's server_registry.example.json."""
    fields: dict[str, object] = {
        "format": 1,
        "server_id": "srv-2b7c19e04a5d8f31",
        "instance_id": "a3f9c2e1",
        "pid": os.getpid(),
        "address": "127.0.0.1:52341",
        "listen": "loopback",
        "tls": False,
        "token_required": False,
        "contract_version": 3,
        "server_version": "0.1.0",
        "started_at_unix_ms": int(time.time() * 1000),
        "started_by": "window",
        "owner_pid": 5678,
        "mode": "simulation",
        "firmware_name": "blinky",
        "definition_path": "C:\\work\\blinky\\looper.toml",
    }
    fields.update(changed)
    return fields


def write(directory: Path, name: str, fields: object) -> None:
    (directory / name).write_text(json.dumps(fields), encoding="utf-8")


def test_an_entry_is_read_with_every_field(tmp_path: Path) -> None:
    write(tmp_path, "a3f9c2e1.json", entry())

    [server] = RegistryDir(tmp_path).entries()

    assert (server.address, server.mode, server.owner_pid) == (
        "127.0.0.1:52341",
        "simulation",
        5678,
    )
    assert server.definition_path == "C:\\work\\blinky\\looper.toml"


def test_half_written_broken_and_foreign_entries_are_skipped(tmp_path: Path) -> None:
    write(tmp_path, "half.json.tmp", entry())
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")
    write(tmp_path, "future.json", entry(format=2))
    write(tmp_path, "list.json", [1, 2])
    write(tmp_path, "short.json", {"format": 1, "pid": 1})

    assert RegistryDir(tmp_path).entries() == []


def test_a_missing_directory_has_no_entries(tmp_path: Path) -> None:
    assert RegistryDir(tmp_path / "nothing").entries() == []


def test_the_directory_is_the_one_the_variable_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOOPER_SERVERS_DIR", str(tmp_path))

    assert servers_dir() == tmp_path


def test_this_process_started_before_now_and_a_pid_of_none_runs_nothing() -> None:
    started = OsProcessTable().started_at_unix_ms(os.getpid())

    assert started is not None
    assert started <= int(time.time() * 1000)
    assert OsProcessTable().started_at_unix_ms(0) is None


def test_servers_lists_a_running_one_and_leaves_out_a_reused_pid(tmp_path: Path) -> None:
    write(tmp_path, "live.json", entry(instance_id="live"))
    write(tmp_path, "reused.json", entry(instance_id="reused", started_at_unix_ms=1_000))

    assert [server.instance_id for server in looper.servers(tmp_path)] == ["live"]


def test_a_found_server_that_wants_tls_is_not_dialled(tmp_path: Path) -> None:
    write(tmp_path, "tls.json", entry(tls=True))
    [server] = looper.servers(tmp_path)

    with pytest.raises(ValueError, match="TLS or a token"):
        looper.connect(server)
