"""Starting looper-cli as a child, without looper-cli.

A stand-in written in Python plays looper-cli: it prints what looper-cli
prints and then waits for its standard input to close, or ends straight
away. What is pinned down is the part a test relies on: the command line,
the address read from the right line, and a stop that really stops.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from looper import LooperCliError
from looper.infrastructure.looper_cli import LooperCliRun, RunCommand, address_in, program_of

STAND_IN = """
import sys
print("building ...", flush=True)
if sys.argv[1] == "fails":
    sys.exit(3)
print("listening on 127.0.0.1:50123", flush=True)
sys.stdin.read()
sys.exit(0)
"""


@pytest.fixture
def stand_in(tmp_path: Path) -> Path:
    script = tmp_path / "looper_cli_stand_in.py"
    script.write_text(STAND_IN)
    return script


def a_command(script: Path, behaviour: str) -> RunCommand:
    """A command that runs the stand-in, with `run` and its options after it."""
    return RunCommand(program=(sys.executable, str(script), behaviour))


def test_the_tool_is_asked_for_a_free_port_and_to_follow_its_parent() -> None:
    arguments = RunCommand(program=("looper-cli",), definition=Path("looper.toml")).arguments()

    assert arguments[:3] == ["looper-cli", "run", "looper.toml"]
    assert "--stop-on-stdin-close" in arguments
    assert arguments[arguments.index("--listen") + 1] == "127.0.0.1:0"


def test_a_virtual_clock_and_a_skipped_build_are_passed_on() -> None:
    arguments = RunCommand(program=("looper-cli",), virtual=True, build=False).arguments()

    assert "--virtual" in arguments
    assert "--no-build" in arguments


def test_a_command_given_as_text_is_split_at_spaces() -> None:
    assert program_of("uv run --project ../looper-core looper-cli") == (
        "uv",
        "run",
        "--project",
        "../looper-core",
        "looper-cli",
    )


def test_the_address_is_read_from_the_line_that_announces_it() -> None:
    assert address_in("listening on 127.0.0.1:50123\n") == "127.0.0.1:50123"
    assert address_in("building ...") is None


def test_a_started_tool_names_its_address_and_stops_when_asked(stand_in: Path) -> None:
    started = LooperCliRun.start(a_command(stand_in, "serves"))

    assert started.address == "127.0.0.1:50123"
    assert started.stop() == 0


def test_a_tool_that_ends_before_serving_says_so(stand_in: Path) -> None:
    with pytest.raises(LooperCliError, match="exit 3"):
        LooperCliRun.start(a_command(stand_in, "fails"))


def test_a_tool_that_cannot_be_found_says_which() -> None:
    with pytest.raises(LooperCliError, match="no-such-looper-cli"):
        LooperCliRun.start(RunCommand(program=("no-such-looper-cli",)))
