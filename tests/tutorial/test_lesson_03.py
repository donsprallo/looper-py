"""Lesson 3, variables and watches.

The debounce is fixed. The firmware keeps a status bit field, a counter of
the LED's toggles, and the blink period as a Q8 fixed point number of
seconds: 128 is 0.5 s, 25 is 0.098 s.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import MODE_AUTO, MODE_BOOST, press, value_of, watch

pytestmark = pytest.mark.tutorial

LESSON = "03-variables"


@pytest.mark.parametrize(
    ("press_seconds", "mode"),
    [(0.005, MODE_AUTO), (0.015, MODE_AUTO), (0.050, MODE_BOOST)],
)
def test_only_a_press_longer_than_the_debounce_changes_the_mode(
    lesson_simulation: looper.Simulation, press_seconds: float, mode: int
) -> None:
    status_mode = watch(lesson_simulation, "status.mode")
    lesson_simulation.advance(0.5)

    press(lesson_simulation, press_seconds)
    lesson_simulation.advance(0.1)

    assert value_of(lesson_simulation, status_mode) == mode


def test_the_toggle_count_rises_twice_a_second(lesson_simulation: looper.Simulation) -> None:
    count = watch(lesson_simulation, "toggle_count")
    lesson_simulation.advance(0.5)
    before = value_of(lesson_simulation, count)

    lesson_simulation.advance(10.0)

    assert value_of(lesson_simulation, count) - before == 20


def test_writing_25_to_the_q8_period_makes_the_led_blink_about_ten_times_a_second(
    lesson_simulation: looper.Simulation,
) -> None:
    period = watch(lesson_simulation, "blink_period_q8")
    assert value_of(lesson_simulation, period) == 128

    lesson_simulation.write_variable(period, 25)
    lesson_simulation.advance(0.5)

    check = lesson_simulation.expect()
    # 25 / 256 s is 97 ms between toggles: 10.3 changes a second.
    check.call("adapter_fan_gpio_set").happened_at(10.3, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary
