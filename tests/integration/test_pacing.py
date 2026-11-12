"""Pacing, running at full speed and holding again, against the server.

A pace above one runs the simulation faster than real time: looper-srv sends
the ratio to the runtime in thousandths, and the runtime lets the simulated
clock run ahead of the host's by that factor (``looper_pacer.c``). Needs a
looper-docs checkout beside this one and a C compiler, and skips without them.
"""

from __future__ import annotations

import shutil
import time
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky on a held clock."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        yield started


def test_a_pace_above_one_runs_ahead_of_real_time_and_hold_stops_it(
    simulation: looper.Simulation,
) -> None:
    before = simulation.simulated_seconds

    simulation.pace(10.0)
    paced = simulation.run_state()
    time.sleep(0.5)
    simulation.hold()
    held = simulation.simulated_seconds

    assert (paced.clock_mode, paced.pace_ratio) == (looper.ClockMode.PACED, 10.0)
    assert held - before > 1.0
    assert simulation.clock_mode is looper.ClockMode.HELD
    assert simulation.simulated_seconds == held


def test_full_speed_is_no_pace_and_hold_takes_it_back(simulation: looper.Simulation) -> None:
    simulation.run_at_max()
    running = simulation.run_state()
    simulation.hold()

    assert (running.clock_mode, running.pace_ratio) == (looper.ClockMode.MAX, 0.0)
    assert simulation.clock_mode is looper.ClockMode.HELD
