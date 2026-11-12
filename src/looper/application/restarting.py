"""Restarting a simulation and waiting until the new one answers.

The server answers a restart at once; the old simulation goes, the
connection drops, and the new one comes back from 0 s. What is asked here is
asked again on the same connection until the server says the restart is done
-- its generation went up and it runs -- so that a test goes on with the new
simulation, not with a gap.
"""

from __future__ import annotations

import time
from collections.abc import Mapping

from looper.application.ports import SimulationRefusedError, SimulationUnreachableError
from looper.application.restart_port import RestartInspector
from looper.domain.model import RestartStep

#: How long to wait between two looks at a restart under way.
RESTART_POLL_SECONDS = 0.1


def restart_simulation(
    inspector: RestartInspector,
    *,
    rebuild: bool,
    time_model: str | None,
    time_params: Mapping[str, float],
    from_definition: bool,
    timeout_s: float,
) -> str:
    """Restart and wait for the new simulation; what the server says it did.

    Raises:
        SimulationRefusedError: If the server refused the time model, or the
            build failed; the old simulation then runs on.
        TimeoutError: If the new simulation did not answer in time.
    """
    before = inspector.observe_restart().generation
    asked = inspector.ask_restart(rebuild, time_model, time_params, from_definition)
    if asked.refused_text:
        raise SimulationRefusedError(asked.refused_text)
    done = _settled(inspector, before, rebuild=rebuild, deadline=time.monotonic() + timeout_s)
    if done.generation > before:
        return done.done_text
    if done.refused_text:
        raise SimulationRefusedError(done.refused_text)
    raise SimulationRefusedError(
        f"the build failed: {done.build_summary}; the simulation runs on as it was"
    )


def _settled(
    inspector: RestartInspector, before: int, *, rebuild: bool, deadline: float
) -> RestartStep:
    """The restart's step once it runs again: restarted, or left as it was by its build.

    Only a rebuild can end without a restart: its build failed, or the new
    build lacks the time model asked for.
    """
    while time.monotonic() < deadline:
        step = _looked_at(inspector)
        if step is not None and _restarted_or_left(step, before, rebuild=rebuild):
            return step
        time.sleep(RESTART_POLL_SECONDS)
    raise TimeoutError("the restarted simulation did not answer in time")


def _restarted_or_left(step: RestartStep, before: int, *, rebuild: bool) -> bool:
    """Whether the new simulation runs, or a rebuild left the old one running."""
    if step.phase != "running":
        return False
    return step.generation > before or (rebuild and (step.build_failed or bool(step.refused_text)))


def _looked_at(inspector: RestartInspector) -> RestartStep | None:
    """Where the restart stands, or None while the connection is down."""
    try:
        return inspector.observe_restart()
    except SimulationUnreachableError:
        return None
