"""The PWM test firmware of looper, read and expected from a test.

MOTOR is a centre-aligned PWM of 20 kHz at 37.5 %, 50 % from 20 ms, 10 kHz
from 40 ms, off from 60 ms and on again at 70 ms. SERVO is a pin the loop
drives high for 1.5 ms of every 20 ms.

Needs a looper-docs checkout beside this one and a C compiler, and skips
without them. ``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "pwm_firmware" / "looper.toml"


@pytest.fixture
def simulation() -> Iterator[looper.Simulation]:
    """The PWM firmware, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        yield started


def test_a_pwm_is_read_with_its_duty_frequency_and_the_server_s_text(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.010)

    motor = simulation.pwm("MOTOR")

    assert (motor.enabled, motor.duty, motor.frequency_hz) == (True, 0.375, 20_000.0)
    assert motor.text == "20.0 kHz · 37.5 % · center"
    assert [output.name for output in simulation.pwms().outputs] == ["MOTOR", "LED"]


def test_the_motor_s_first_stretch_keeps_its_frequency_and_reaches_half_duty(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.pwm("MOTOR").duty_between(0.37, 0.51)
    check.pwm("MOTOR").frequency(20_000, tol=0.01)
    check.pwm("MOTOR").reaches_duty(0.5, within_s=0.025)

    report = check.evaluate(for_seconds=0.035)

    assert report, report.summary


def test_a_duty_outside_its_range_fails_with_what_the_server_measured(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.pwm("MOTOR").duty_between(0.1, 0.4)

    report = check.evaluate(for_seconds=0.035)

    assert not report
    assert "expected duty within 10 % .. 40 %, saw duty " in report.summary
    assert "50.0 %" in report.summary


def test_the_motor_switched_off_stays_off_until_it_is_started_again(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.061)

    check = simulation.expect()
    check.pwm("MOTOR").stays_off()

    assert check.evaluate(for_seconds=0.008)


def test_the_servo_pulse_is_measured_from_the_pin_s_edges(simulation: looper.Simulation) -> None:
    check = simulation.expect()
    check.pin("SERVO").pulse_width_between(1000, 2000, unit="us")
    check.pin("SERVO").frequency_between(49.0, 51.0)

    report = check.evaluate(for_seconds=0.065)

    assert report, report.summary


def test_a_servo_pulse_too_short_for_its_range_fails_with_the_widths(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.pin("SERVO").pulse_width_between(1.6, 2.0, unit="ms")

    report = check.evaluate(for_seconds=0.065)

    assert not report
    assert "expected every high pulse within 1600 .. 2000 us, saw 1500 .. 1500 us" in (
        report.summary
    )


#: Why a duty set before a window is not measured in it, for now.
FORGETS_ON_CLEAR = (
    "looper-srv forgets a PWM's state when the recording is cleared: MeasurePwm and "
    "ObservePwms then start from the contract's state (off) until the next change"
)


@pytest.mark.xfail(strict=True, reason=FORGETS_ON_CLEAR)
def test_a_duty_set_before_the_window_is_measured_in_it(simulation: looper.Simulation) -> None:
    simulation.advance(0.025)

    check = simulation.expect()
    check.pwm("MOTOR").duty_between(0.49, 0.51)

    report = check.evaluate(for_seconds=0.010)

    assert report, report.summary


@pytest.mark.xfail(strict=True, reason=FORGETS_ON_CLEAR)
def test_the_duty_the_firmware_starts_with_is_measured_in_the_first_window(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.pwm("MOTOR").duty_between(0.37, 0.38)

    report = check.evaluate(for_seconds=0.015)

    assert report, report.summary
