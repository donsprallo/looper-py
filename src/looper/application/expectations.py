"""Expecting things of a running firmware, and finding out.

A firmware test has two halves. Setting the scene -- driving an input,
putting a frame on a bus -- which is what `Simulation` is for, and saying
what should then be true, which is this.

Expectations are declared first and checked afterwards, against one window
of time. That ordering is what lets twenty of them cost one reading of
each recording, and it is also what lets a check look at the whole window
rather than at the instant it happened to run.

In virtual time the window is advanced rather than waited out, so a test
takes as long as the firmware needs and not a second more, and two runs
see the same thing.
"""

from __future__ import annotations

import time

from looper.application.ports import Inspector, SimulationRefusedError
from looper.application.subjects import (
    BusExpectation,
    CallExpectation,
    ChannelExpectation,
    MemoryExpectation,
    StackExpectation,
)
from looper.domain.checks import Check, FirmwareIsAlive
from looper.domain.model import (
    Exchange,
    ExpectationReport,
    MemoryUsage,
    Observation,
    Recordings,
    Sample,
    TimeMode,
)

MICROSECONDS_PER_SECOND = 1_000_000

#: Pages one reading will take before giving up. A window long enough to
#: need more than this is long enough that a check should say so.
MAXIMUM_PAGES = 512


class Expectations:
    """Collects what should be true, then finds out whether it is.

    Declare, then evaluate::

        check = simulation.expect()
        check.channel(0, "P1A").reaches(1.0, tolerance=0.01, within_seconds=0.2)
        check.call("adapter_spi_dma_transfer").happened_at(8000)
        check.bus(2, "CAN2").nothing_refused()

        assert check.evaluate(for_seconds=1.0)
    """

    def __init__(self, inspector: Inspector, time_mode: TimeMode) -> None:
        self._inspector = inspector
        self._time_mode = time_mode
        self._checks: list[Check] = []

    def add(self, check: Check) -> Expectations:
        """Take one more expectation, and allow another to be chained."""
        self._checks.append(check)
        return self

    def channel(self, channel_id: int, name: str = "") -> ChannelExpectation:
        """Expect something of one analog channel."""
        return ChannelExpectation(self, channel_id, name or f"channel {channel_id}")

    def bus(self, bus_id: int, name: str = "") -> BusExpectation:
        """Expect something of one bus."""
        return BusExpectation(self, bus_id, name or f"bus {bus_id}")

    def call(self, function: str) -> CallExpectation:
        """Expect something of one adapter function."""
        return CallExpectation(self, function)

    def memory(self) -> MemoryExpectation:
        """Expect something of the heap."""
        return MemoryExpectation(self)

    def stack(self) -> StackExpectation:
        """Expect something of the stack."""
        return StackExpectation(self)

    def firmware_is_alive(self) -> Expectations:
        """Expect the firmware to still be reaching the adapter at all."""
        return self.add(FirmwareIsAlive())

    def evaluate(self, for_seconds: float = 1.0) -> ExpectationReport:
        """Watch for a while, then check everything that was declared.

        The recordings and measurements are cleared first, so a check sees
        the window and not whatever happened before it. They are cleared for
        every client of the simulation: there is one simulation.
        """
        self._inspector.clear_recordings()
        self._inspector.clear_measurements()
        before = self._inspector.simulated_microseconds()
        self._let_time_pass(for_seconds)
        observed = self._observe(before)
        return ExpectationReport(outcomes=tuple(check.evaluate(observed) for check in self._checks))

    def _let_time_pass(self, seconds: float) -> None:
        """Advance the clock, or wait."""
        if self._time_mode is TimeMode.VIRTUAL:
            self._inspector.advance(int(seconds * MICROSECONDS_PER_SECOND))
        else:
            time.sleep(seconds)

    def _observe(self, before_microseconds: int) -> Observation:
        """Read the clock and count the calls together, then read every recording.

        The firmware keeps running while it is read -- a virtual clock moves
        on every idle pass as well. A rate is calls over time, so the clock
        and the calls are read one straight after the other, the clock first:
        the server counts the calls at the start of its answer and then
        ranks the profile beside them, which takes a while, and that while
        must not land in the window.
        """
        after = self._inspector.simulated_microseconds()
        timings = self._inspector.read_timings()
        recorded = self._read_all()
        return Observation(
            samples=recorded.samples,
            exchanges=recorded.exchanges,
            timings=timings,
            elapsed_seconds=(after - before_microseconds) / MICROSECONDS_PER_SECOND,
            lost_samples=max(0, _after(recorded.samples) - len(recorded.samples)),
            lost_exchanges=max(0, _after(recorded.exchanges) - len(recorded.exchanges)),
            memory=self._memory(),
        )

    def _read_all(self) -> Recordings:
        """Read pages up to where the recordings stood when reading began.

        A check that counted one page would quietly measure the page size
        instead of the run, so the pages are read to the end. The end is
        the one the first reply names, not wherever the recordings have got
        to since: a firmware that keeps running keeps recording, and a
        reader chasing it would never finish.
        """
        collected = self._inspector.read_recordings(0, 0)
        end = (collected.next_sample, collected.next_exchange)
        for _ in range(MAXIMUM_PAGES):
            position = (_after(collected.samples), _after(collected.exchanges))
            if position[0] >= end[0] and position[1] >= end[1]:
                return collected
            page = self._inspector.read_recordings(*position)
            if not (page.samples or page.exchanges):
                return collected
            collected = _joined(collected, page)
        return collected

    def _memory(self) -> MemoryUsage:
        """The heap and the stack, or nothing known when the build cannot be read."""
        try:
            return self._inspector.read_memory()
        except SimulationRefusedError:
            return MemoryUsage()


def _after(records: tuple[Sample, ...] | tuple[Exchange, ...]) -> int:
    """Where reading goes on after the records already read.

    From the last record seen rather than from the sequence a reply names
    as next: that one is where the recording has got to, not this reader.
    """
    return records[-1].sequence + 1 if records else 0


def _joined(collected: Recordings, page: Recordings) -> Recordings:
    """What has been read so far, with one more page behind it."""
    return Recordings(
        samples=(*collected.samples, *page.samples),
        next_sample=max(collected.next_sample, page.next_sample),
        exchanges=(*collected.exchanges, *page.exchanges),
        next_exchange=max(collected.next_exchange, page.next_exchange),
    )
