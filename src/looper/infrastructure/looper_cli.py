"""Starting `looper-cli run` as a child of the test.

`looper-cli run` builds the simulation, starts it, and serves the inspector
contract for it on a free port, which it names on the line that starts with
`listening on`. It is told to stop when its standard input closes, and that
input is held here: however the test ends -- finished, failed, killed -- the
pipe closes with it, and looper-cli stops the simulation and the server.
"""

from __future__ import annotations

import subprocess
import threading
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import IO

#: What looper-cli prints before the address it serves on.
LISTENING_PREFIX = "listening on "

#: Where the server should listen: this machine, any free port.
LISTEN_ANYWHERE_LOCAL = "127.0.0.1:0"

#: How long looper-cli is given to stop the server and the simulation.
STOP_GRACE_SECONDS = 8.0


class LooperCliError(RuntimeError):
    """looper-cli could not be started, or ended before it served."""


@dataclass(frozen=True)
class RunCommand:
    """How to start looper-cli, and what it should run.

    Attributes:
        program: The program and its leading arguments, for example
            ``("looper-cli",)`` or ``("uv", "run", "--project", "../looper-core",
            "looper-cli")``.
        definition: The build definition; looper-cli's own default,
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
        return arguments


class LooperCliRun:
    """A running looper-cli, stopped by `stop`."""

    def __init__(self, process: subprocess.Popen[str], address: str) -> None:
        self._process = process
        self._address = address

    @classmethod
    def start(cls, command: RunCommand) -> LooperCliRun:
        """Start looper-cli and wait until it says where it serves.

        What the build and the firmware print goes to this process's error
        stream, where a person running the test reads it.

        Raises:
            LooperCliError: If it could not be started or ended before serving.
        """
        try:
            process = subprocess.Popen(  # noqa: S603
                command.arguments(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
        except OSError as error:
            raise LooperCliError(f"could not start {command.program[0]!r}: {error}") from error
        address = _read_address(_lines(process.stdout))
        if address is None:
            raise LooperCliError(f"looper-cli stopped before it served (exit {process.wait()})")
        return cls(process, address)

    @property
    def address(self) -> str:
        """Where the server listens."""
        return self._address

    def stop(self) -> int:
        """Ask looper-cli to stop, make it stop if it does not, and hand back its exit code.

        Closing its standard input is the asking. It comes first because it
        reaches looper-cli itself: the program started is often a launcher
        whose child is the interpreter, and killing the launcher would leave
        the interpreter running.
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

    looper-cli prints little after that line, but a pipe nobody reads would
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


def program_of(command: str | Sequence[str]) -> tuple[str, ...]:
    """A command as a program and its leading arguments, split at spaces if given as text."""
    if isinstance(command, str):
        return tuple(command.split())
    return tuple(command)
