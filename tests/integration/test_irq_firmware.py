"""The interrupt test firmware of looper, raised and read from a test.

A button on EXTI0 counts presses in its ISR, TIM2 ticks every millisecond.
A test reads what each source did and raises one itself.

Needs a looper-docs checkout beside this one and a C compiler, and skips
without them. ``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "irq_firmware" / "looper.toml"


@pytest.fixture
def simulation(monkeypatch: pytest.MonkeyPatch) -> Iterator[looper.Simulation]:
    """The interrupt firmware, built, started on a held clock and attached to, without Pro."""
    monkeypatch.setenv("LOOPER_DEV_EDITION", "free")
    monkeypatch.setenv("LOOPER_LICENSE", "no licence here")
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        yield started


def test_a_timer_of_one_millisecond_ticks_ten_times_in_ten_milliseconds(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.010)

    tick = simulation.interrupts().source("TIM2")
    assert tick.handled == 10
    assert tick.kind_text == "timer, every 1 ms"
    assert tick.handler == "HAL_TIM_PeriodElapsedCallback"


def test_a_raised_source_runs_its_isr(simulation: looper.Simulation) -> None:
    simulation.advance(0.002)

    simulation.raise_interrupt("EXTI0")
    simulation.advance(0.001)

    button = simulation.interrupts().source("EXTI0")
    assert (button.raised, button.handled, button.latency_max_us) == (1, 1, 0)


LOCK = 2


@pytest.fixture
def pro_simulation(monkeypatch: pytest.MonkeyPatch) -> Iterator[looper.Simulation]:
    """The interrupt firmware with run findings unlocked, as a checkout unlocks them."""
    monkeypatch.setenv("LOOPER_DEV_EDITION", "pro")
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        yield started


def test_a_lock_past_the_project_s_limit_fails_its_check_and_ticks_pass_theirs(
    pro_simulation: looper.Simulation,
) -> None:
    pro_simulation.advance(0.005)
    check = pro_simulation.expect()
    check.interrupts().locked_at_most()
    check.interrupt("TIM2").handled_at_least(5)
    pro_simulation.toggle_pin(LOCK)

    report = check.evaluate(for_seconds=0.01)

    locked, ticks = report.outcomes
    assert not locked.met
    assert locked.observed == "Interrupts disabled for 2 ms (limit 1 ms)"
    assert ticks.met


def test_without_the_licence_an_interrupt_check_says_it_is_pro(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.interrupt("TIM2").never_lost()

    with pytest.raises(looper.ProFeatureLockedError, match="part of looper Pro"):
        check.evaluate(for_seconds=0.005)


def test_the_race_mode_goes_round_every_point_of_the_loop(
    pro_simulation: looper.Simulation,
) -> None:
    pro_simulation.advance(0.002)

    with pro_simulation.race("TIM2") as race:
        pro_simulation.advance(0.02)
        coverage = race.coverage()

    assert coverage.complete
    assert coverage.source == "TIM2"
    assert coverage.points_covered == coverage.points_seen > 0
