"""The time model of a run, chosen at the start and changed by a restart, against looper-srv.

blinky names no ``[time]``, so it runs on ``fixed`` unless the test chooses.
A restart on another model needs no build; a plain restart keeps a model
chosen deliberately; a value out of range is refused while the simulation
runs on.

Needs a looper-docs checkout beside this one and a C compiler, and skips without them.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from looper.application.ports import SimulationRefusedError
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky on adaptive with a largest step of 250 µs, on a held clock."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    started = looper.run(
        DEFINITION,
        virtual=True,
        server=server_command(),
        time_model="adaptive",
        time_params={"max_step_us": 250},
    )
    with started:
        yield started


def test_the_run_starts_on_the_model_asked_for(simulation: looper.Simulation) -> None:
    model = simulation.time_model

    assert model is not None
    assert (model.name, model.origin, model.parameter("max_step_us")) == (
        "adaptive",
        "command_line",
        250,
    )
    assert (
        model.summary_text == "adaptive · min_step_us=1 · max_step_us=250 · time_read_cost_ns=1000"
    )
    assert [one.name for one in simulation.time_models][:2] == ["fixed", "adaptive"]


def test_a_restart_on_another_model_begins_at_0_s_and_a_plain_one_keeps_it(
    simulation: looper.Simulation,
) -> None:
    simulation.advance(0.01)

    notice = simulation.restart(time_model="fixed", time_params={"step_us": 100})

    assert notice.endswith("time model fixed 100 µs (was adaptive)"), notice
    assert simulation.simulated_seconds < 0.01
    simulation.restart()
    model = simulation.time_model
    assert model is not None
    assert (model.short_text, model.origin) == ("fixed 100 µs", "restart")


def test_a_value_out_of_range_is_refused_and_the_simulation_runs_on(
    simulation: looper.Simulation,
) -> None:
    before = simulation.time_model

    with pytest.raises(SimulationRefusedError, match="step_us takes a whole number from 1 to"):
        simulation.restart(time_model="fixed", time_params={"step_us": 0})

    assert simulation.time_model == before


def test_the_model_of_looper_toml_comes_back_on_request(simulation: looper.Simulation) -> None:
    simulation.restart(from_definition=True)

    model = simulation.time_model
    assert model is not None
    assert (model.name, model.origin) == ("fixed", "default")
    assert simulation.run_state().clock_mode is looper.ClockMode.HELD
