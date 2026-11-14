"""The servers that run are the registry's entries without those of servers gone."""

from __future__ import annotations

from dataclasses import replace

from looper.application.server_list import ProcessTable, ServerRegistry, running_servers
from looper.domain.model.servers import AnnouncedServer

STARTED = 1_762_767_733_000

SERVER = AnnouncedServer(
    server_id="srv-1",
    instance_id="a",
    pid=10,
    address="127.0.0.1:50051",
    listen="loopback",
    tls=False,
    token_required=False,
    contract_version=3,
    server_version="0.1.0",
    started_at_unix_ms=STARTED,
    started_by="test",
    owner_pid=0,
    mode="simulation",
    firmware_name="blinky",
    definition_path="blinky/looper.toml",
)


class Entries(ServerRegistry):
    def __init__(self, *servers: AnnouncedServer) -> None:
        self._servers = list(servers)

    def entries(self) -> list[AnnouncedServer]:
        return self._servers


class Processes(ProcessTable):
    def __init__(self, started: dict[int, int]) -> None:
        self._started = started

    def started_at_unix_ms(self, pid: int) -> int | None:
        return self._started.get(pid)


def test_an_entry_whose_pid_runs_no_process_is_left_out() -> None:
    assert running_servers(Entries(SERVER), Processes({})) == []


def test_an_entry_whose_pid_was_taken_by_a_later_process_is_left_out() -> None:
    later = Processes({SERVER.pid: STARTED + 2_001})

    assert running_servers(Entries(SERVER), later) == []


def test_a_process_started_just_before_its_entry_is_the_server() -> None:
    assert running_servers(Entries(SERVER), Processes({SERVER.pid: STARTED - 300})) == [SERVER]


def test_the_most_recently_started_server_comes_first() -> None:
    newer = replace(SERVER, instance_id="b", pid=11, started_at_unix_ms=STARTED + 60_000)
    processes = Processes({10: STARTED, 11: STARTED + 60_000})

    assert running_servers(Entries(SERVER, newer), processes) == [newer, SERVER]


def test_a_server_that_wants_tls_or_a_token_is_not_reachable_without_credentials() -> None:
    assert SERVER.reachable_without_credentials
    assert not replace(SERVER, tls=True).reachable_without_credentials
    assert not replace(SERVER, token_required=True).reachable_without_credentials
