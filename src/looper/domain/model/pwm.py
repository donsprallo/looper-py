"""The firmware's PWM outputs and the pulses of a pin, as the server reports them (free).

A PWM output of contract.toml's ``[pwm.NAME]`` is a state -- period,
compare, reload, on or off -- and every change of it is one event. The
server measures duty, frequency and on time from those changes, and the
pulse widths of a pin from its recorded edges; the numbers and every text
here are the server's. Times are simulated microseconds.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.model.triggers import Polarity


@dataclass(frozen=True)
class PwmOutput:
    """One PWM output: what the contract says of it, and its state when it was read.

    Attributes:
        pwm_id: Its number, from 1 in the contract's order, which a measurement names.
        name: Its name in contract.toml, ``MOTOR``.
        enabled: Whether the output runs; off it drives no pulse.
        duty: The active part of a period, 0 to 1.
        frequency_hz: How many periods a second.
        period_ns: One period in nanoseconds.
        mean: ``duty × full_scale`` while on, 0 while off: what ``output`` carries.
        text: ``20.0 kHz · 37.5 % · center``.
        state_text: ``on``, ``off`` or ``off – not started yet``.
        detail_text: The timer, the pin, the polarity and preload in one line.
    """

    pwm_id: int
    name: str
    enabled: bool = False
    duty: float = 0.0
    frequency_hz: float = 0.0
    period_ns: int = 0
    compare: int = 0
    reload: int = 0
    timer: str = ""
    pin: str = ""
    output: str = ""
    alignment: str = "edge"
    polarity: str = "active high"
    full_scale: float = 0.0
    mean: float = 0.0
    changed_at_us: int = 0
    text: str = ""
    state_text: str = ""
    output_text: str = ""
    detail_text: str = ""


@dataclass(frozen=True)
class PwmOutputs:
    """Every PWM output in the contract's order.

    Attributes:
        outputs: The outputs; empty when the contract lists none.
        state_text: Why the list is empty, or what the states are without a
            simulation, in the server's words; else empty.
    """

    outputs: tuple[PwmOutput, ...] = ()
    state_text: str = ""

    def named(self, name: str) -> PwmOutput | None:
        """The output of that name, or None when the contract lists none such."""
        return next((output for output in self.outputs if output.name == name), None)

    @property
    def names(self) -> str:
        """The outputs' names for a sentence, or ``none at all``."""
        return ", ".join(output.name for output in self.outputs) or "none at all"


@dataclass(frozen=True)
class PwmChange:
    """One change of a PWM output's state, at a moment of the run.

    Attributes:
        pwm_id: The output that changed.
        sim_us: When the new state began.
        enabled: Whether it runs from then on.
        duty: Its duty from then on, 0 to 1.
        period_ns: Its period from then on.
    """

    pwm_id: int
    sim_us: int
    enabled: bool
    duty: float
    period_ns: int = 0


@dataclass(frozen=True)
class PwmMeasurement:
    """One output over a stretch of the run, weighed by the time each state held while on.

    Attributes:
        measured: False when it was off the whole stretch, or the stretch is
            empty; ``note`` says which.
        duty: The mean duty while on; ``duty_min`` and ``duty_max`` its range.
        frequency_hz: The mean frequency while on, with its range.
        high_width_ns: The mean active pulse while on.
        on_us: How long it was on within the stretch.
        changes: How many changes the firmware made within it.
        text: All of it in one line, ``20.0 kHz · 41.7 % (37.5 % – 50.0 %) · ...``.
        note: Why nothing was measured, or what the log no longer keeps.
    """

    pwm_id: int
    from_us: int
    to_us: int
    measured: bool = False
    duty: float = 0.0
    duty_min: float = 0.0
    duty_max: float = 0.0
    frequency_hz: float = 0.0
    frequency_min_hz: float = 0.0
    frequency_max_hz: float = 0.0
    high_width_ns: float = 0.0
    on_us: int = 0
    changes: int = 0
    duty_text: str = ""
    frequency_text: str = ""
    high_width_text: str = ""
    on_text: str = ""
    text: str = ""
    note: str = ""


@dataclass(frozen=True)
class PinMeasurement:
    """One pin over a stretch of the run, from its recorded edges in whole microseconds.

    A period runs from one rising edge to the next, a width from an edge to
    the next of the other kind; what the stretch cuts is not counted, and a
    field of a kind of pulse that did not occur is 0.

    Attributes:
        measured: False without a whole high pulse or period; ``note`` says why.
        pulses: Whole high pulses.
        periods: Rising edge to rising edge.
        frequency_hz: Of the mean period.
        duty: The mean of each high pulse over its period.
        text: All of it in one line, ``50.0 Hz · duty 7.5 % · high 1.50 ms, 2 pulses``;
            with a reference pin it begins with ``delay_text``.
        reference_pin_id: The pin the delay was measured from; None when none was asked.
        delays: Reference edges this pin answered, each one delay.
        delay_min_us: The shortest delay; ``delay_max_us`` the longest.
        delay_mean_us: Their mean.
        delays_missed: Reference edges this pin did not answer before the next one.
        delay_text: ``ZC↑ → GATE↑ 2.50 ms (2.40 ms – 2.60 ms, 50 delays)``, or
            why there is none.
    """

    pin_id: int
    from_us: int
    to_us: int
    measured: bool = False
    rising_edges: int = 0
    falling_edges: int = 0
    pulses: int = 0
    high_width_min_us: int = 0
    high_width_max_us: int = 0
    high_width_mean_us: float = 0.0
    low_width_min_us: int = 0
    low_width_max_us: int = 0
    periods: int = 0
    period_min_us: int = 0
    period_max_us: int = 0
    period_mean_us: float = 0.0
    frequency_hz: float = 0.0
    duty: float = 0.0
    high_us: int = 0
    high_width_text: str = ""
    frequency_text: str = ""
    text: str = ""
    note: str = ""
    reference_pin_id: int | None = None
    delays: int = 0
    delay_min_us: int = 0
    delay_max_us: int = 0
    delay_mean_us: float = 0.0
    delays_missed: int = 0
    delay_text: str = ""


@dataclass(frozen=True)
class PinDelay:
    """The delay from one pin's edges to another's, by the names the firmware registered.

    For each `reference_edge` of `reference`, the time to the first `edge`
    of `pin` at or after it and before the reference's next such edge.

    Attributes:
        pin: The pin that answers, ``GATE``.
        reference: The pin whose edges start each delay, ``ZC``.
        reference_edge: Which edges of the reference count.
        edge: Which edges of `pin` answer.
    """

    pin: str
    reference: str
    reference_edge: Polarity = Polarity.RISE
    edge: Polarity = Polarity.RISE


@dataclass(frozen=True)
class PwmWindow:
    """What one output did over a window: how it stood at its start, its changes, the measurement.

    Attributes:
        start: The output as it stood when the window began.
        start_us: When the window began.
        changes: Its changes within the window, oldest first.
        measurement: The server's measurement of the window.
    """

    start: PwmOutput
    start_us: int
    changes: tuple[PwmChange, ...]
    measurement: PwmMeasurement
