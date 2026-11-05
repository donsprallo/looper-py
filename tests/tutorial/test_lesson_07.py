"""Lesson 7, the logic analyzer and a trigger.

The mode is a state machine OFF, AUTO, BOOST, FAULT on ``unit.mode``. More
than 45 °C for longer than 2 s is a FAULT: the fan runs flat out, all three
mode LEDs light, and the status LED pulses 100 ms on, 400 ms off. Below
40 °C the machine goes to OFF. After a step of the sensor from 30 °C to
50 °C the filter passes 45 °C 0.695 s later, and the FAULT follows 2 s after
that. With the room model in the loop the fan keeps the room below 45 °C,
so the lesson drives the sensor from a generator.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import MODE_FAULT, MODE_OFF, pin_level, value_of, watch

pytestmark = pytest.mark.tutorial

LESSON = "07-logic-analyzer"


def overheat(simulation: looper.Simulation) -> int:
    """Settle at 30 °C, then step the sensor to 50 °C; give the step's time in microseconds."""
    sensor = simulation.channel("TEMP_SENSOR").channel_id
    simulation.apply_signal(sensor, looper.Signal(offset=30.0))
    simulation.advance(3.0)
    step_at_us = round(simulation.simulated_seconds * 1_000_000)
    simulation.apply_signal(sensor, looper.Signal(offset=50.0))
    return step_at_us


def test_the_fault_trigger_fires_once_two_seconds_after_the_filter_passes_45(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "unit.mode")
    fault = lesson_simulation.triggers.arm(
        looper.Value(mode, looper.Comparison.EQ, MODE_FAULT), mode=looper.TriggerMode.NORMAL
    )
    try:
        step_at_us = overheat(lesson_simulation)
        lesson_simulation.advance(5.0)
        fired = lesson_simulation.triggers.current(fault)
    finally:
        lesson_simulation.triggers.disarm_own()

    assert fired.fires == 1
    # 0.695 s to 45 °C, then 2 s of it.
    assert (fired.last_fired_at_us - step_at_us) / 1_000_000 == pytest.approx(2.695, abs=0.01)


def test_in_fault_the_status_led_pulses_100_ms_on_and_400_ms_off(
    lesson_simulation: looper.Simulation,
) -> None:
    overheat(lesson_simulation)
    lesson_simulation.advance(4.0)

    levels = []
    for _ in range(400):
        lesson_simulation.advance_microseconds(5_000)
        levels.append(pin_level(lesson_simulation, "LED_STATUS"))
    runs = run_lengths_ms(levels, step_ms=5)

    assert set(runs[1:-1]) == {("high", 100), ("low", 400)}
    assert all(
        pin_level(lesson_simulation, one) == "high" for one in ("LED_OFF", "LED_AUTO", "LED_BOOST")
    )
    assert lesson_simulation.channel("FAN_DUTY").value == 100.0


def test_when_the_room_has_cooled_the_machine_stops_in_off(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "unit.mode")
    overheat(lesson_simulation)
    lesson_simulation.advance(4.0)
    assert value_of(lesson_simulation, mode) == MODE_FAULT

    sensor = lesson_simulation.channel("TEMP_SENSOR").channel_id
    lesson_simulation.apply_signal(sensor, looper.Signal(offset=30.0))
    lesson_simulation.advance(3.0)

    assert value_of(lesson_simulation, mode) == MODE_OFF
    assert lesson_simulation.channel("FAN_DUTY").value == 0.0


def run_lengths_ms(levels: list[str], step_ms: int) -> list[tuple[str, int]]:
    """How long each level lasted, in order, from levels read every step."""
    runs: list[tuple[str, int]] = []
    for level in levels:
        if runs and runs[-1][0] == level:
            runs[-1] = (level, runs[-1][1] + step_ms)
        else:
            runs.append((level, step_ms))
    return runs
