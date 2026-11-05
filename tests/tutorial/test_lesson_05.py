"""Lesson 5, a control loop with a model of its own.

``models/room.py`` is a room heated by a load and cooled by the fan. In the
signal graph a constant 40 W heats it, the firmware's ``FAN_DUTY`` cools it,
and its temperature is what ``TEMP_SENSOR`` reads. A P controller with
kp = 10 %/K holds ``setpoint``: at 35 °C the room settles at 35.31 °C, and
after a step to 28 °C at 29.18 °C, within 0.2 K after about 5 s. A P
controller leaves that error.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import room_in_the_loop, watch

pytestmark = pytest.mark.tutorial

LESSON = "05-control-loop"


def test_the_project_offers_its_room_model(lesson_simulation: looper.Simulation) -> None:
    room = lesson_simulation.model("Room")

    assert room.origin == "project"
    assert room.problem == ""
    assert room.inputs == ("heat", "duty")


def test_the_room_settles_above_the_first_setpoint(lesson_simulation: looper.Simulation) -> None:
    room_in_the_loop(lesson_simulation)
    lesson_simulation.advance(90.0)

    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    check = lesson_simulation.expect()
    check.channel(sensor, "TEMP_SENSOR").stays_between(35.2, 35.4)
    report = check.evaluate(for_seconds=5.0)
    assert report, report.summary


def test_after_a_step_from_35_to_28_degrees_it_settles_within_30_seconds(
    lesson_simulation: looper.Simulation,
) -> None:
    room_in_the_loop(lesson_simulation)
    lesson_simulation.advance(90.0)

    lesson_simulation.write_variable(watch(lesson_simulation, "setpoint"), 28.0)
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    check = lesson_simulation.expect()
    check.channel(sensor, "TEMP_SENSOR").reaches(29.18, tolerance=0.2, within_seconds=30.0)
    report = check.evaluate(for_seconds=30.0)
    assert report, report.summary

    settled = lesson_simulation.expect()
    settled.channel(sensor, "TEMP_SENSOR").stays_between(29.0, 29.4)
    report = settled.evaluate(for_seconds=5.0)
    assert report, report.summary
