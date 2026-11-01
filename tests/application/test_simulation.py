"""What a test does with a simulation, through the port."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import (
    Bus,
    BusMessage,
    Channel,
    ClockMode,
    Pin,
    Signal,
    Simulation,
    SimulationRefusedError,
    Variable,
)


def test_the_description_is_read_once_when_reached() -> None:
    simulation = Simulation(ScriptedInspector())

    assert simulation.firmware_name == "blinky"


def test_the_description_has_no_clock_mode_because_any_client_can_switch_it() -> None:
    simulation = Simulation(ScriptedInspector(ClockMode.PACED))

    assert not hasattr(simulation.description, "time_mode")
    assert simulation.clock_mode is ClockMode.PACED


def test_toggling_a_pin_is_left_to_the_simulation_and_says_the_level_it_set() -> None:
    inspector = ScriptedInspector()
    inspector.pins = (Pin(pin_id=3, name="BUTTON_MODE", level="high", is_drivable=True),)

    driven = Simulation(inspector).toggle_pin(3)

    assert inspector.toggled == [3]
    assert driven == "low"


def test_a_pin_the_simulation_refuses_is_a_refusal_with_its_reason() -> None:
    with pytest.raises(SimulationRefusedError, match="unknown pin, or the pin is an output"):
        Simulation(ScriptedInspector()).toggle_pin(9)


def test_time_is_advanced_in_seconds() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.advance(0.5)

    assert simulation.simulated_seconds == 0.5


def test_a_span_is_rounded_to_whole_microseconds() -> None:
    """0.57 seconds times a million is 569999.99... as a float."""
    inspector = ScriptedInspector()

    Simulation(inspector).advance(0.57)

    assert inspector.asked == ["advance 570000"]


def test_a_clock_that_runs_by_itself_cannot_be_advanced() -> None:
    simulation = Simulation(ScriptedInspector(ClockMode.PACED))

    with pytest.raises(SimulationRefusedError, match="cannot be advanced"):
        simulation.advance(0.5)


def test_a_signal_and_a_message_reach_the_simulation() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.apply_signal(10, Signal(offset=0.001))
    simulation.send_bus_message(BusMessage(bus_id=2, address=0x6FF, payload=b"\x01"))

    assert inspector.signals == [(10, Signal(offset=0.001))]
    assert inspector.messages[0].address == 0x6FF


def test_a_variable_is_watched_written_and_let_go() -> None:
    inspector = ScriptedInspector()
    inspector.variables = (Variable(7, "config.gain", "gain", "uint", 1, 0x2000, is_writable=True),)
    simulation = Simulation(inspector)

    watch = simulation.watch_variable(simulation.variables()[0].variable_id)
    simulation.write_variable(watch.channel_id, 3.0)

    assert simulation.watches() == (watch,)
    assert inspector.written == [(watch.channel_id, 3.0)]

    simulation.remove_watch(watch.channel_id)

    assert simulation.watches() == ()


def test_a_variable_the_catalogue_lacks_is_refused() -> None:
    with pytest.raises(SimulationRefusedError, match="no variable 9"):
        Simulation(ScriptedInspector()).watch_variable(9)


def test_closing_lets_go_once_and_stops_what_was_started() -> None:
    inspector = ScriptedInspector()
    stopped: list[str] = []

    with Simulation(inspector, on_close=lambda: stopped.append("stopped")) as simulation:
        simulation.close()

    assert inspector.closed == 1
    assert stopped == ["stopped"]


def test_a_channel_and_a_bus_are_found_by_name() -> None:
    inspector = ScriptedInspector()
    inspector.channels = (Channel(10, "SHUNT", "V", "input", 0.0, is_drivable=True),)
    inspector.buses = (Bus(2, "can", "CAN2", 500_000, accepts_messages=True),)
    simulation = Simulation(inspector)

    assert simulation.channel("SHUNT").channel_id == 10
    assert simulation.bus("CAN2").bus_id == 2


def test_a_name_nothing_has_says_which_names_there_are() -> None:
    inspector = ScriptedInspector()
    inspector.pins = (
        Pin(pin_id=1, name="LED_STATUS", level="low", is_drivable=False),
        Pin(pin_id=3, name="BUTTON_MODE", level="high", is_drivable=True),
    )

    with pytest.raises(SimulationRefusedError, match="it has BUTTON_MODE, LED_STATUS"):
        Simulation(inspector).pin("BUTTON")
