"""Restarting a simulation, on its time model or on another, and waiting for the new one."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import Simulation
from looper.application.ports import SimulationRefusedError
from looper.domain.model import ActiveTimeModel, Description, TimeModel


def test_a_restart_on_another_model_asks_for_it_and_the_run_then_reports_it() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    notice = simulation.restart(time_model="adaptive", time_params={"max_step_us": 500})

    assert inspector.restarts_asked == [(False, "adaptive", {"max_step_us": 500}, False)]
    assert notice == "Restarted at 0 s"
    model = simulation.time_model
    assert model is not None
    assert (model.name, model.parameter("max_step_us"), model.origin) == (
        "adaptive",
        500,
        "restart",
    )


def test_a_plain_restart_names_no_model_so_that_the_server_keeps_the_one_running() -> None:
    inspector = ScriptedInspector()

    Simulation(inspector).restart()

    assert inspector.restarts_asked == [(False, None, {}, False)]


def test_a_restart_on_the_model_of_looper_toml_says_so() -> None:
    inspector = ScriptedInspector()

    Simulation(inspector).restart(from_definition=True, rebuild=True)

    assert inspector.restarts_asked == [(True, None, {}, True)]


def test_a_model_the_server_refuses_is_a_refusal_with_its_sentence() -> None:
    inspector = ScriptedInspector()
    inspector.refuse_with = "max_step_us takes a whole number from 1 to 1 000 000."

    with pytest.raises(SimulationRefusedError, match="max_step_us takes a whole number"):
        Simulation(inspector).restart(time_model="adaptive", time_params={"max_step_us": 0})


def test_a_build_that_fails_leaves_the_simulation_running_and_says_what_the_compiler_said() -> None:
    inspector = ScriptedInspector()
    inspector.build_fails = True

    with pytest.raises(SimulationRefusedError, match="the build failed: 1 error"):
        Simulation(inspector).restart(rebuild=True, timeout_s=2.0)


def test_the_connection_that_drops_during_the_restart_is_asked_again() -> None:
    inspector = ScriptedInspector()
    inspector.looks_while_restarting = 2

    assert Simulation(inspector).restart() == "Restarted at 0 s"
    assert inspector.looks_while_restarting == 0


def test_parameters_without_a_model_are_refused_before_anything_is_asked() -> None:
    inspector = ScriptedInspector()

    with pytest.raises(ValueError, match="time_params need a time_model"):
        Simulation(inspector).restart(time_params={"step_us": 100})

    assert inspector.restarts_asked == []


def test_the_description_is_read_again_after_a_restart() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)
    fixed = TimeModel(name="fixed", description="", source="built in", built_in=True)
    inspector.description = Description(
        contract_version=3, firmware_name="blinky", time_models=(fixed,)
    )

    simulation.restart()

    assert [model.name for model in simulation.time_models] == ["fixed"]


def test_a_server_that_predates_time_models_reports_none() -> None:
    assert Simulation(ScriptedInspector()).time_model is None
    assert (
        ActiveTimeModel("fixed", (("step_us", 250),), "default", "", "").parameter("max_step_us")
        is None
    )
