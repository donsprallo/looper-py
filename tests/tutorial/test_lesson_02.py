"""Lesson 2, time: the debounce, in its first and broken version.

A debounced press switches between AUTO and BOOST, and the LED blinks five
times as fast in BOOST. The debounce of this lesson takes the time of the
last accepted change instead of the last edge, so after a quiet spell a
bounce of 5 ms is taken at once and switches the mode: the bug the reader
finds with Run for, and fixes with the lesson's fix.patch.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import MODE_AUTO, MODE_BOOST, press, value_of, watch

pytestmark = pytest.mark.tutorial

LESSON = "02-time"


def test_a_press_switches_to_boost_and_the_led_blinks_at_ten_hertz(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "mode")
    lesson_simulation.advance(0.5)

    press(lesson_simulation, 0.05)
    lesson_simulation.advance(1.0)

    assert value_of(lesson_simulation, mode) == MODE_BOOST
    check = lesson_simulation.expect()
    check.call("adapter_fan_gpio_set").happened_at(10.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary


def test_the_broken_debounce_takes_a_five_millisecond_bounce_as_a_press(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "mode")
    lesson_simulation.advance(0.5)

    press(lesson_simulation, 0.005)
    lesson_simulation.advance(0.1)
    after_one_bounce = value_of(lesson_simulation, mode)
    press(lesson_simulation, 0.005)
    lesson_simulation.advance(0.1)

    assert after_one_bounce == MODE_BOOST
    assert value_of(lesson_simulation, mode) == MODE_AUTO
