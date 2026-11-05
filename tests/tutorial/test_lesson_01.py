"""Lesson 1, the first simulation: an LED and a button.

The LED toggles every 500 ms, so it blinks twice a second; while the button
is held it toggles every 100 ms. The generated adapter drives the pins
itself from the contract's roles, so the lesson has no device model.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import pin_level

pytestmark = pytest.mark.tutorial

LESSON = "01-led-and-button"


def test_the_led_changes_twice_a_second(lesson_simulation: looper.Simulation) -> None:
    lesson_simulation.advance(1.0)

    check = lesson_simulation.expect()
    check.call("adapter_fan_gpio_set").happened_at(2.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)

    assert report, report.summary


def test_with_the_button_held_it_blinks_five_times_as_fast(
    lesson_simulation: looper.Simulation,
) -> None:
    button = lesson_simulation.pin("BUTTON_MODE").pin_id
    assert lesson_simulation.toggle_pin(button) == "low"  # active low: pressed
    lesson_simulation.advance(1.0)

    check = lesson_simulation.expect()
    check.call("adapter_fan_gpio_set").happened_at(10.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)

    assert report, report.summary
    assert pin_level(lesson_simulation, "BUTTON_MODE") == "low"
