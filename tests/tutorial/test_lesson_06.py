"""Lesson 6, buses and components.

The board reports its status on CAN every 100 ms (``0x321``) and takes a
setpoint from ``0x320``; a terminal on UART takes ``mode``, ``set`` and
``status``; three LEDs on an MCP23008 on I2C show the mode.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import pin_level, type_into_terminal

pytestmark = pytest.mark.tutorial

LESSON = "06-buses"

MODE_LEDS = ("LED_OFF", "LED_AUTO", "LED_BOOST")


def lit(simulation: looper.Simulation) -> tuple[str, ...]:
    """The mode LEDs that are on."""
    return tuple(name for name in MODE_LEDS if pin_level(simulation, name) == "high")


def test_the_status_goes_out_ten_times_a_second(lesson_simulation: looper.Simulation) -> None:
    can = lesson_simulation.bus("CAN1").bus_id
    lesson_simulation.advance(1.0)

    check = lesson_simulation.expect()
    check.bus(can, "CAN1").message(0x321, direction="outbound").happened_at(10)
    check.bus(can, "CAN1").nothing_refused()
    check.bus(lesson_simulation.bus("I2C1").bus_id, "I2C1").nothing_refused()
    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary


def test_set_28_on_the_terminal_is_answered_and_moves_the_setpoint(
    lesson_simulation: looper.Simulation,
) -> None:
    lesson_simulation.advance(0.5)

    answer = type_into_terminal(lesson_simulation, "set 28\n")
    lesson_simulation.advance(0.05)

    assert answer == "ok\n"
    assert lesson_simulation.channel("SETPOINT").value == 28.0
    assert type_into_terminal(lesson_simulation, "set 99\n") == "error\n"
    assert type_into_terminal(lesson_simulation, "status\n").startswith("mode=auto ")


def test_a_setpoint_frame_on_can_moves_the_setpoint(lesson_simulation: looper.Simulation) -> None:
    can = lesson_simulation.bus("CAN1").bus_id
    lesson_simulation.advance(0.5)

    lesson_simulation.send_bus_message(looper.BusMessage(can, 0x320, bytes([30])))
    lesson_simulation.advance(0.05)

    assert lesson_simulation.channel("SETPOINT").value == 30.0


@pytest.mark.parametrize(
    ("command", "led"),
    [("mode off\n", "LED_OFF"), ("mode auto\n", "LED_AUTO"), ("mode boost\n", "LED_BOOST")],
)
def test_the_expander_leds_show_the_mode(
    lesson_simulation: looper.Simulation, command: str, led: str
) -> None:
    lesson_simulation.advance(0.5)

    assert type_into_terminal(lesson_simulation, command) == "ok\n"
    lesson_simulation.advance(0.05)

    assert lit(lesson_simulation) == (led,)
