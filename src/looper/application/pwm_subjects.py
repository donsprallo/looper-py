"""What a test can expect of a PWM output and of the pulses on a pin (free).

Each subject has the window read what it is about: a PWM output's state at
the window's start and the server's measurement of it, or the server's
measurement of a pin's edges. A server without PWM outputs, or one that
does not measure pins, refuses the evaluation with a sentence that says so.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from looper.application.interrupt_subjects import UNITS
from looper.domain.checks.pin_checks import PinFrequencyBetween, PulseWidthBetween
from looper.domain.checks.pwm_checks import DutyBetween, PwmFrequency, ReachesDuty, StaysOff

if TYPE_CHECKING:
    from looper.application.expectations import Expectations

#: How close a duty has to come to count as reached: a tenth of a percent.
DUTY_TOLERANCE = 0.001


def _microseconds(amount: float, unit: str) -> int:
    if unit not in UNITS:
        raise ValueError(f"a pulse width is in us, ms or s, not {unit}")
    return round(amount * UNITS[unit])


class PwmExpectation:
    """What is expected of one PWM output, by its name in contract.toml."""

    def __init__(self, expectations: Expectations, name: str) -> None:
        self._expectations = expectations
        self._name = name
        expectations.reads_pwm(name)

    def duty_between(self, low: float, high: float) -> Expectations:
        """Expect the duty, 0 to 1, to stay within a range whenever the output is on."""
        return self._expectations.add(DutyBetween(self._name, low, high))

    def frequency(self, hertz: float, tol: float = 0.01) -> Expectations:
        """Expect the output to run at about a frequency; `tol` is relative, 0.01 for 1 %."""
        return self._expectations.add(PwmFrequency(self._name, hertz, tol))

    def reaches_duty(
        self, duty: float, within_s: float = float("inf"), tolerance: float = DUTY_TOLERANCE
    ) -> Expectations:
        """Expect the output to get to a duty while on, within so many seconds of the start."""
        return self._expectations.add(ReachesDuty(self._name, duty, tolerance, within_s))

    def stays_off(self) -> Expectations:
        """Expect the output to be off for the whole window."""
        return self._expectations.add(StaysOff(self._name))


class PinExpectation:
    """What is expected of the pulses on one pin, by the name the firmware registered."""

    def __init__(self, expectations: Expectations, name: str) -> None:
        self._expectations = expectations
        self._name = name
        expectations.measures_pin(name)

    def pulse_width_between(self, low: float, high: float, unit: str = "us") -> Expectations:
        """Expect every whole high pulse to last within a range, in ``us``, ``ms`` or ``s``."""
        low_us, high_us = _microseconds(low, unit), _microseconds(high, unit)
        return self._expectations.add(PulseWidthBetween(self._name, low_us, high_us))

    def frequency_between(self, low_hz: float, high_hz: float) -> Expectations:
        """Expect every whole period, rising edge to rising edge, within a frequency range."""
        return self._expectations.add(PinFrequencyBetween(self._name, low_hz, high_hz))
