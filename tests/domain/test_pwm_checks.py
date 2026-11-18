"""The checks of a PWM output and of a pin's pulses, and what their failures say."""

from __future__ import annotations

from looper.domain.checks.pin_checks import PinFrequencyBetween, PulseWidthBetween
from looper.domain.checks.pwm_checks import DutyBetween, PwmFrequency, ReachesDuty, StaysOff
from looper.domain.model import Observation
from looper.domain.model.pwm import (
    PinMeasurement,
    PwmChange,
    PwmMeasurement,
    PwmOutput,
    PwmOutputs,
    PwmWindow,
)

MOTOR = PwmOutput(1, "MOTOR", enabled=True, duty=0.375, frequency_hz=20_000.0)
LED = PwmOutput(2, "LED")
#: MOTOR over 0 .. 40 ms: 37.5 % at 20 kHz, then 50 % from 20 ms.
MOTOR_MEASURED = PwmMeasurement(
    1,
    0,
    40_000,
    measured=True,
    duty=0.4375,
    duty_min=0.375,
    duty_max=0.5,
    frequency_hz=20_000.0,
    frequency_min_hz=20_000.0,
    frequency_max_hz=20_000.0,
    on_us=40_000,
    duty_text="43.8 % (37.5 % – 50.0 %)",
    frequency_text="20.0 kHz",
    on_text="on 40.00 ms of 40.00 ms",
)
OFF_MEASURED = PwmMeasurement(2, 0, 40_000, note="off the whole stretch")
#: SERVO over 0 .. 60 ms: high 1.5 ms of every 20 ms, one pulse 1.6 ms.
SERVO_MEASURED = PinMeasurement(
    1,
    0,
    60_000,
    measured=True,
    pulses=3,
    high_width_min_us=1500,
    high_width_max_us=1600,
    periods=2,
    period_min_us=19_900,
    period_max_us=20_100,
)


def _motor(*changes: PwmChange, start: PwmOutput = MOTOR) -> PwmWindow:
    return PwmWindow(start, 0, changes, MOTOR_MEASURED)


def _observed(*windows: PwmWindow, pins: dict[str, PinMeasurement] | None = None) -> Observation:
    return Observation(
        samples=(),
        exchanges=(),
        timings=(),
        elapsed_seconds=0.04,
        pwm_outputs=PwmOutputs(outputs=(MOTOR, LED)),
        pwm_windows={window.start.name: window for window in windows},
        pin_measurements=pins or {},
        pin_names=("SERVO", "LED"),
    )


def test_a_duty_inside_its_range_passes_and_one_that_leaves_it_fails_with_the_range() -> None:
    observed = _observed(_motor())

    assert DutyBetween("MOTOR", 0.1, 0.9).evaluate(observed).met
    failed = DutyBetween("MOTOR", 0.1, 0.45).evaluate(observed)
    assert not failed.met
    assert failed.line == (
        "FAIL  MOTOR: expected duty within 10 % .. 45 %, saw duty 43.8 % (37.5 % – 50.0 %)"
    )


def test_an_output_that_was_off_the_whole_window_has_no_duty_and_says_why() -> None:
    observed = _observed(PwmWindow(LED, 0, (), OFF_MEASURED))

    failed = DutyBetween("LED", 0.0, 1.0).evaluate(observed)

    assert (failed.met, failed.observed) == (False, "off the whole stretch")


def test_an_output_the_contract_does_not_list_names_the_ones_it_does() -> None:
    failed = DutyBetween("MOTR", 0.0, 1.0).evaluate(_observed(_motor()))

    assert failed.observed == "no PWM output named 'MOTR'; the contract lists MOTOR, LED"


def test_a_frequency_inside_its_tolerance_passes_and_one_outside_fails() -> None:
    observed = _observed(_motor())

    assert PwmFrequency("MOTOR", 20_000, 0.01).evaluate(observed).met
    failed = PwmFrequency("MOTOR", 10_000, 0.01).evaluate(observed)
    assert failed.line == "FAIL  MOTOR: expected 10000 Hz +/- 1%, saw 20.0 kHz"


def test_an_output_on_for_a_while_does_not_stay_off_and_says_how_long() -> None:
    assert StaysOff("LED").evaluate(_observed(PwmWindow(LED, 0, (), OFF_MEASURED))).met
    failed = StaysOff("MOTOR").evaluate(_observed(_motor()))
    assert (failed.met, failed.observed) == (False, "on 40.00 ms of 40.00 ms")


def test_a_duty_is_reached_at_the_change_that_brings_it() -> None:
    observed = _observed(_motor(PwmChange(1, 20_000, enabled=True, duty=0.5)))

    reached = ReachesDuty("MOTOR", 0.5, 0.001, 0.03).evaluate(observed)
    late = ReachesDuty("MOTOR", 0.5, 0.001, 0.01).evaluate(observed)

    assert (reached.met, reached.observed) == (True, "reached after 0.02 s")
    assert not late.met


def test_the_duty_the_window_starts_with_is_reached_at_once() -> None:
    reached = ReachesDuty("MOTOR", 0.375, 0.001, 0.0).evaluate(_observed(_motor()))

    assert (reached.met, reached.observed) == (True, "reached after 0 s")


def test_a_duty_only_set_while_off_is_not_reached() -> None:
    observed = _observed(_motor(PwmChange(1, 20_000, enabled=False, duty=0.5)))

    failed = ReachesDuty("MOTOR", 0.5, 0.001, 1.0).evaluate(observed)

    assert (failed.met, failed.observed) == (False, "never closer than 37.5 %")


def test_an_output_off_the_whole_window_reaches_nothing() -> None:
    failed = ReachesDuty("LED", 0.25, 0.001, 1.0).evaluate(
        _observed(PwmWindow(LED, 0, (), OFF_MEASURED))
    )

    assert failed.observed == "off the whole window"


def test_pulses_inside_their_range_pass_and_a_longer_one_fails_with_the_widths() -> None:
    observed = _observed(pins={"SERVO": SERVO_MEASURED})

    assert PulseWidthBetween("SERVO", 1000, 2000).evaluate(observed).met
    failed = PulseWidthBetween("SERVO", 1000, 1550).evaluate(observed)
    assert failed.line == (
        "FAIL  SERVO: expected every high pulse within 1000 .. 1550 us, "
        "saw 1500 .. 1600 us over 3 pulses"
    )


def test_a_pin_without_a_whole_pulse_fails_with_the_server_s_note() -> None:
    quiet = PinMeasurement(3, 0, 60_000, note="no edge in the stretch")
    observed = _observed(pins={"LED": quiet})

    failed = PulseWidthBetween("LED", 1, 2).evaluate(observed)

    assert (failed.met, failed.observed) == (False, "no edge in the stretch")


def test_every_period_has_to_fit_the_frequency_range() -> None:
    observed = _observed(pins={"SERVO": SERVO_MEASURED})

    assert PinFrequencyBetween("SERVO", 49.0, 51.0).evaluate(observed).met
    failed = PinFrequencyBetween("SERVO", 49.9, 50.1).evaluate(observed)
    assert failed.observed == "49.75 .. 50.25 Hz over 2 periods"
    assert not failed.met


def test_a_pin_the_firmware_did_not_register_names_the_ones_it_did() -> None:
    failed = PinFrequencyBetween("SERV0", 49.0, 51.0).evaluate(_observed())

    assert failed.observed == "no pin named 'SERV0'; the firmware registered LED, SERVO"
