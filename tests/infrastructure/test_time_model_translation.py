"""The time models and a restart, between the contract's messages and this library's values."""

from __future__ import annotations

from looper.infrastructure import time_model_translation, translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.looper_cli import RunCommand


def test_the_models_a_description_lists_keep_the_server_s_words_and_bounds() -> None:
    largest = contract.TimeModelParameterView(
        name="max_step_us",
        title_text="Largest idle step",
        unit="µs",
        default_value=500,
        lowest=1,
        highest=1e6,
    )
    views = [
        contract.TimeModelView(
            name="adaptive", source_text="built in", built_in=True, parameters=[largest]
        ),
        contract.TimeModelView(
            name="old", source_text="sim/old.c", problem_text="Could not be loaded."
        ),
    ]

    description = translation.description_of(contract.Description(time_models=views))

    adaptive, old = description.time_models
    assert (adaptive.name, adaptive.built_in, old.problem) == (
        "adaptive",
        True,
        "Could not be loaded.",
    )
    parameter = adaptive.parameters[0]
    assert (parameter.title, parameter.unit, parameter.default, parameter.highest) == (
        "Largest idle step",
        "µs",
        500,
        1e6,
    )


def test_a_parameter_without_bounds_has_none() -> None:
    view = contract.TimeModelView(
        name="mine", parameters=[contract.TimeModelParameterView(name="speed")]
    )

    (model,) = time_model_translation.time_models_of([view])

    assert (model.parameters[0].lowest, model.parameters[0].highest) == (None, None)


def test_the_run_state_reports_the_model_in_force_with_its_origin() -> None:
    model = contract.TimeModelState(
        name="adaptive",
        short_text="adaptive",
        summary_text="adaptive · max_step_us=500",
        parameters=[contract.TimeParameterValue(name="max_step_us", value=500)],
        origin=contract.TIME_MODEL_ORIGIN_COMMAND_LINE,
    )

    status = translation.run_status_of(contract.RunState(time_model=model))

    assert status.time_model is not None
    assert (status.time_model.origin, status.time_model.parameter("max_step_us")) == (
        "command_line",
        500,
    )
    assert translation.run_status_of(contract.RunState()).time_model is None


def test_a_restart_names_a_model_only_when_one_is_asked_for() -> None:
    plain = time_model_translation.restart_request(False, None, {}, False)  # noqa: FBT003
    chosen = time_model_translation.restart_request(True, "fixed", {"step_us": 100}, False)  # noqa: FBT003
    toml = time_model_translation.restart_request(False, None, {}, True)  # noqa: FBT003

    assert not plain.HasField("time_model")
    assert (chosen.rebuild, chosen.time_model.name, dict(chosen.time_model.parameters)) == (
        True,
        "fixed",
        {"step_us": 100},
    )
    assert toml.time_model.from_definition


def test_a_refusal_comes_back_with_its_parameter() -> None:
    view = contract.RestartView(refused_text="no", refused_parameter="step_us", generation=3)

    step = time_model_translation.restart_step_of(view)

    assert (step.phase, step.generation, step.refused_parameter) == ("running", 3, "step_us")


def test_the_server_is_started_on_the_model_asked_for() -> None:
    command = RunCommand(
        program=("looper-srv",), time_model="adaptive", time_params=(("max_step_us", 500),)
    )

    arguments = command.arguments()

    assert arguments[arguments.index("--time-model") + 1] == "adaptive"
    assert arguments[arguments.index("--time-param") + 1] == "max_step_us=500"
    assert "--time-model" not in RunCommand(program=("looper-srv",)).arguments()
