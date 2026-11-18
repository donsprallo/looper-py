"""PWM outputs and a pin's pulses, read and expected through the port."""

from __future__ import annotations

from dataclasses import replace

import pytest

from doubles import ScriptedInspector
from looper import Pin, Simulation, SimulationRefusedError
from looper.application.expectations import Expectations
from looper.domain.model.pwm import PinMeasurement, PwmChange, PwmMeasurement

MOTOR_MEASURED = PwmMeasurement(
    1,
    0,
    40_000,
    measured=True,
    duty_min=0.375,
    duty_max=0.5,
    frequency_min_hz=20_000.0,
    frequency_max_hz=20_000.0,
    on_us=40_000,
    duty_text="43.8 % (37.5 % – 50.0 %)",
)
SERVO = Pin(pin_id=1, name="SERVO", level="low", is_drivable=False)
SERVO_MEASURED = PinMeasurement(
    1, 0, 40_000, measured=True, pulses=2, high_width_min_us=1500, high_width_max_us=1500
)


@pytest.fixture
def inspector() -> ScriptedInspector:
    """A firmware whose MOTOR goes from 37.5 % to 50 % at 20 ms, with a servo pulse of 1.5 ms."""
    built = ScriptedInspector()
    built.pwm_measurements = {1: MOTOR_MEASURED}
    built.pwm_changes = (PwmChange(1, 20_000, enabled=True, duty=0.5),)
    built.pins = (SERVO,)
    built.pin_measurements = {1: SERVO_MEASURED}
    return built


def test_a_pwm_is_read_by_its_name_with_the_server_s_text(inspector: ScriptedInspector) -> None:
    motor = Simulation(inspector).pwm("MOTOR")

    assert (motor.duty, motor.frequency_hz, motor.enabled) == (0.375, 20_000.0, True)
    assert motor.text == "20.0 kHz · 37.5 % · center"


def test_a_pwm_the_contract_does_not_list_is_refused_with_the_ones_it_does(
    inspector: ScriptedInspector,
) -> None:
    with pytest.raises(SimulationRefusedError, match="no PWM output named 'FAN'; it lists MOTOR"):
        Simulation(inspector).pwm("FAN")


def test_a_server_without_pwm_outputs_refuses_to_read_one(inspector: ScriptedInspector) -> None:
    inspector.description = replace(inspector.description, capabilities=())

    with pytest.raises(SimulationRefusedError, match=r"no PWM outputs \(CAPABILITY_PWM\)"):
        Simulation(inspector).pwm("MOTOR")


def test_a_window_measures_its_outputs_and_pins_over_exactly_its_stretch(
    inspector: ScriptedInspector,
) -> None:
    inspector.run = replace(inspector.run, now_us=10_000)
    check = Expectations(inspector)
    check.pwm("MOTOR").duty_between(0.1, 0.9)
    check.pin("SERVO").pulse_width_between(1, 2, unit="ms")

    report = check.evaluate(for_seconds=0.04)

    assert report, report.summary
    assert inspector.measure_asks == [("pwm", 1, 10_000, 50_000), ("pin", 1, 10_000, 50_000)]


def test_a_failed_pwm_expectation_says_what_was_measured(inspector: ScriptedInspector) -> None:
    check = Expectations(inspector)
    check.pwm("MOTOR").duty_between(0.1, 0.45)
    check.pwm("MOTOR").frequency(10_000, tol=0.01)

    report = check.evaluate(for_seconds=0.04)

    assert not report
    assert "saw duty 43.8 % (37.5 % – 50.0 %)" in report.summary
    assert "expected 10000 Hz +/- 1%, saw" in report.summary
    assert [ask[0] for ask in inspector.measure_asks] == ["pwm"]


def test_a_duty_reached_by_a_change_in_the_window_counts_from_the_window_s_start(
    inspector: ScriptedInspector,
) -> None:
    check = Expectations(inspector)
    check.pwm("MOTOR").reaches_duty(0.5, within_s=0.03)

    report = check.evaluate(for_seconds=0.04)

    assert report, report.summary
    assert report.outcomes[0].observed == "reached after 0.02 s"


def test_the_outputs_are_read_before_the_recording_is_cleared(
    inspector: ScriptedInspector,
) -> None:
    """After the clear the server's log no longer holds the change that set the duty."""
    read_before: list[str] = []
    reading = inspector.read_pwms

    def read_pwms() -> object:
        read_before.append(inspector.asked[-1] if inspector.asked else "nothing")
        return reading()

    inspector.read_pwms = read_pwms  # type: ignore[method-assign]
    check = Expectations(inspector)
    check.pwm("MOTOR").stays_off()

    check.evaluate(for_seconds=0.01)

    assert read_before == ["nothing"]


def test_a_server_that_does_not_measure_pins_refuses_the_window(
    inspector: ScriptedInspector,
) -> None:
    inspector.description = replace(inspector.description, capabilities=("pwm",))
    check = Expectations(inspector)
    check.pin("SERVO").frequency_between(49.0, 51.0)

    with pytest.raises(SimulationRefusedError, match="CAPABILITY_PIN_MEASURE"):
        check.evaluate(for_seconds=0.04)


def test_a_pulse_width_in_an_unknown_unit_is_refused_before_the_window(
    inspector: ScriptedInspector,
) -> None:
    with pytest.raises(ValueError, match="us, ms or s, not min"):
        Expectations(inspector).pin("SERVO").pulse_width_between(1, 2, unit="min")
