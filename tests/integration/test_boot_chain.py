"""The boot chain test firmware of looper, updated and checked from a test (Pro).

The board starts stage 0, which jumps through stage 1 into the application
in slot A. A test writes a built image into slot B, puts it on trial in the
boot state, resets, and expects slot B to hold that image and to run it.

Needs a looper-docs checkout beside this one and a C compiler, and skips
without them. ``LOOPER_FIXTURES`` points at the fixtures elsewhere. Pro is
unlocked by looper-core's development switch, as in its own tests.
"""

from __future__ import annotations

import shutil
import zlib
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "boot_chain" / "looper.toml"

BOOT_STATE_MAGIC, BOOT_STATE = 0xB5B5B5B5, 0x12000
SLOT_A, ON_TRIAL = 0, 1


@pytest.fixture
def simulation(monkeypatch: pytest.MonkeyPatch) -> Iterator[looper.Simulation]:
    """The boot chain firmware and its images, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    monkeypatch.setenv("LOOPER_DEV_EDITION", "pro")
    with looper.run(DEFINITION, virtual=True, looper_cli=server_command()) as started:
        yield started


def _boot_state(active: int, trial: int) -> bytes:
    words = (BOOT_STATE_MAGIC, active, trial, 0)
    return b"".join(word.to_bytes(4, "little") for word in words)


def test_the_board_jumps_through_its_stages_into_app_a(simulation: looper.Simulation) -> None:
    simulation.advance(0.05)

    lives = simulation.lives()

    assert [(life.image, life.partition) for life in lives] == [
        ("stage0", "stage0"),
        ("stage1@1.0", "stage1_a"),
        ("app@2.0", "app_a"),
    ]
    assert [life.entered_by for life in lives[1:]] == ["jump", "jump"]
    assert [(life.cause, life.ended_by) for life in lives[:2]] == [("", "jump")] * 2
    assert lives[2].is_running


def test_an_update_written_into_b_on_trial_runs_after_a_reset(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    flash = simulation.flash()
    flash.partition("app_b").write_image("app@2.1")
    flash.write(BOOT_STATE, _boot_state(SLOT_A, ON_TRIAL), raw=True)
    check = simulation.expect()
    check.flash().partition("app_b").is_valid("app@2.1")
    check.flash().partition("app_a").is_valid("app@2.0")
    simulation.reset()

    report = check.evaluate(for_seconds=0.05)

    assert report, report.summary
    assert simulation.lives()[-1].image == "app@2.1"


def test_the_images_are_listed_with_their_variants(simulation: looper.Simulation) -> None:
    images = simulation.images()

    assert "app@2.1-unconfirmed" in [image.ref for image in images]
    assert all(image.built for image in images)


COPY_UPDATE = 4


def test_a_confirmed_update_is_expected_as_the_way_the_board_went(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    simulation.flash().partition("app_b").write_image("app@2.1")
    simulation.flash().write(BOOT_STATE, _boot_state(SLOT_A, ON_TRIAL), raw=True)
    check = simulation.expect()
    check.boot_chain().went("stage0", "stage1_a", "app_b")
    simulation.reset()

    report = check.evaluate(for_seconds=0.05)

    assert report, report.summary
    assert simulation.otp().read(0, 1) == b"\x01"
    assert simulation.boot_chains()[-1].started_by == "pin"


def test_a_power_cut_in_the_middle_of_an_update_leaves_b_invalid_and_a_runs(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    simulation.power_cut(after_bytes=8192, during="flash.write", off_for_us=5000, seed=1)
    simulation.toggle_pin(COPY_UPDATE)
    simulation.advance(0.012)
    simulation.toggle_pin(COPY_UPDATE)
    check = simulation.expect()
    check.boot_chain().went("stage0", "stage1_a", "app_a")
    check.flash().partition("app_b").is_invalid()

    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary


def _copy_update(sim: looper.Simulation) -> None:
    """Hold the update button long enough for A to copy itself into B."""
    sim.toggle_pin(COPY_UPDATE)
    sim.advance(0.012)
    sim.toggle_pin(COPY_UPDATE)


#: The bytes of app@2.0 that A copies first: its 64-byte header and 8 KiB payload.
#: A cut past them leaves B whole, but never put on trial.
IMAGE_BYTES = 64 + 8192


def test_power_cuts_in_turn_through_the_update_never_leave_b_bootable(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    points = []

    points_in_turn = looper.sweep_power_cuts(
        simulation, _copy_update, total_bytes=IMAGE_BYTES, every=4096, off_for_us=5000
    )
    for point in points_in_turn:
        check = simulation.expect()
        check.flash().partition("app_b").is_invalid()
        check.boot_chain().went("stage0", "stage1_a", "app_a")
        report = check.evaluate(for_seconds=0.1)
        assert report, f"after {point} bytes: {report.summary}"
        points.append(point)

    assert points == [0, 4096, 8192]


def test_the_run_state_says_the_armed_cut_until_it_is_disarmed(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    simulation.power_cut(after_bytes=4096, during="flash.write")
    armed = simulation.run_state().power_cut_text
    simulation.reset("pin")
    simulation.advance(0.02)
    after_the_reset = simulation.run_state().power_cut_text
    simulation.disarm_power_cut()
    simulation.advance(0.001)

    assert armed == "power cut armed: after 4096 bytes of a flash write"
    assert after_the_reset == armed
    assert simulation.run_state().power_cut_text == ""


APP_A = 0x6000


def _make_app_a_unknown(simulation: looper.Simulation) -> None:
    """Give app_a's header an identity no build has and mend its CRC: a valid unknown image."""
    header = bytearray(simulation.flash().read(APP_A, 64))
    header[20] ^= 0xFF
    header[60:64] = zlib.crc32(bytes(header[:60])).to_bytes(4, "little")
    simulation.flash().write(APP_A, bytes(header), raw=True)


def test_a_standing_board_s_flash_is_read_and_an_image_written_before_the_reset(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.05)
    _make_app_a_unknown(simulation)
    simulation.reset("pin")
    with pytest.raises(looper.SimulationRefusedError):
        simulation.advance(0.05)

    stood = simulation.flash().read(APP_A, 4)
    simulation.flash().partition("app_a").write_image("app@2.0")
    simulation.reset("pin")
    simulation.advance(0.05)

    assert stood == b"LIMG"
    assert simulation.lives()[-1].image == "app@2.0"
    assert simulation.run_state().hold_reason == ""
