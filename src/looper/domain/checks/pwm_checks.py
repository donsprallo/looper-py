"""The things one can expect of a PWM output (free).

Duty, frequency and on time are the server's measurement of the window,
weighed by how long each state held -- exact at any frequency, since an
output is a state and not a stream of edges. Only when the output got to a
duty is read here, from its state at the window's start and its changes in
it, the way a channel's arrival is read from its samples.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome
from looper.domain.model.pwm import PwmChange, PwmMeasurement, PwmWindow

MICROSECONDS_PER_SECOND = 1_000_000


def _percent(duty: float) -> str:
    return f"{duty * 100:g} %"


def _missing(observed: Observation, name: str) -> str:
    return f"no PWM output named {name!r}; the contract lists {observed.pwm_outputs.names}"


def _unmeasured(measurement: PwmMeasurement) -> str:
    return measurement.note or "off the whole window"


@dataclass(frozen=True)
class DutyBetween(Check):
    """A PWM output's duty stays within a range whenever it is on, and it is on at all."""

    name: str
    low: float
    high: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the smallest and the largest duty of the window with the range."""
        expected = f"duty within {_percent(self.low)} .. {_percent(self.high)}"
        window = observed.pwm_windows.get(self.name)
        if window is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        measurement = window.measurement
        if not measurement.measured:
            return Outcome(self.name, expected, _unmeasured(measurement), met=False)
        met = measurement.duty_min >= self.low and measurement.duty_max <= self.high
        return Outcome(self.name, expected, f"duty {measurement.duty_text}", met=met)


@dataclass(frozen=True)
class PwmFrequency(Check):
    """A PWM output runs at about a frequency whenever it is on, and it is on at all."""

    name: str
    hertz: float
    tolerance: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the lowest and the highest frequency of the window with the band.

        The server's text gives the range itself when the frequency changed.
        """
        expected = f"{self.hertz:g} Hz +/- {self.tolerance * 100:g}%"
        window = observed.pwm_windows.get(self.name)
        if window is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        measurement = window.measurement
        if not measurement.measured:
            return Outcome(self.name, expected, _unmeasured(measurement), met=False)
        low, high = self.hertz * (1 - self.tolerance), self.hertz * (1 + self.tolerance)
        met = measurement.frequency_min_hz >= low and measurement.frequency_max_hz <= high
        return Outcome(self.name, expected, measurement.frequency_text, met=met)


@dataclass(frozen=True)
class StaysOff(Check):
    """A PWM output is off for the whole window."""

    name: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Look at how long it was on."""
        expected = "off the whole window"
        window = observed.pwm_windows.get(self.name)
        if window is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        measurement = window.measurement
        if measurement.on_us > 0:
            return Outcome(self.name, expected, measurement.on_text or "on", met=False)
        return Outcome(self.name, expected, "off", met=True)


@dataclass(frozen=True)
class ReachesDuty(Check):
    """A PWM output gets to a duty while on, and does so in time."""

    name: str
    duty: float
    tolerance: float
    within_seconds: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Find the first state on and within tolerance, and say how long it took."""
        expected = (
            f"duty {_percent(self.duty)} +/- {_percent(self.tolerance)} "
            f"within {self.within_seconds:g} s"
        )
        window = observed.pwm_windows.get(self.name)
        if window is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        states = [state for state in _states(window) if state.enabled]
        if not states:
            return Outcome(self.name, expected, "off the whole window", met=False)
        arrived = [state for state in states if abs(state.duty - self.duty) <= self.tolerance]
        if not arrived:
            closest = min(states, key=lambda state: abs(state.duty - self.duty))
            seen = f"never closer than {_percent(closest.duty)}"
            return Outcome(self.name, expected, seen, met=False)
        took = (arrived[0].sim_us - window.start_us) / MICROSECONDS_PER_SECOND
        seen = f"reached after {took:.4g} s"
        return Outcome(self.name, expected, seen, met=took <= self.within_seconds)


def _states(window: PwmWindow) -> list[PwmChange]:
    """The output's states over the window: the one it began in, then each change."""
    start = window.start
    first = PwmChange(start.pwm_id, window.start_us, start.enabled, start.duty, start.period_ns)
    return [first, *window.changes]
