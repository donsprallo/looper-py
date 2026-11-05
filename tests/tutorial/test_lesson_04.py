"""Lesson 4, analog: a signal on the sensor, the filter, the fan's curve.

``TEMP_SENSOR`` is sampled at 1 kHz and smoothed by a first order low pass
of 0.5 s into ``TEMP_FILTERED``. ``FAN_DUTY`` rises from 0 % at 25 °C to
100 % at 40 °C and is clamped beyond. Above 40 °C the LED blinks fast.

The lesson's generator is a sine of 30 °C ± 15 °C at 0.2 Hz. The plan had
± 10 °C, which after the filter stays between 21.5 °C and 38.5 °C: it never
reaches 40 °C and the duty cycle never 100 %.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import sample

pytestmark = pytest.mark.tutorial

LESSON = "04-analog"

LESSON_SINE = looper.Signal(waveform="sine", offset=30.0, amplitude=15.0, frequency_hz=0.2)


def test_the_filtered_temperature_follows_the_sine_smaller_and_later(
    lesson_simulation: looper.Simulation,
) -> None:
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    lesson_simulation.apply_signal(sensor, LESSON_SINE)
    lesson_simulation.advance(5.0)

    period = sample(lesson_simulation, ("TEMP_SENSOR", "TEMP_FILTERED"), 5.0, 0.01)

    filtered = [values["TEMP_FILTERED"] for _, values in period]
    assert max(filtered) - min(filtered) == pytest.approx(25.4, abs=0.5)  # of the sensor's 30
    raw_peak = max(period, key=lambda one: one[1]["TEMP_SENSOR"])[0]
    filtered_peak = max(period, key=lambda one: one[1]["TEMP_FILTERED"])[0]
    assert (filtered_peak - raw_peak) % 5.0 == pytest.approx(0.44, abs=0.03)


def test_a_step_reaches_63_percent_after_the_time_constant(
    lesson_simulation: looper.Simulation,
) -> None:
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=20.0))
    lesson_simulation.advance(5.0)

    lesson_simulation.apply_signal(sensor, looper.Signal(offset=30.0))
    filtered = lesson_simulation.channel("TEMP_FILTERED").channel_id
    check = lesson_simulation.expect()
    check.channel(filtered, "TEMP_FILTERED").reaches(26.32, tolerance=0.05, within_seconds=0.53)
    report = check.evaluate(for_seconds=1.0)
    assert report, report.summary


def test_the_duty_cycle_is_clamped_at_0_and_100_percent(
    lesson_simulation: looper.Simulation,
) -> None:
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    duty = lesson_simulation.channel("FAN_DUTY").channel_id
    lesson_simulation.apply_signal(sensor, LESSON_SINE)
    lesson_simulation.advance(5.0)

    check = lesson_simulation.expect()
    check.channel(duty, "FAN_DUTY").stays_between(0.0, 100.0)
    check.channel(duty, "FAN_DUTY").reaches(0.0)
    check.channel(duty, "FAN_DUTY").reaches(100.0)
    report = check.evaluate(for_seconds=5.0)
    assert report, report.summary


def test_above_40_degrees_the_led_blinks_fast(lesson_simulation: looper.Simulation) -> None:
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=45.0))
    lesson_simulation.advance(1.0)

    check = lesson_simulation.expect()
    check.call("adapter_fan_gpio_set").happened_at(10.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary
