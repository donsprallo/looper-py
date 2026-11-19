"""The device as a block diagram on blinky, run in looper-srv (#7).

blinky's board code attaches an AS8510 to SPI1 at chip select 0 and an
MCP23008 to I2C1 at 0x20; the board names both as wired in board code. A
value the signal graph drives onto the button pin is that pin's driver, and
the taps count their exchanges while the simulation runs (looper-srv#33).

Needs a looper-docs checkout beside this one, a C compiler, and a
looper-srv that describes the board; skips without them.
``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky, built, started on a held clock and attached to, for this module alone."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        if "board" not in started.description.capabilities:
            pytest.skip("the server describes no board")
        yield started


def test_the_as8510_hangs_on_spi1_at_its_chip_select(simulation: looper.Simulation) -> None:
    tap = simulation.board().bus("SPI1").tap("AS8510")

    assert tap.text == "CS 0"
    assert tap.device.hand_wired


def test_the_mcp23008_hangs_on_i2c1_at_0x20(simulation: looper.Simulation) -> None:
    board = simulation.board()
    tap = board.bus("I2C1").tap("MCP23008")

    assert tap.text == "0x20"
    assert any(note.node_key == tap.device.key for note in board.notes)


def test_a_bus_without_a_device_says_so(simulation: looper.Simulation) -> None:
    board = simulation.board()

    assert board.bus("CAN1").taps == ()
    assert board.bus("CAN1").node.empty_text == "no devices on CAN1"
    assert board.bus("I2C1").node.empty_text == ""


def test_a_value_the_graph_drives_onto_a_pin_is_its_driver(simulation: looper.Simulation) -> None:
    button = simulation.pin("BUTTON_MODE")
    before = simulation.board()
    graph = looper.SignalGraph().value("pressed", 0.0).drive_pin(button.pin_id, "pressed")
    simulation.apply_signal_graph(graph)
    try:
        after = simulation.board()
        driven = after.port("BUTTON_MODE")
        state = simulation.board_state()
    finally:
        simulation.apply_signal_graph(looper.SignalGraph())

    assert before.port("BUTTON_MODE").reference_text == "not driven"
    assert (driven.driven_by_node_key, driven.reference_node_key) == ("pressed", "pressed")
    assert driven.driven_by_text and driven.driven_by_text in driven.reference_text
    assert after.revision > before.revision
    assert "BUTTON_MODE" in after.revision_text
    assert state.revision == after.revision


def test_the_exchange_counts_grow_while_the_simulation_runs(simulation: looper.Simulation) -> None:
    simulation.advance(0.2)
    earlier = simulation.board_state()
    simulation.advance(0.6)
    later = simulation.board_state()

    for device_key, bus in (("device:SPI1:0", "SPI1"), ("device:I2C1:0x20", "I2C1")):
        then, now = earlier.tap(device_key), later.tap(device_key)
        assert then is not None and now is not None
        assert now.exchanges > then.exchanges
        assert now.unanswered == 0
        rail = later.rail(bus)
        assert rail is not None and rail.exchanges >= now.exchanges
        assert 0 < rail.last_us <= later.sim_us
    assert later.sim_us > earlier.sim_us
