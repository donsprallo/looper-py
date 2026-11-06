"""Resets, lives, the retained memory and the flash, through the port."""

from __future__ import annotations

from pathlib import Path

import pytest

from doubles import ScriptedInspector
from looper import Simulation, SimulationRefusedError


def test_a_reset_from_the_test_is_a_pin_reset_unless_it_says_otherwise() -> None:
    inspector = ScriptedInspector()

    Simulation(inspector).reset()
    Simulation(inspector).reset("power-on")
    Simulation(inspector).reset("brown-out")

    assert inspector.reset_causes == ["pin", "power-on", "brown-out"]


def test_a_reset_cannot_claim_to_be_the_firmware_s_own() -> None:
    with pytest.raises(SimulationRefusedError):
        Simulation(ScriptedInspector()).reset("watchdog")


def test_a_retained_word_is_little_endian() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.retained().write(4, (0xB007B007).to_bytes(4, "little"))

    assert simulation.retained().word(4) == 0xB007B007
    assert simulation.retained().read(4, 2) == b"\x07\xb0"


def test_a_partition_is_written_from_its_own_beginning() -> None:
    inspector = ScriptedInspector()

    Simulation(inspector).flash().partition("config").write(4, b"\x00\x01", raw=True)

    assert inspector.flash_writes == [(1028, b"\x00\x01", True)]


def test_a_write_past_a_partition_s_end_is_refused_before_it_is_sent() -> None:
    inspector = ScriptedInspector()

    with pytest.raises(SimulationRefusedError, match="1024 bytes long"):
        Simulation(inspector).flash().partition("config").write(1023, b"\x00\x00")
    assert inspector.flash_writes == []


def test_an_unknown_partition_is_refused_with_its_name() -> None:
    with pytest.raises(SimulationRefusedError, match="no partition called app_b"):
        Simulation(ScriptedInspector()).flash().partition("app_b")


def test_a_saved_flash_is_loaded_back_from_a_file(tmp_path: Path) -> None:
    inspector = ScriptedInspector()
    flash = Simulation(inspector).flash()
    saved = flash.save_file(tmp_path / "flash.bin")
    inspector.flash[0] = 0

    flash.load_file(saved)

    assert inspector.flash[0] == 0xFF


def test_a_built_image_is_written_into_a_partition_by_its_name() -> None:
    inspector = ScriptedInspector()

    Simulation(inspector).flash().partition("config").write_image("app@2.1")

    assert inspector.images_written == [("config", "app@2.1")]


def test_an_image_file_is_named_to_the_server_by_its_whole_path(tmp_path: Path) -> None:
    inspector = ScriptedInspector()
    image = tmp_path / "app.limg"

    Simulation(inspector).flash().partition("config").write_image_file(image)

    assert inspector.images_written == [("config", str(image.resolve()))]
