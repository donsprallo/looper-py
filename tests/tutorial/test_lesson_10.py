"""Lesson 10, the source and the debugger.

The leak and the slow median of lesson 9 are fixed. New is the ``name``
command, with an off-by-one in ``mode_set_name``: a name of exactly 16
characters leaves no room for the terminating zero, which lands on the
field after the name, ``unit.mode``, and switches the fan to OFF.

Not checked here, because looper-py has no way to: the breakpoint at
``mode.c:63`` and the line counts of the counting build.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import (
    MODE_AUTO,
    MODE_OFF,
    room_in_the_loop,
    type_into_terminal,
    value_of,
    watch,
)

pytestmark = pytest.mark.tutorial

LESSON = "10-source-and-debugger"


def test_a_name_of_15_characters_is_taken(lesson_simulation: looper.Simulation) -> None:
    mode = watch(lesson_simulation, "unit.mode")
    lesson_simulation.advance(0.5)

    assert type_into_terminal(lesson_simulation, "name abcdefghijklmno\n") == "ok\n"

    assert value_of(lesson_simulation, mode) == MODE_AUTO
    assert type_into_terminal(lesson_simulation, "status\n").startswith(
        "abcdefghijklmno: mode=auto"
    )


def test_a_name_of_exactly_16_characters_switches_the_fan_off(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "unit.mode")
    lesson_simulation.advance(0.5)

    assert type_into_terminal(lesson_simulation, "name 0123456789abcdef\n") == "ok\n"
    lesson_simulation.advance(0.05)

    assert value_of(lesson_simulation, mode) == MODE_OFF
    assert lesson_simulation.channel("FAN_DUTY").value == 0.0


def test_the_leak_of_lesson_9_is_gone(lesson_simulation: looper.Simulation) -> None:
    uart = lesson_simulation.bus("UART1").bus_id
    lesson_simulation.advance(1.0)

    for _ in range(2):
        lesson_simulation.send_bus_message(looper.BusMessage(uart, 0, b"bogus\n" * 10))
    check = lesson_simulation.expect()
    check.memory().nothing_leaked()
    report = check.evaluate(for_seconds=1.0)

    assert report, report.summary


def test_the_median_no_longer_leads_the_profile(lesson_simulation: looper.Simulation) -> None:
    room_in_the_loop(lesson_simulation)
    lesson_simulation.advance(2.0)
    lesson_simulation.clear_measurements()
    lesson_simulation.advance(5.0)

    heaviest = lesson_simulation.profile().heaviest_first("firmware")

    assert heaviest[0].name == "app_step"
    assert "sort" not in {one.name for one in heaviest}
