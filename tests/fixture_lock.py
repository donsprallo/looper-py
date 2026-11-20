"""One simulation of a fixture at a time, shared with looper-srv's conformance suite.

looper-srv keeps a simulation's files in the fixture's own build directory,
and a project runs on a bench or alone, not both at once. Two servers on one
fixture -- this suite and srv's conformance suite in another terminal --
would overwrite each other's files. srv's suite holds a lock per fixture in
the temporary directory while it serves one; this takes the same lock, in
the same place and by the same name, so either waits for the other.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import IO

#: How often a waiting test tries the lock again.
RETRY_SECONDS = 0.2
#: How long a test waits before it gives up: a whole module of the other suite fits.
WAIT_SECONDS = 900.0
#: Where srv's conformance suite keeps its locks.
LOCKS = Path(tempfile.gettempdir()) / "looper-conformance"


def lock_path(definition: Path) -> Path:
    """The lock of the fixture a definition belongs to: one per build directory."""
    project = str(definition.resolve().parent).casefold()
    return LOCKS / f"{hashlib.sha256(project.encode()).hexdigest()[:16]}.lock"


@contextmanager
def simulation_of(definition: Path) -> Iterator[None]:
    """Hold the fixture's lock for as long as the block runs."""
    path = lock_path(definition)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        _acquire(handle)
        try:
            yield
        finally:
            _release(handle)


def _acquire(handle: IO[bytes]) -> None:
    """Wait until this process holds the first byte of the lock file."""
    deadline = time.monotonic() + WAIT_SECONDS
    while not _tried(handle):
        if time.monotonic() > deadline:
            raise TimeoutError(f"{handle.name} stayed locked: is the fixture served elsewhere?")
        time.sleep(RETRY_SECONDS)


def _tried(handle: IO[bytes]) -> bool:
    """Take the lock if nobody holds it; whether it was taken."""
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _release(handle: IO[bytes]) -> None:
    """Let the other suite in."""
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
