"""Starting the server's `run` command as a child of the test.

`looper-srv run` builds the simulation, starts it, and serves the inspector
contract for it on a free port, which it names on the line that starts with
`listening on`. It is told to stop when its standard input closes, and that
input is held here: however the test ends -- finished, failed, killed -- the
pipe closes with it, and the server stops the simulation and itself.

Started from here, looper-srv is told that a test started it and which process
that is, so that a list of servers on this PC shows it as a test's, ending
with it. Another program that takes the same `run` command (looper-core's
``looper-cli``, the frozen reference) is started without those two options.

The module keeps its old name, from the days when looper-core's ``looper-cli``
was the only server.
"""

from __future__ import annotations

import os
import subprocess
import threading
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import IO

#: What the server prints before the address it serves on.
LISTENING_PREFIX = "listening on "

#: Where the server should listen: this machine, any free port.
LISTEN_ANYWHERE_LOCAL = "127.0.0.1:0"

#: What looper-srv's program is called, with or without `.exe`.
LOOPER_SRV = "looper-srv"

#: How long the server is given to stop itself and the simulation.
STOP_GRACE_SECONDS = 8.0


class ServerStartError(RuntimeError):
    """The server could not be started, or ended before it served.

    It ends before serving when it cannot build or start the simulation; what
    it printed about that went to the test's error stream.
    """


#: The old name of `ServerStartError`, from the days of looper-core's
#: ``looper-cli``. Deprecated: catch `ServerStartError`; this name stays so
#: that existing code keeps working.
LooperCliError = ServerStartError


@dataclass(frozen=True)
class RunCommand:
    """How to start the server, and what it should run.

    Attributes:
        program: The program and its leading arguments, for example
            ``("looper-srv",)`` or ``("C:/looper/looper-srv.exe",)``.
        definition: The build definition; the server's own default,
            ``looper.toml`` in the working directory, when none is named.
        virtual: Whether the simulation runs on a virtual clock.
        build: Whether to build before starting, or start what was built.
    """

    program: tuple[str, ...]
    definition: Path | None = None
    virtual: bool = False
    build: bool = True

    def arguments(self) -> list[str]:
        """The whole command line."""
        arguments = [*self.program, "run"]
        if self.definition is not None:
            arguments.append(str(self.definition))
        arguments.extend(["--listen", LISTEN_ANYWHERE_LOCAL, "--stop-on-stdin-close", "--quiet"])
        if self.virtual:
            arguments.append("--virtual")
        if not self.build:
            arguments.append("--no-build")
        if is_looper_srv(self.program):
            arguments.extend(["--started-by", "test", "--owner-pid", str(os.getpid())])
        return arguments


class LooperCliRun:
    """A running server, stopped by `stop`."""

    def __init__(self, process: subprocess.Popen[str], address: str) -> None:
        self._process = process
        self._address = address

    @classmethod
    def start(cls, command: RunCommand) -> LooperCliRun:
        """Start the server and wait until it says where it serves.

        What the build and the firmware print goes to this process's error
        stream, where a person running the test reads it.

        Raises:
            ServerStartError: If it could not be started or ended before serving.
        """
        try:
            process = subprocess.Popen(  # noqa: S603
                command.arguments(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
        except OSError as error:
            raise ServerStartError(f"could not start {command.program[0]!r}: {error}") from error
        address = _read_address(_lines(process.stdout))
        if address is None:
            raise ServerStartError(f"the server stopped before it served (exit {process.wait()})")
        return cls(process, address)

    @property
    def address(self) -> str:
        """Where the server listens."""
        return self._address

    def stop(self) -> int:
        """Ask the server to stop, make it stop if it does not, and hand back its exit code.

        Closing its standard input is the asking. It comes first because it
        reaches the server itself: the program started may be a launcher
        (``uv run ...``) whose child is the server, and killing the launcher
        would leave the server running.
        """
        if self._process.stdin is not None:
            self._process.stdin.close()
        try:
            return self._process.wait(timeout=STOP_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            self._process.kill()
            return self._process.wait()


def _lines(stream: IO[str] | None) -> Iterator[str]:
    """The lines of a stream, or none when there is no stream."""
    if stream is None:
        return iter(())
    return iter(stream.readline, "")


def _read_address(lines: Iterator[str]) -> str | None:
    """Read lines until one names the address, then keep the pipe drained.

    The server prints little after that line, but a pipe nobody reads would
    block it the moment it did.
    """
    for line in lines:
        address = address_in(line)
        if address is not None:
            threading.Thread(target=_drain, args=(lines,), daemon=True).start()
            return address
    return None


def _drain(lines: Iterator[str]) -> None:
    """Read and forget whatever else is printed."""
    for _ in lines:
        continue


def address_in(line: str) -> str | None:
    """The address a line announces, if it announces one."""
    stripped = line.strip()
    if not stripped.startswith(LISTENING_PREFIX):
        return None
    return stripped.removeprefix(LISTENING_PREFIX)


def is_looper_srv(program: Sequence[str]) -> bool:
    """Whether a program is looper-srv, which takes who started it; looper-cli refuses that."""
    return bool(program) and Path(program[0]).stem == LOOPER_SRV


def program_of(command: str | Sequence[str]) -> tuple[str, ...]:
    """A command as a program and its leading arguments, split at spaces if given as text."""
    if isinstance(command, str):
        return tuple(command.split())
    return tuple(command)
