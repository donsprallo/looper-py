"""Which looper-srv run on this PC: the registry's entries, without those of servers gone.

A server killed without ending leaves its entry behind; the contract says a
client skips it and never deletes it. Whether the pid still runs, and since
when, is the operating system's, behind `ProcessTable`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.servers import AnnouncedServer


class ServerRegistry(ABC):
    """Where running servers announce themselves."""

    @abstractmethod
    def entries(self) -> list[AnnouncedServer]:
        """Every entry of a format this library reads, stale ones included."""


class ProcessTable(ABC):
    """The processes of this PC, as far as telling a server from a reused pid needs."""

    @abstractmethod
    def started_at_unix_ms(self, pid: int) -> int | None:
        """When the process started, or ``None`` when none runs under the pid."""


def running_servers(registry: ServerRegistry, processes: ProcessTable) -> list[AnnouncedServer]:
    """The servers that still run, the most recently started first."""
    running = [
        server
        for server in registry.entries()
        if server.is_announced_by(processes.started_at_unix_ms(server.pid))
    ]
    return sorted(running, key=lambda server: server.started_at_unix_ms, reverse=True)
