"""Starting a bench with `looper-srv run --bench bench.toml` as a child of the test.

The server started is the bench's leader. It builds every member as a
library, starts the bench host and one looper-srv per further member, and
before its own ``listening on`` line it says the host's process and where
every other member's server listens (looper-srv ``docs/bench.md``)::

    bench host pid=4242
    bench member=gateway listening on 127.0.0.1:50123
    listening on 127.0.0.1:50051

Its standard input is held here, as `LooperCliRun` holds a server's: when it
closes, the leader closes the input of every member's server, which ends
them, and then the host's. A bench runs on held virtual clocks.

What the leader prints on its error stream goes on to the test's, and its
last lines are kept: a bench it refused -- the free download, a bench file
that does not fit, a join the firmware has no bus for -- is said there in
one sentence, which the error raised here carries.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import threading
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

from looper.application.ports import ProFeatureLockedError
from looper.infrastructure.looper_cli import (
    LISTEN_ANYWHERE_LOCAL,
    ServerStartError,
    address_in,
)

#: What the leader prints before the bench host's process number.
HOST_PREFIX = "bench host pid="
#: What it prints before a further member's name and where its server listens.
MEMBER_PREFIX = "bench member="
MEMBER_LISTENING = " listening on "
#: What the server puts before a sentence on its error stream.
SAID_PREFIX = "looper-srv: "
#: The exit code of a part of looper Pro the licence does not unlock.
PRO_LOCKED_EXIT = 3
#: How many of the leader's last error lines are kept for the error raised.
KEPT_LINES = 40
#: How long the leader is given to stop the members' servers, the host and itself.
STOP_GRACE_SECONDS = 30.0


class BenchProLockedError(ServerStartError, ProFeatureLockedError):
    """The server refused the bench because its licence does not unlock looper Pro.

    A `ServerStartError`, since nothing started, and a `ProFeatureLockedError`,
    so that a test tells a missing licence from a bench that did not build.
    """


@dataclass(frozen=True)
class BenchCommand:
    """How to start the leader of a bench, and from which bench file.

    Attributes:
        program: The program and its leading arguments, ``("looper-srv",)``.
        bench_file: The ``bench.toml`` of the bench.
        build: Whether to build the members first, or start what was built.
        options: Further options of `run` for every member, ``--no-profile``.
    """

    program: tuple[str, ...]
    bench_file: Path
    build: bool = True
    options: tuple[str, ...] = ()

    def arguments(self) -> list[str]:
        """The whole command line."""
        arguments = [*self.program, "run", "--bench", str(self.bench_file)]
        arguments.extend(["--listen", LISTEN_ANYWHERE_LOCAL, "--stop-on-stdin-close", "--quiet"])
        if not self.build:
            arguments.append("--no-build")
        arguments.extend(self.options)
        arguments.extend(["--started-by", "test", "--owner-pid", str(os.getpid())])
        return arguments


@dataclass
class BenchAddresses:
    """What the leader said before it served: the host's process and every server's address."""

    host_pid: int = 0
    members: dict[str, str] = field(default_factory=dict)
    leader: str | None = None

    def take(self, line: str) -> bool:
        """Take in one line of the leader's; whether it was the leader's own, the last."""
        stripped = line.strip()
        if stripped.startswith(HOST_PREFIX):
            self.host_pid = int(stripped.removeprefix(HOST_PREFIX))
        elif stripped.startswith(MEMBER_PREFIX) and MEMBER_LISTENING in stripped:
            member, address = stripped.removeprefix(MEMBER_PREFIX).split(MEMBER_LISTENING, 1)
            self.members[member] = address
        else:
            self.leader = address_in(stripped)
        return self.leader is not None


class BenchRun:
    """A running bench's leader, stopped by `stop`."""

    def __init__(self, process: subprocess.Popen[str], addresses: BenchAddresses) -> None:
        self._process = process
        self._addresses = addresses

    @classmethod
    def start(cls, command: BenchCommand) -> BenchRun:
        """Start the leader and wait until every server of the bench listens.

        Raises:
            BenchProLockedError: If the licence does not unlock a bench.
            ServerStartError: If the bench could not be built or started;
                the message is the server's sentence.
        """
        try:
            process = subprocess.Popen(  # noqa: S603
                command.arguments(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError as error:
            raise ServerStartError(f"could not start {command.program[0]!r}: {error}") from error
        said = _ErrorEcho.started(process.stderr)
        addresses = _read_addresses(_lines(process.stdout))
        if addresses.leader is None:
            raise _start_failed(process.wait(), said.joined())
        return cls(process, addresses)

    @property
    def leader_address(self) -> str:
        """Where the leader's server listens."""
        return self._addresses.leader or ""

    @property
    def member_addresses(self) -> dict[str, str]:
        """Where every further member's server listens, by the member's name."""
        return dict(self._addresses.members)

    @property
    def host_pid(self) -> int:
        """The bench host's process."""
        return self._addresses.host_pid

    def stop(self) -> int:
        """Ask the leader to stop the bench, make it stop if it does not; its exit code."""
        if self._process.stdin is not None:
            self._process.stdin.close()
        try:
            return self._process.wait(timeout=STOP_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            self._process.kill()
            return self._process.wait()


def _read_addresses(lines: Iterator[str]) -> BenchAddresses:
    """Read the leader's lines until its own address, then keep the pipe drained."""
    addresses = BenchAddresses()
    for line in lines:
        if addresses.take(line):
            threading.Thread(target=_drain, args=(lines,), daemon=True).start()
            break
    return addresses


def _start_failed(exit_code: int, said: str) -> ServerStartError:
    """The error for a leader that ended before it served, with what it said."""
    sentence = said or f"the bench server stopped before it served (exit {exit_code})"
    if exit_code == PRO_LOCKED_EXIT:
        return BenchProLockedError(sentence)
    return ServerStartError(sentence)


class _ErrorEcho:
    """Passes the leader's error stream on to the test's, keeping its last sentences."""

    def __init__(self, stream: IO[str]) -> None:
        self._kept: deque[str] = deque(maxlen=KEPT_LINES)
        self._thread = threading.Thread(target=self._echo, args=(stream,), daemon=True)

    @classmethod
    def started(cls, stream: IO[str] | None) -> _ErrorEcho:
        """An echo of `stream`, already reading."""
        echo = cls(stream if stream is not None else io.StringIO())
        echo._thread.start()
        return echo

    def _echo(self, stream: IO[str]) -> None:
        for line in iter(stream.readline, ""):
            sys.stderr.write(line)
            if line.startswith(SAID_PREFIX):
                self._kept.append(line.removeprefix(SAID_PREFIX).strip())

    def joined(self) -> str:
        """The server's sentences, once the stream ended."""
        self._thread.join(timeout=STOP_GRACE_SECONDS)
        return " ".join(self._kept)


def _lines(stream: IO[str] | None) -> Iterator[str]:
    """The lines of a stream, or none when there is no stream."""
    if stream is None:
        return iter(())
    return iter(stream.readline, "")


def _drain(lines: Iterator[str]) -> None:
    """Read and forget whatever else is printed."""
    for _ in lines:
        continue
