"""The DMA test firmware of looper-core, read and checked from a test.

USART2 receives by circular DMA until its line is idle. A test sends it
bytes and reads where the transfer stands; with the licence it checks that
the firmware leaves the running buffer alone, which PEEK breaks. ADC1 scans
AIN0 every millisecond into a circular buffer whose halves are averaged.

Needs a looper-core checkout beside this one and a C compiler, and skips
without them. ``LOOPER_CORE`` points at a checkout elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from looper.domain.model.requests import BusMessage, Signal
from server_under_test import CORE, server_command

DEFINITION = CORE / "tests" / "fixtures" / "dma_firmware" / "looper.toml"
#: The switch that reads ahead in the running buffer, and USART2's bus.
PEEK, USART2_BUS = 1, 2


@pytest.fixture
def pro_simulation(monkeypatch: pytest.MonkeyPatch) -> Iterator[looper.Simulation]:
    """The DMA firmware with run findings unlocked, as a checkout unlocks them."""
    monkeypatch.setenv("LOOPER_DEV_EDITION", "pro")
    if not DEFINITION.is_file():
        pytest.skip(f"no looper-core checkout at {CORE}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, looper_cli=server_command()) as started:
        yield started


def test_bytes_sent_to_the_uart_stand_in_the_buffer(pro_simulation: looper.Simulation) -> None:
    pro_simulation.advance(0.002)

    pro_simulation.send_bus_message(BusMessage(USART2_BUS, 0, bytes(range(1, 41))))
    pro_simulation.advance(0.02)

    channel = pro_simulation.dma().channel("USART2_RX")
    assert (channel.position, channel.buffer_name, channel.guard) == (40, "rx_buf", "precise")


def test_a_read_ahead_in_the_running_buffer_fails_its_check(
    pro_simulation: looper.Simulation,
) -> None:
    pro_simulation.advance(0.002)
    check = pro_simulation.expect()
    check.dma("USART2_RX").not_accessed_while_running()
    check.dma("USART2_RX").no_overrun()
    pro_simulation.toggle_pin(PEEK)

    accessed, overrun = check.evaluate(for_seconds=0.005).outcomes

    assert not accessed.met
    assert accessed.observed == "The firmware read USART2_RX's buffer while the channel ran"
    assert overrun.met


def test_the_adc_scans_its_input_into_the_buffer_lap_after_lap(
    pro_simulation: looper.Simulation,
) -> None:
    pro_simulation.apply_signal(0, Signal(offset=1.65))
    check = pro_simulation.expect()
    check.dma("ADC1").no_overrun()
    check.dma("ADC1").not_accessed_while_running()

    report = check.evaluate(for_seconds=0.07)

    adc = pro_simulation.dma().channel("ADC1")
    assert (adc.peripheral_text, adc.mode, adc.width) == ("ADC 0 -> adc_buf", "circular", 2)
    assert adc.laps >= 2
    assert all(outcome.met for outcome in report.outcomes)
