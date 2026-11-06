"""The firmware's lives as a test reads them: resets, lives, and flash operations.

A reset is not a restart. The firmware begins a new life, simulated time and
the recording go on, and the test keeps its connection. These are the words
the server uses -- causes such as ``watchdog`` or ``software``, flash
operations such as ``write`` or ``violation`` -- so a test reads like the
window does.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from looper.domain.model.profile import Profile
from looper.domain.model.readings import MemoryUsage


@dataclass(frozen=True)
class Life:
    """One life of the firmware.

    Attributes:
        number: 1 for the first of a run.
        started_at_us: When it began.
        ended_at_us: When it ended; 0 while it runs.
        cause: The cause of the reset that ended it; empty while it runs.
        text: The line the server shows for it.
        has_dump: Whether what it left behind can be read.
    """

    number: int
    started_at_us: int
    ended_at_us: int = 0
    cause: str = ""
    text: str = ""
    has_dump: bool = False

    @property
    def is_running(self) -> bool:
        """Whether this is the life that runs now."""
        return self.ended_at_us == 0 and not self.cause


@dataclass(frozen=True)
class LifeDump:
    """What a life left behind when it ended: its heap book and its profile."""

    life: Life
    memory: MemoryUsage = field(default_factory=MemoryUsage)
    profile: Profile = field(default_factory=Profile)
    note: str = ""


@dataclass(frozen=True)
class Lives:
    """Every life of the run, and a reset loop while there is one."""

    lives: tuple[Life, ...] = ()
    resets: int = 0
    loop_finding: str = ""
