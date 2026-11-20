"""Starting a bench's leader as a child, without looper-srv (#9).

A stand-in written in Python plays the leader of `run --bench`: it prints
the host's process and every member's address before its own, then waits
for its standard input to close; or it refuses the bench the way the free
download does, with a sentence on its error stream and exit code 3.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from looper import BenchProLockedError, ProFeatureLockedError, ServerStartError
from looper.infrastructure.bench_run import BenchAddresses, BenchCommand, BenchRun

STAND_IN = """
import sys
if sys.argv[1] == "free":
    print("looper-srv: Bench is part of looper Pro - this is the free download.", file=sys.stderr)
    sys.exit(3)
if sys.argv[1] == "unfit":
    print("looper-srv: The bench lab could not be set up: gateway has no CAN bus CAN2.",
          file=sys.stderr)
    sys.exit(1)
print("bench host pid=4242", flush=True)
print("bench member=gateway listening on 127.0.0.1:50124", flush=True)
print("listening on 127.0.0.1:50123", flush=True)
sys.stdin.read()
sys.exit(0)
"""


@pytest.fixture
def stand_in(tmp_path: Path) -> Path:
    script = tmp_path / "bench_leader_stand_in.py"
    script.write_text(STAND_IN)
    return script


def a_command(script: Path, behaviour: str) -> BenchCommand:
    return BenchCommand(program=(sys.executable, str(script), behaviour), bench_file=Path("b.toml"))


def test_the_leader_is_started_on_the_bench_file_and_told_a_test_started_it() -> None:
    command = BenchCommand(program=("looper-srv",), bench_file=Path("bench.toml"), build=False)
    arguments = command.arguments()

    assert arguments[:4] == ["looper-srv", "run", "--bench", "bench.toml"]
    assert arguments[arguments.index("--listen") + 1] == "127.0.0.1:0"
    assert "--stop-on-stdin-close" in arguments
    assert "--no-build" in arguments
    assert arguments[arguments.index("--owner-pid") + 1] == str(os.getpid())


def test_the_lines_name_the_host_every_member_and_end_with_the_leader() -> None:
    addresses = BenchAddresses()
    lines = [
        "bench host pid=4242\n",
        "bench member=gateway listening on 127.0.0.1:50124\n",
        "listening on 127.0.0.1:50123\n",
    ]

    assert [addresses.take(line) for line in lines] == [False, False, True]
    assert (addresses.host_pid, addresses.members, addresses.leader) == (
        4242,
        {"gateway": "127.0.0.1:50124"},
        "127.0.0.1:50123",
    )


def test_a_started_bench_says_where_each_server_listens_and_stops(stand_in: Path) -> None:
    started = BenchRun.start(a_command(stand_in, "serves"))

    assert started.leader_address == "127.0.0.1:50123"
    assert started.member_addresses == {"gateway": "127.0.0.1:50124"}
    assert started.host_pid == 4242
    assert started.stop() == 0


def test_the_free_download_s_refusal_carries_its_sentence(stand_in: Path) -> None:
    with pytest.raises(BenchProLockedError) as locked:
        BenchRun.start(a_command(stand_in, "free"))

    assert str(locked.value) == "Bench is part of looper Pro - this is the free download."
    assert isinstance(locked.value, ProFeatureLockedError)
    assert isinstance(locked.value, ServerStartError)


def test_a_bench_that_does_not_fit_is_a_start_error_with_the_server_s_sentence(
    stand_in: Path,
) -> None:
    with pytest.raises(ServerStartError, match="gateway has no CAN bus CAN2") as failed:
        BenchRun.start(a_command(stand_in, "unfit"))

    assert not isinstance(failed.value, ProFeatureLockedError)
