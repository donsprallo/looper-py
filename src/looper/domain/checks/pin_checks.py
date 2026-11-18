"""The things one can expect of the pulses on a pin (free).

The widths and periods are the server's measurement of the pin's recorded
edges over the window, in whole microseconds, as Logic measures them: a
pulse the window cuts is not counted. Every pulse and every period has to
fit, so a single stray one fails the check and the report names the range.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome
from looper.domain.model.pwm import PinMeasurement

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
