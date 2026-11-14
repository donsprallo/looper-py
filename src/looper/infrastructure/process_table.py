"""When a process started, from the operating system, without a dependency for it.

Windows answers through ``GetProcessTimes``, Linux through ``/proc``. Where
neither is there, a process that runs is taken to be the one that announced
itself: a reused pid then goes unnoticed, which is a stale row in a list,
not a wrong connection -- ``Describe`` names the server that answers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from looper.application.server_list import ProcessTable

#: FILETIME counts 100 ns from 1601; the Unix epoch is this many of them later.
_FILETIME_UNIX_EPOCH = 116_444_736_000_000_000
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


class OsProcessTable(ProcessTable):
    """The processes of this PC."""

    def started_at_unix_ms(self, pid: int) -> int | None:
        """When the process started, or ``None`` when none runs under the pid."""
        if pid <= 0:
            return None
        if sys.platform == "win32":
            return _windows_start(pid)
        if Path("/proc/stat").is_file():
            return _proc_start(pid)
        return _running_since_now(pid)


def _windows_start(pid: int) -> int | None:
    """The creation time Windows keeps for the process, in Unix milliseconds."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel32.GetProcessTimes(handle, *(ctypes.byref(one) for one in times)):
            return None
        created = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        return (created - _FILETIME_UNIX_EPOCH) // 10_000
    finally:
        kernel32.CloseHandle(handle)


def _proc_start(pid: int) -> int | None:
    """The start of the process from ``/proc``: clock ticks after boot, plus the boot."""
    if sys.platform == "win32":
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
        boot = next(
            int(line.split()[1])
            for line in Path("/proc/stat").read_text(encoding="ascii").splitlines()
            if line.startswith("btime ")
        )
    except (OSError, StopIteration, ValueError):
        return None
    # The command name is in parentheses and may hold spaces; field 22 counts from after it.
    ticks = int(stat.rsplit(")", 1)[1].split()[19])
    ticks_per_second = int(os.sysconf("SC_CLK_TCK"))
    return boot * 1000 + ticks * 1000 // ticks_per_second


def _running_since_now(pid: int) -> int | None:
    """Zero when the process runs, which no entry started before; ``None`` when not."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except PermissionError:
        return 0
    return 0
