"""A generated signal, and a table file read for one.

`Signal` is one waveform, evaluated by the simulation on an analog input or
as a generator of the signal graph. Which of its fields a waveform reads is
the server's to say (``ListWaveforms``); the others are ignored. A choice
left empty is the waveform's first option, and whatever cannot be -- a duty
outside 0 to 1, a pulse's high below its low, times that do not rise -- is
refused by the simulation with its sentence.

A table's points come from a CSV or PWL file that the server reads and, for
a long recording, simplifies (``ReadTable``): reading and simplifying stay
in one place, so a test plays the points the window would.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Signal:
    """A generated signal for an analog input or a generator of the graph.

    The first five fields are every waveform's; the rest belong to one
    waveform each and carry the contract's names, so that
    ``Signal("sweep", 1.0, 0.0, 0.0, 0.0, sweep_from_hz=10.0, ...)`` reads as
    the server's pytest export writes it.

    Attributes:
        waveform: ``constant``, ``sine``, ``square``, ``triangle``,
            ``sawtooth``, ``noise``, ``pulse``, ``rectified_sine``, ``sweep``
            or ``table``, as the simulation offers them.
        amplitude: How far the signal swings around the offset; a rectified
            sine's peak; what a table's values are multiplied by.
        offset: Where it swings around; the whole value of a constant.
        frequency_hz: How often it repeats.
        phase_degrees: Where in its period it starts.
        duty: Square and pulse: the share of each period that is high, 0 to
            1; None is a half.
        low: Pulse: its low level. None takes it from offset and amplitude.
        high: Pulse: its high level. None takes it from offset and amplitude.
        rectification: Rectified sine: ``full`` or ``half``.
        sweep_from_hz: Sweep: where the frequency starts.
        sweep_to_hz: Sweep: where it ends.
        sweep_seconds: Sweep: how long it takes.
        sweep_spacing: Sweep: ``linear`` or ``logarithmic``.
        sweep_end: Sweep: ``repeat``, ``hold`` or ``stop`` at the end.
        table_times: Table: the points' times in seconds, from 0 on, rising.
        table_values: Table: the points' values, as many as times.
        table_between: Table: ``linear`` or ``steps`` between points.
        table_end: Table: ``repeat`` or ``hold`` after the last point.
        table_time_scale: Table: how much slower than its times it plays; 0 is 1.
    """

    waveform: str = "constant"
    amplitude: float = 0.0
    offset: float = 0.0
    frequency_hz: float = 0.0
    phase_degrees: float = 0.0
    duty: float | None = None
    low: float | None = None
    high: float | None = None
    rectification: str = ""
    sweep_from_hz: float = 0.0
    sweep_to_hz: float = 0.0
    sweep_seconds: float = 0.0
    sweep_spacing: str = ""
    sweep_end: str = ""
    table_times: tuple[float, ...] = ()
    table_values: tuple[float, ...] = ()
    table_between: str = ""
    table_end: str = ""
    table_time_scale: float = 0.0

    @property
    def levels(self) -> tuple[float, float]:
        """A pulse's low and high: as given, else from the offset and the amplitude."""
        low = self.offset - self.amplitude if self.low is None else self.low
        high = self.offset + self.amplitude if self.high is None else self.high
        return low, high

    @classmethod
    def pulse(
        cls,
        low: float,
        high: float,
        frequency_hz: float,
        duty: float = 0.5,
        phase_degrees: float = 0.0,
    ) -> Signal:
        """A pulse between two levels, high for `duty` of each period: a gate, a PWM pin."""
        middle, swing = (low + high) / 2, (high - low) / 2
        return cls(
            "pulse", swing, middle, frequency_hz, phase_degrees, duty=duty, low=low, high=high
        )

    @classmethod
    def table(
        cls,
        points: Iterable[tuple[float, float]],
        amplitude: float = 1.0,
        offset: float = 0.0,
        between: str = "",
        end: str = "",
        time_scale: float = 0.0,
    ) -> Signal:
        """A table of ``(seconds, value)`` points, played as ``offset + amplitude * value``.

        `between` is ``linear`` (the default) or ``steps``; `end` is
        ``repeat`` (the default) or ``hold``.
        """
        listed = tuple(points)
        return cls(
            "table",
            amplitude,
            offset,
            table_times=tuple(time for time, _ in listed),
            table_values=tuple(value for _, value in listed),
            table_between=between,
            table_end=end,
            table_time_scale=time_scale,
        )

    @classmethod
    def from_csv(
        cls,
        path: str | os.PathLike[str],
        reader: TableReader,
        value_column: int = 0,
        max_error: float = 0.0,
        keep_every_point: bool = False,
    ) -> Signal:
        """A table from a CSV or PWL file, read and simplified by the server.

        `reader` is the `Simulation` at hand: its ``read_table`` asks the
        server, which reads the file as the window does -- the time first,
        the value from `value_column` after it, a long recording simplified
        so that no point moves further than `max_error`. The signal plays
        the values as they are; `TableFile.signal` scales them.

        Raises:
            ValueError: With the server's sentence, if the file cannot be played.
        """
        read = reader.read_table(path, value_column, max_error, keep_every_point)
        return read.signal()


@dataclass(frozen=True)
class TableFile:
    """A table file as the server read it, ready to be played.

    Attributes:
        path: The file read.
        problem_text: Why it cannot be played, with the file and the line;
            empty when it can, and every other field empty when not.
        summary_text: ``1 024 points · 0 to 2 s · −325 to 325 V``.
        columns: The names of the file's columns, the time first.
        value_column: Which column after the time the values came from.
        rows: Points in the file.
        times: The points to play, in seconds, simplified where it was.
        values: Their values.
        simplified_text: ``120 000 → 2 310 points, max error 0.4 mV``; empty
            when every point is played.
        max_error: The largest distance a point was moved.
        hash: A hash of the file's bytes, which tells a changed file.
        warning_text: What was played of a file too long to read whole.
    """

    path: str
    problem_text: str = ""
    summary_text: str = ""
    columns: tuple[str, ...] = ()
    value_column: int = 0
    rows: int = 0
    times: tuple[float, ...] = ()
    values: tuple[float, ...] = ()
    simplified_text: str = ""
    max_error: float = 0.0
    hash: str = ""
    warning_text: str = ""

    def signal(
        self,
        amplitude: float = 1.0,
        offset: float = 0.0,
        between: str = "",
        end: str = "",
        time_scale: float = 0.0,
    ) -> Signal:
        """The points as a table signal, played as ``offset + amplitude * value``.

        Raises:
            ValueError: With the server's sentence, if the file cannot be played.
        """
        if self.problem_text:
            raise ValueError(self.problem_text)
        points = zip(self.times, self.values, strict=True)
        return Signal.table(points, amplitude, offset, between, end, time_scale)


class TableReader(Protocol):
    """What reads a table file for `Signal.from_csv`: a `Simulation`, through its server."""

    def read_table(
        self,
        path: str | os.PathLike[str],
        value_column: int = 0,
        max_error: float = 0.0,
        keep_every_point: bool = False,
    ) -> TableFile:
        """The file's points as the server reads them."""
        ...
