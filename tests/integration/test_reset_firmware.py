"""The reset test firmware of looper-core, reset and checked from a test.

The firmware counts its starts in retained memory, keeps a small checked
configuration in the flash, and resets itself when its reset button is
pressed. A test resets it from outside, expects resets of a cause, reads
what survives a reset, and lays broken data down in the flash on purpose.

Needs a looper-core checkout beside this one and a C compiler, and skips
without them. ``LOOPER_CORE`` points at a checkout elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

import looper
from server_under_test import CORE, server_command

DEFINITION = CORE / "tests" / "fixtures" / "reset_firmware" / "looper.toml"

RESET_BUTTON = 2
STARTS, CONFIG_STATE = 0, 8
BROKEN = 2


@pytest.fixture
def simulation() -> Iterator[looper.Simulation]:
    """The reset firmware, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no looper-core checkout at {CORE}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, looper_cli=server_command()) as started:
        yield started


def _press_reset(simulation: looper.Simulation) -> None:
    simulation.advance(0.005)
    simulation.toggle_pin(RESET_BUTTON)
    simulation.advance(0.005)
    simulation.toggle_pin(RESET_BUTTON)


def test_a_software_reset_is_expected_once_and_is_no_loop(simulation: looper.Simulation) -> None:
    simulation.advance(0.005)
    check = simulation.expect()
    check.reset(cause="software").happened_once()
    check.reset().no_loop()
    simulation.toggle_pin(RESET_BUTTON)

    report = check.evaluate(for_seconds=0.05)

    assert report, report.summary


def test_a_pin_reset_from_the_test_begins_a_new_life(simulation: looper.Simulation) -> None:
    simulation.advance(0.005)

    simulation.reset()
    simulation.advance(0.005)

    lives = simulation.lives()
    assert [life.number for life in lives] == [1, 2]
    assert lives[0].cause == "pin"
    assert simulation.retained().word(STARTS) == 2


def test_a_brown_out_from_the_test_begins_a_new_life(simulation: looper.Simulation) -> None:
    simulation.advance(0.005)

    simulation.reset("brown-out")
    simulation.advance(0.005)

    assert [life.cause for life in simulation.lives()[:1]] == ["brown-out"]


def test_the_server_refuses_a_reset_that_claims_to_be_the_firmware_s_own(
    simulation: looper.Simulation,
) -> None:
    with pytest.raises(looper.SimulationRefusedError, match="software"):
        simulation.reset("software")


def test_a_word_that_is_no_cause_is_refused_before_anything_is_sent(
    simulation: looper.Simulation,
) -> None:
    with pytest.raises(ValueError, match="not a reset cause"):
        simulation.reset("reboot")

    assert len(simulation.lives()) == 1


def test_what_a_life_left_behind_can_be_read_back(simulation: looper.Simulation) -> None:
    _press_reset(simulation)

    dump = simulation.life(1)

    assert dump.life.cause == "software"
    assert dump.memory.heap.allocations >= 1


def test_a_broken_configuration_laid_down_raw_is_found_by_the_firmware(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.005)
    config = simulation.flash().partition("config")
    broken = (0xC0FFEE00).to_bytes(4, "little") + (7).to_bytes(4, "little") + bytes(4)

    config.write(0, broken, raw=True)
    _press_reset(simulation)

    assert config.read(0, 4) == (0xC0FFEE00).to_bytes(4, "little")
    assert simulation.retained().word(CONFIG_STATE) == BROKEN


def test_the_flash_is_saved_and_loaded(simulation: looper.Simulation, tmp_path: Path) -> None:
    simulation.advance(0.005)
    flash = simulation.flash()
    saved = flash.save_file(tmp_path / "flash.bin")

    flash.erase_partition("config")
    simulation.advance(0.001)
    assert flash.partition("config").read(0, 4) == b"\xff" * 4
    flash.load_file(saved)
    simulation.advance(0.001)

    assert flash.partition("config").read(0, 4) == (0xC0FFEE00).to_bytes(4, "little")
