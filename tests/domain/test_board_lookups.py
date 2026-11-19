"""The board's lookups: a port and a bus by name, a bus's taps, a state by key."""

from __future__ import annotations

import pytest

from board_doubles import BOARD, STATE
from looper import BoardNodeKind


def test_a_port_is_found_by_the_name_the_firmware_gives_it() -> None:
    zc = BOARD.port("ZC")

    assert (zc.key, zc.kind, zc.is_port) == ("pin:ZC", BoardNodeKind.PIN, True)
    assert (zc.driven_by_text, zc.driven_by_node_key) == ("Comparator", "zero_cross")


def test_a_port_the_board_lacks_names_the_ones_it_has() -> None:
    with pytest.raises(KeyError, match="no port named 'GATE'; it has ZC"):
        BOARD.port("GATE")


def test_a_bus_is_not_a_port() -> None:
    with pytest.raises(KeyError, match="no port named 'SPI1'"):
        BOARD.port("SPI1")


def test_a_bus_carries_its_taps_with_where_each_device_hangs() -> None:
    (spi,) = BOARD.buses

    assert spi.name == "SPI1"
    assert (spi.tap("AS8510").text, spi.tap("AS8510").device.hand_wired) == ("CS 0", True)
    assert BOARD.bus("SPI1") == spi


def test_a_device_not_on_the_bus_names_the_ones_that_are() -> None:
    with pytest.raises(KeyError, match="no device 'MCP23008' hangs on SPI1; it has AS8510"):
        BOARD.bus("SPI1").tap("MCP23008")


def test_the_mcu_the_devices_and_the_ports_are_picked_by_kind() -> None:
    assert BOARD.mcu is not None
    assert BOARD.mcu.title == "MCU"
    assert [device.title for device in BOARD.devices] == ["AS8510"]
    assert [port.title for port in BOARD.ports] == ["ZC"]


def test_a_state_is_found_by_pin_bus_and_tap() -> None:
    assert STATE.pin("ZC") is not None
    assert STATE.pin("ZC").value == 1.0  # type: ignore[union-attr]
    assert STATE.rail("SPI1").last_us == 500_000  # type: ignore[union-attr]
    assert STATE.tap("device:SPI1:0").unanswered == 1  # type: ignore[union-attr]
    assert STATE.channel("POT") is None
