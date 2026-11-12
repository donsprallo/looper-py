"""The restart part of the scripted simulation: a restart and the time model it runs on.

A restart asked for is done at the next look, unless a refusal or a failed
build was scripted; the model asked for becomes the one running, as the
server would report it.
"""

from __future__ import annotations

from collections.abc import Mapping

from looper.application.ports import SimulationUnreachableError
from looper.application.restart_port import RestartInspector
from looper.domain.model import ActiveTimeModel, RestartStep


class ScriptedRestarts(RestartInspector):
    """Restarts from scripted answers, each one written down."""

    def __init__(self) -> None:
        self.restart = RestartStep(phase="running", generation=0)
        self.restarts_asked: list[tuple[bool, str | None, dict[str, float], bool]] = []
        self.refuse_with = ""
        self.build_fails = False
        self.looks_while_restarting = 0
        self.time_model_now: ActiveTimeModel | None = None

    def ask_restart(
        self,
        rebuild: bool,  # noqa: FBT001
        time_model: str | None,
        time_params: Mapping[str, float],
        from_definition: bool,  # noqa: FBT001
    ) -> RestartStep:
        self.restarts_asked.append((rebuild, time_model, dict(time_params), from_definition))
        if self.refuse_with:
            return RestartStep(
                phase="running", generation=self.restart.generation, refused_text=self.refuse_with
            )
        if self.build_fails:
            failed = RestartStep(phase="running", generation=self.restart.generation)
            self.restart = RestartStep(
                **{**failed.__dict__, "build_failed": True, "build_summary": "1 error"}
            )
            return RestartStep(phase="building", generation=self.restart.generation)
        self._restarted(time_model, time_params)
        return RestartStep(phase="restarting", generation=self.restart.generation - 1)

    def _restarted(self, time_model: str | None, time_params: Mapping[str, float]) -> None:
        if time_model is not None:
            parameters = tuple(time_params.items())
            self.time_model_now = ActiveTimeModel(
                time_model, parameters, "restart", time_model, time_model
            )
        generation = self.restart.generation + 1
        self.restart = RestartStep(
            phase="running", generation=generation, done_text="Restarted at 0 s"
        )

    def observe_restart(self) -> RestartStep:
        if self.restarts_asked and self.looks_while_restarting > 0:
            self.looks_while_restarting -= 1
            raise SimulationUnreachableError("the connection dropped")
        return self.restart
