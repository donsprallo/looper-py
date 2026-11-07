"""What a test can expect of the firmware's interrupts, DMA and the run's findings (Pro).

Every expectation here has the window read the server's run findings at
its end, which only a licence for run findings allows: without one the
evaluation raises ProFeatureLockedError with the server's sentence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from looper.domain.checks.dma_checks import LengthFits, NoOverrun, NotAccessedWhileRunning
from looper.domain.checks.interrupt_checks import (
    HandledAtLeast,
    LatencyBelow,
    LockedAtMost,
    NeverLost,
    NoRunFindings,
    ShorterThanPeriod,
)

if TYPE_CHECKING:
    from looper.application.expectations import Expectations

#: Microseconds in each unit a limit may be given in.
UNITS = {"us": 1, "ms": 1000, "s": 1_000_000}


def _microseconds(amount: float, unit: str) -> int:
    if unit not in UNITS:
        raise ValueError(f"a time is in us, ms or s, not {unit}")
    return round(amount * UNITS[unit])


class InterruptExpectation:
    """What is expected of one interrupt source, by its name in contract.toml."""

    def __init__(self, expectations: Expectations, source: str) -> None:
        self._expectations = expectations
        self._source = source
        expectations.reads_run_findings()

    def latency_below(self, amount: float, unit: str = "us") -> Expectations:
        """Expect every ISR of the source to start less than this after it fell due."""
        limit = _microseconds(amount, unit)
        return self._expectations.add(LatencyBelow(self._source, limit))

    def never_lost(self) -> Expectations:
        """Expect no interrupt of the source to be lost."""
        return self._expectations.add(NeverLost(self._source))

    def handled_at_least(self, times: int) -> Expectations:
        """Expect the source's ISR to run at least so often."""
        return self._expectations.add(HandledAtLeast(self._source, times))

    def shorter_than_period(self) -> Expectations:
        """Expect a timer's ISR always to end within its period."""
        return self._expectations.add(ShorterThanPeriod(self._source))


class InterruptsExpectation:
    """What is expected of the interrupts as a whole: how long they were masked."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations
        expectations.reads_run_findings()

    def locked_at_most(self, amount: float = 0, unit: str = "us") -> Expectations:
        """Expect interrupts never masked longer than this; without it, than looper.toml allows."""
        return self._expectations.add(LockedAtMost(_microseconds(amount, unit)))


class RunFindingsExpectation:
    """What is expected of the server's findings of the run."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations
        expectations.reads_run_findings()

    def none(self, kinds: tuple[str, ...] | list[str] = ()) -> Expectations:
        """Expect no finding, of the kinds given or of any."""
        return self._expectations.add(NoRunFindings(tuple(kinds)))


class DmaExpectation:
    """What is expected of one DMA channel, by its name in contract.toml."""

    def __init__(self, expectations: Expectations, channel: str) -> None:
        self._expectations = expectations
        self._channel = channel
        expectations.reads_run_findings()
        expectations.reads_dma()

    def no_overrun(self) -> Expectations:
        """Expect the channel never to write into a half whose ISR had not ended."""
        return self._expectations.add(NoOverrun(self._channel))

    def not_accessed_while_running(self) -> Expectations:
        """Expect the firmware never to touch the buffer where the channel still works."""
        return self._expectations.add(NotAccessedWhileRunning(self._channel))

    def length_fits(self) -> Expectations:
        """Expect every transfer to fit the variable it was given."""
        return self._expectations.add(LengthFits(self._channel))
