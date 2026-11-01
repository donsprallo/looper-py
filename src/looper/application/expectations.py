"""Expecting things of a running firmware, and finding out.

A firmware test has two halves. Setting the scene -- driving an input,
putting a frame on a bus -- which is what `Simulation` is for, and saying
what should then be true, which is this.

Expectations are declared first and checked afterwards, against one window
of time. That ordering is what lets twenty of them cost one reading of
each recording, and it is also what lets a check look at the whole window
rather than at the instant it happened to run.

On a held clock the window is advanced rather than waited out, so a test
takes as long as the firmware needs and not a second more, and two runs
see the same thing. On a clock that runs by itself the window is waited
out on the host and cut by simulated time.
"""

from __future__ import annotations

import time

from looper.application.event_window import WindowReader
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
    ClockMode,
    ExpectationReport,
    MemoryUsage,
    Observation,
    RunStatus,
)

MICROSECONDS_PER_SECOND = 1_000_000


class Expectations:
    """Collects what should be true, then finds out whether it is.

    Declare, then evaluate::

        check = simulation.expect()
        check.channel(0, "P1A").reaches(1.0, tolerance=0.01, within_seconds=0.2)
        check.call("adapter_spi_dma_transfer").happened_at(8000)
        check.bus(2, "CAN2").nothing_refused()

        assert check.evaluate(for_seconds=1.0)
    """

    def __init__(self, inspector: Inspector) -> None:
        self._inspector = inspector
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
        every client of the simulation: there is one simulation, and the
        clear begins a new recording epoch for all of them.

        The clock mode is read at the start of every window, because any
        client may have switched it. A held clock is run for the window; a
        clock that runs by itself is waited out.

        Raises:
            SimulationRefusedError: If a debugger holds the firmware, another
                client cleared the recording meanwhile, or the clock refuses.
        """
        start = self._begin_window()
        self._let_time_pass(start.clock_mode, for_seconds)
        end = self._inspector.run_state()
        observed = self._observe(start, end)
        return ExpectationReport(outcomes=tuple(check.evaluate(observed) for check in self._checks))

    def _begin_window(self) -> RunStatus:
        """Clear what was recorded and say where the window starts."""
        before = self._inspector.run_state()
        if before.hold_reason:
            raise SimulationRefusedError(before.hold_reason)
        self._inspector.clear_recordings(before.epoch)
        self._inspector.clear_measurements()
        return self._inspector.run_state()

    def _let_time_pass(self, clock_mode: ClockMode, seconds: float) -> None:
        """Run a held clock for the span, or wait for one that runs by itself."""
        if clock_mode is ClockMode.HELD:
            self._inspector.run_for(round(seconds * MICROSECONDS_PER_SECOND))
        else:
            time.sleep(seconds)

    def _observe(self, start: RunStatus, end: RunStatus) -> Observation:
        """Count the calls straight after the clock, then read the window's events.

        The firmware may keep running while it is read. A rate is calls over
        time, so the clock is read first and the calls straight after it:
        the server counts the calls at the start of its answer and then
        ranks the profile beside them, which takes a while, and that while
        must not land in the window.
        """
        timings = self._inspector.read_timings()
        events = WindowReader(self._inspector, start, end.now_us).read()
        return Observation(
            samples=events.samples,
            exchanges=events.exchanges,
            timings=timings,
            elapsed_seconds=(end.now_us - start.now_us) / MICROSECONDS_PER_SECOND,
            lost_events=events.lost_events,
            memory=self._memory(),
        )

    def _memory(self) -> MemoryUsage:
        """The heap and the stack, or nothing known when the build cannot be read."""
        try:
            return self._inspector.read_memory()
        except SimulationRefusedError:
            return MemoryUsage()
