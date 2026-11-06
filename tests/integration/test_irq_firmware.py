"""The interrupt test firmware of looper-core, raised and read from a test.

A button on EXTI0 counts presses in its ISR, TIM2 ticks every millisecond.
A test reads what each source did and raises one itself.

Needs a looper-core checkout beside this one and a C compiler, and skips
without them. ``LOOPER_CORE`` points at a checkout elsewhere.
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
DEFINITION = CORE / "tests" / "fixtures" / "irq_firmware" / "looper.toml"
LOOPER_CLI = ("uv", "run", "--no-sync", "--project", str(CORE), "python", "-m")
CLI_MODULE = "looper_core.presentation.cli.main"


@pytest.fixture
def simulation() -> Iterator[looper.Simulation]:
    """The interrupt firmware, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no looper-core checkout at {CORE}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, looper_cli=(*LOOPER_CLI, CLI_MODULE)) as started:
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
