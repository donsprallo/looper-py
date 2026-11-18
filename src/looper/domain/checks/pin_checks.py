"""The things one can expect of the pulses on a pin (free).

The widths and periods are the server's measurement of the pin's recorded
edges over the window, in whole microseconds, as Logic measures them: a
pulse the window cuts is not counted. Every pulse and every period has to
fit, so a single stray one fails the check and the report names the range.
A delay from another pin's edges is measured the same way, by the server.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome
from looper.domain.model.pwm import PinDelay, PinMeasurement
from looper.domain.model.triggers import Polarity

MICROSECONDS_PER_SECOND = 1_000_000


def _missing(observed: Observation, name: str) -> str:
    known = ", ".join(sorted(observed.pin_names)) or "none at all"
    return f"no pin named {name!r}; the firmware registered {known}"


def _unmeasured(measurement: PinMeasurement) -> str:
    return measurement.note or "no whole pulse"


@dataclass(frozen=True)
class PulseWidthBetween(Check):
    """Every whole high pulse on a pin lasts within a range, and there is one at all."""

    name: str
    low_us: int
    high_us: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the shortest and the longest high pulse with the range."""
        expected = f"every high pulse within {self.low_us} .. {self.high_us} us"
        measurement = observed.pin_measurements.get(self.name)
        if measurement is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        if measurement.pulses == 0:
            return Outcome(self.name, expected, _unmeasured(measurement), met=False)
        seen = (
            f"{measurement.high_width_min_us} .. {measurement.high_width_max_us} us "
            f"over {measurement.pulses} pulses"
        )
        met = (
            measurement.high_width_min_us >= self.low_us
            and measurement.high_width_max_us <= self.high_us
        )
        return Outcome(self.name, expected, seen, met=met)


@dataclass(frozen=True)
class PinFrequencyBetween(Check):
    """Every whole period on a pin, rising edge to rising edge, is within a frequency range."""

    name: str
    low_hz: float
    high_hz: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Turn the longest and the shortest period into frequencies and compare them."""
        expected = f"every period within {self.low_hz:g} .. {self.high_hz:g} Hz"
        measurement = observed.pin_measurements.get(self.name)
        if measurement is None:
            return Outcome(self.name, expected, _missing(observed, self.name), met=False)
        if measurement.periods == 0:
            return Outcome(self.name, expected, _unmeasured(measurement), met=False)
        slowest = MICROSECONDS_PER_SECOND / measurement.period_max_us
        fastest = MICROSECONDS_PER_SECOND / measurement.period_min_us
        seen = f"{slowest:.4g} .. {fastest:.4g} Hz over {measurement.periods} periods"
        met = slowest >= self.low_hz and fastest <= self.high_hz
        return Outcome(self.name, expected, seen, met=met)


#: How an arrow names an edge, as the server's delay text does.
ARROWS = {Polarity.RISE: "↑", Polarity.FALL: "↓", Polarity.ANY: "↕"}


@dataclass(frozen=True)
class DelayBetween(Check):
    """Every edge of a reference pin is answered by the pin within a range of time.

    A reference edge the pin did not answer before the reference's next one
    fails the check as well: a gate that stays away is not in range. The
    server measures; its ``delay_text`` is what the report shows.
    """

    delay: PinDelay
    low_us: int
    high_us: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the shortest and the longest delay with the range, and count the missed."""
        subject = self._subject()
        expected = f"every delay within {self.low_us} .. {self.high_us} us"
        measurement = observed.pin_delays.get(self.delay)
        if measurement is None:
            named = (self.delay.reference, self.delay.pin)
            missing = next((one for one in named if one not in observed.pin_names), self.delay.pin)
            return Outcome(subject, expected, _missing(observed, missing), met=False)
        seen = measurement.delay_text or measurement.note or "no delay measured"
        met = (
            measurement.delays > 0
            and measurement.delays_missed == 0
            and measurement.delay_min_us >= self.low_us
            and measurement.delay_max_us <= self.high_us
        )
        return Outcome(subject, expected, seen, met=met)

    def _subject(self) -> str:
        """``ZC↑ → GATE↑``, as the server's delay text names it."""
        reference = f"{self.delay.reference}{ARROWS[self.delay.reference_edge]}"
        return f"{reference} → {self.delay.pin}{ARROWS[self.delay.edge]}"
