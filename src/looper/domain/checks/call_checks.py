"""What one can expect of the calls the firmware makes into its adapter."""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome


@dataclass(frozen=True)
class CallHappened(Check):
    """An adapter function was called at least so many times."""

    function: str
    count: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Count how often the firmware made the call."""
        calls = _calls_of(observed, self.function)
        return Outcome(
            self.function, f"at least {self.count} calls", f"{calls}", met=calls >= self.count
        )


@dataclass(frozen=True)
class CallWasAnswered(Check):
    """Something implemented a call, rather than handing back the zero value."""

    function: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the calls made against the ones something answered."""
        timing = observed.timing_of(self.function)
        if timing is None:
            return Outcome(self.function, "implemented and called", "never called", met=False)
        seen = f"{timing.answered_calls} of {timing.calls} answered"
        return Outcome(self.function, "every call answered", seen, met=not timing.unanswered_calls)


@dataclass(frozen=True)
class CallRate(Check):
    """An adapter function was called at about a given rate."""

    function: str
    hertz: float
    tolerance: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Work the rate out of the calls and the time that passed."""
        calls = _calls_of(observed, self.function)
        expected = f"{self.hertz:g} Hz +/- {self.tolerance:.0%}"
        if observed.elapsed_seconds <= 0.0:
            return Outcome(self.function, expected, "no time passed", met=False)
        measured = calls / observed.elapsed_seconds
        allowed = self.hertz * self.tolerance
        return Outcome(
            self.function,
            expected,
            f"{measured:.4g} Hz",
            met=abs(measured - self.hertz) <= allowed,
        )


@dataclass(frozen=True)
class FirmwareIsAlive(Check):
    """The firmware is still reaching the adapter at all."""

    def evaluate(self, observed: Observation) -> Outcome:
        """Count every adapter call there was."""
        calls = sum(timing.calls for timing in observed.timings)
        return Outcome("the firmware", "still calling the adapter", f"{calls} calls", met=calls > 0)


def _calls_of(observed: Observation, function: str) -> int:
    """How often one function was called."""
    timing = observed.timing_of(function)
    return 0 if timing is None else timing.calls
