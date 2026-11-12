"""Time models and restarts, from the contract's messages into this library's values.

Every text is the server's and is passed on as it is.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from looper.domain.model import ActiveTimeModel, RestartStep, TimeModel, TimeModelParameter
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: Where the model in force comes from, by the contract's numbers.
ORIGINS = {
    contract.TIME_MODEL_ORIGIN_DEFAULT: "default",
    contract.TIME_MODEL_ORIGIN_DEFINITION: "definition",
    contract.TIME_MODEL_ORIGIN_COMMAND_LINE: "command_line",
    contract.TIME_MODEL_ORIGIN_RESTART: "restart",
}

#: The phases of a restart, by the contract's numbers.
PHASES = {
    contract.RESTART_PHASE_RUNNING: "running",
    contract.RESTART_PHASE_BUILDING: "building",
    contract.RESTART_PHASE_RESTARTING: "restarting",
}


def time_models_of(messages: Iterable[contract.TimeModelView]) -> tuple[TimeModel, ...]:
    """The models a description lists, in its order."""
    return tuple(_model_of(one) for one in messages)


def _model_of(message: contract.TimeModelView) -> TimeModel:
    return TimeModel(
        name=message.name,
        description=message.description_text,
        source=message.source_text,
        built_in=message.built_in,
        parameters=tuple(_parameter_of(one) for one in message.parameters),
        problem=message.problem_text,
    )


def _parameter_of(message: contract.TimeModelParameterView) -> TimeModelParameter:
    return TimeModelParameter(
        name=message.name,
        title=message.title_text,
        description=message.description_text,
        unit=message.unit,
        default=message.default_value,
        lowest=message.lowest if message.HasField("lowest") else None,
        highest=message.highest if message.HasField("highest") else None,
    )


def active_time_model_of(state: contract.RunState) -> ActiveTimeModel | None:
    """The model a run state reports; None from a server that predates time models."""
    if not state.HasField("time_model"):
        return None
    model = state.time_model
    return ActiveTimeModel(
        name=model.name,
        parameters=tuple((one.name, one.value) for one in model.parameters),
        origin=ORIGINS.get(model.origin, "default"),
        short_text=model.short_text,
        summary_text=model.summary_text,
        origin_text=model.origin_text,
        toml_text=model.toml_text,
    )


def restart_request(
    rebuild: bool,  # noqa: FBT001
    time_model: str | None,
    time_params: Mapping[str, float],
    from_definition: bool,  # noqa: FBT001
) -> contract.RestartRequest:
    """The request: no model keeps the one running, `from_definition` asks for looper.toml's."""
    if from_definition:
        return contract.RestartRequest(
            rebuild=rebuild, time_model=contract.TimeModelChoice(from_definition=True)
        )
    if time_model is None:
        return contract.RestartRequest(rebuild=rebuild)
    choice = contract.TimeModelChoice(name=time_model, parameters=dict(time_params))
    return contract.RestartRequest(rebuild=rebuild, time_model=choice)


def restart_step_of(view: contract.RestartView) -> RestartStep:
    """Where a restart stands."""
    return RestartStep(
        phase=PHASES.get(view.phase, "running"),
        generation=view.generation,
        refused_text=view.refused_text,
        refused_parameter=view.refused_parameter,
        build_failed=view.last_build.failed,
        build_summary=view.last_build.summary_text,
        done_text=view.done_text,
    )
