"""Lesson 13, looper Pro: machines followed in a run, the baseline.

The firmware is that of lesson 12. ``architecture-baseline.toml`` accepts
all 8 findings, so none is new and ``looper-cli audit --architecture``
passes. The window project follows ``unit_t.mode`` in the run: after a press,
an over-temperature and cooling down, all four states are reached and
FAULT to OFF is taken once. looper-py cannot read what the window draws, so
the walk through the states is checked on the variable itself.
"""

from __future__ import annotations

import os

import pytest

import looper
from tutorial.lessons import MODE_AUTO, MODE_BOOST, MODE_FAULT, MODE_OFF, press, value_of, watch

pytestmark = pytest.mark.tutorial

# The Architect is part of looper Pro; see test_lesson_12.py.
os.environ["LOOPER_DEV_EDITION"] = "pro"

LESSON = "13-pro"


def test_the_baseline_holds_every_finding(lesson_simulation: looper.Simulation) -> None:
    findings = lesson_simulation.findings()

    assert findings.is_complete, findings.note
    assert len(findings.findings) == 8
    assert findings.new() == ()
    assert findings.fixed == ()


def test_press_overheat_and_cool_reach_every_state_and_take_fault_to_off_once(
    lesson_simulation: looper.Simulation,
) -> None:
    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    mode = watch(lesson_simulation, "unit.mode")
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=30.0))
    visited = [MODE_AUTO]

    def follow(seconds: float) -> None:
        for _ in range(round(seconds / 0.01)):
            lesson_simulation.advance(0.01)
            now = int(value_of(lesson_simulation, mode))
            if now != visited[-1]:
                visited.append(now)

    follow(1.0)
    press(lesson_simulation, 0.05)
    follow(1.0)
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=50.0))
    follow(4.0)
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=30.0))
    follow(3.0)

    assert visited == [MODE_AUTO, MODE_BOOST, MODE_FAULT, MODE_OFF]
