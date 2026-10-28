"""What a test does with a simulation, through the port."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import Bus, BusMessage, Channel, Pin, Signal, Simulation, SimulationRefusedError


def test_the_description_is_read_once_when_reached() -> None:
    simulation = Simulation(ScriptedInspector())

    assert simulation.firmware_name == "blinky"


def test_toggling_a_pin_drives_the_opposite_of_its_level_now() -> None:
    inspector = ScriptedInspector()
    inspector.pins = (Pin(pin_id=3, name="BUTTON_MODE", level="high", is_drivable=True),)

    driven = Simulation(inspector).toggle_pin(3)

    assert inspector.toggled == [(3, "high")]
    assert driven == "low"


def test_a_pin_the_firmware_never_registered_is_refused() -> None:
    with pytest.raises(SimulationRefusedError, match="no pin 9"):
        Simulation(ScriptedInspector()).toggle_pin(9)


def test_time_is_advanced_in_seconds() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.advance(0.5)

    assert simulation.simulated_seconds == 0.5


def test_a_signal_and_a_message_reach_the_simulation() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.apply_signal(10, Signal(offset=0.001))
    simulation.send_bus_message(BusMessage(bus_id=2, address=0x6FF, payload=b"\x01"))

    assert inspector.signals == [(10, Signal(offset=0.001))]
    assert inspector.messages[0].address == 0x6FF


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
