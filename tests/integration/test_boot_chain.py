"""The boot chain test firmware of looper-core, updated and checked from a test (Pro).

The board starts stage 0, which jumps through stage 1 into the application
in slot A. A test writes a built image into slot B, puts it on trial in the
boot state, resets, and expects slot B to hold that image and to run it.

Needs a looper-core checkout beside this one and a C compiler, and skips
without them. ``LOOPER_CORE`` points at a checkout elsewhere. Pro is
unlocked by looper-core's development switch, as in its own tests.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

import looper

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))
DEFINITION = CORE / "tests" / "fixtures" / "boot_chain" / "looper.toml"
LOOPER_CLI = ("uv", "run", "--no-sync", "--project", str(CORE), "python", "-m")
CLI_MODULE = "looper_core.presentation.cli.main"

BOOT_STATE_MAGIC, BOOT_STATE = 0xB5B5B5B5, 0x12000
SLOT_A, ON_TRIAL = 0, 1


@pytest.fixture
def simulation(monkeypatch: pytest.MonkeyPatch) -> Iterator[looper.Simulation]:
    """The boot chain firmware and its images, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no looper-core checkout at {CORE}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    monkeypatch.setenv("LOOPER_DEV_EDITION", "pro")
    with looper.run(DEFINITION, virtual=True, looper_cli=(*LOOPER_CLI, CLI_MODULE)) as started:
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
