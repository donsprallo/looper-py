"""A looper-srv that announced itself on this PC, as its registry entry says.

The entry is an announcement only (looper-srv's ``proto/server_registry.md``):
every text a list shows comes from ``Describe``. What the entry is good for
is finding a server before asking it anything, and telling a server that
still runs from the file of one that was killed.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The one format of registry entry this library reads; others are skipped.
REGISTRY_FORMAT = 1
#: How much later than its entry's start a process may have started and still be that server.
#: A pid used again belongs to a process that started after the server did.
START_TOLERANCE_MS = 2000


@dataclass(frozen=True)
class AnnouncedServer:
    """One running looper-srv, by its registry entry."""

    server_id: str
    instance_id: str
    pid: int
    address: str
    listen: str
    tls: bool
    token_required: bool
    contract_version: int
    server_version: str
    started_at_unix_ms: int
    started_by: str
    owner_pid: int
    mode: str
    firmware_name: str
    definition_path: str

    def is_announced_by(self, process_started_at_unix_ms: int | None) -> bool:
        """Whether a process that started then is the server that wrote this entry.

        ``None`` means no process runs under the pid. A process that started
        well after the entry's server is another one that took the pid.
        """
        if process_started_at_unix_ms is None:
            return False
        return process_started_at_unix_ms <= self.started_at_unix_ms + START_TOLERANCE_MS

    @property
    def reachable_without_credentials(self) -> bool:
        """Whether this library can dial it: plain gRPC and no token."""
        return not self.tls and not self.token_required
