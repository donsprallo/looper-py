"""The registry directory of this user, where every running looper-srv keeps an entry.

The place and the format are looper-srv's contract (``proto/server_registry.md``):
``%LOCALAPPDATA%/looper/servers`` on Windows, ``$XDG_RUNTIME_DIR/looper/servers``
elsewhere or ``~/.local/state/looper/servers`` without a runtime directory, and
``LOOPER_SERVERS_DIR`` in place of all of them. One ``<instance_id>.json`` per
server, written to a ``.tmp`` and renamed, so a ``.json`` is always whole.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from looper.application.server_list import ServerRegistry
from looper.domain.model.servers import REGISTRY_FORMAT, AnnouncedServer

#: The variable that names another registry directory, as looper-srv reads it.
SERVERS_DIR_VARIABLE = "LOOPER_SERVERS_DIR"


def servers_dir() -> Path:
    """The registry directory of this user, as looper-srv chooses it."""
    named = os.environ.get(SERVERS_DIR_VARIABLE)
    if named:
        return Path(named)
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_RUNTIME_DIR")
    root = Path(base) if base else Path.home() / ".local" / "state"
    return root / "looper" / "servers"


class RegistryDir(ServerRegistry):
    """The entries in one registry directory."""

    def __init__(self, directory: Path | None = None) -> None:
        self._directory = directory if directory is not None else servers_dir()

    def entries(self) -> list[AnnouncedServer]:
        """Every readable entry of the known format; a missing directory has none."""
        if not self._directory.is_dir():
            return []
        found = (_entry_in(path) for path in sorted(self._directory.glob("*.json")))
        return [entry for entry in found if entry is not None]


def _entry_in(path: Path) -> AnnouncedServer | None:
    """The entry in one file, or ``None`` for one that is unreadable or of another format.

    A file can vanish between listing and reading, when its server ends.
    """
    try:
        fields = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(fields, dict) or fields.get("format") != REGISTRY_FORMAT:
        return None
    try:
        return _server_of(fields)
    except (KeyError, TypeError, ValueError):
        return None


def _server_of(fields: dict[str, Any]) -> AnnouncedServer:
    """An entry's fields as a server; a missing required field raises `KeyError`."""
    return AnnouncedServer(
        server_id=str(fields["server_id"]),
        instance_id=str(fields["instance_id"]),
        pid=int(fields["pid"]),
        address=str(fields["address"]),
        listen=str(fields.get("listen", "loopback")),
        tls=bool(fields.get("tls", False)),
        token_required=bool(fields.get("token_required", False)),
        contract_version=int(fields.get("contract_version", 0)),
        server_version=str(fields.get("server_version", "")),
        started_at_unix_ms=int(fields["started_at_unix_ms"]),
        started_by=str(fields.get("started_by", "")),
        owner_pid=int(fields.get("owner_pid", 0)),
        mode=str(fields.get("mode", "")),
        firmware_name=str(fields.get("firmware_name", "")),
        definition_path=str(fields.get("definition_path", "")),
    )
