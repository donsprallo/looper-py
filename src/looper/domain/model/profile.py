"""Where the simulation spent its time, function by function.

The server weaves the firmware with instrumentation and ranks what it
measured. A test reads that ranking to say what a change did to it: the
filter that was rewritten should no longer be the heaviest function, or
should be, if that was the point of the exercise.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The origin the server gives a function of the firmware itself, as
#: opposed to the device model, the adapter, the runtime or a library.
FIRMWARE_ORIGIN = "firmware"


@dataclass(frozen=True)
class ProfileEntry:
    """One measured function.

    Attributes:
        name: The function's name.
        origin: Which part of the simulation it belongs to: ``firmware``,
            ``device model``, ``adapter``, ``component``, ``runtime`` or
            ``library``.
        calls: How often it was called since the measurements were cleared.
        self_nanoseconds: Host time spent in the function itself.
        total_nanoseconds: Host time spent in it and in what it called.
        source_path: The file it is written in; empty when the build does not say.
        line: The line it is declared on; zero when the build does not say.
    """

    name: str
    origin: str
    calls: int
    self_nanoseconds: int
    total_nanoseconds: int
    source_path: str = ""
    line: int = 0


@dataclass(frozen=True)
class Profile:
    """Every measured function since the measurements were last cleared.

    Attributes:
        functions: Every function the profile measured, in the server's order.
        measured_nanoseconds: Host time the measurement covered.
        is_profiling: Whether the build is woven at all; without it every
            figure is zero, and a test would otherwise read that as "fast".
        note: What the server says about the profile, including why it is empty.
    """

    functions: tuple[ProfileEntry, ...] = ()
    measured_nanoseconds: int = 0
    is_profiling: bool = False
    note: str = ""

    def heaviest_first(self, origin: str | None = None) -> tuple[ProfileEntry, ...]:
        """The functions by the time spent in themselves, the heaviest first.

        Self time rather than total time, because ``main`` would otherwise
        always win. `origin` narrows the ranking to one part of the
        simulation, such as ``firmware``.
        """
        chosen = (one for one in self.functions if origin is None or one.origin == origin)
        return tuple(sorted(chosen, key=lambda one: one.self_nanoseconds, reverse=True))

    def heaviest(self, origin: str | None = None) -> ProfileEntry | None:
        """The function that spent the most time in itself, or None when nothing was measured."""
        ranking = self.heaviest_first(origin)
        return ranking[0] if ranking else None

    def entry(self, name: str) -> ProfileEntry | None:
        """The measurement of one function, or None when it was not measured."""
        return next((one for one in self.functions if one.name == name), None)
