"""Waiting for a join or a leave of a bench to go through.

The server answers `JoinBus` and `LeaveBench` at once; then both devices are
built, both servers restart, and the connections drop and come back, as at a
restart. What is asked here is asked again on the same connection until the
bench reaches the phase wanted, or the server says why it did not
(`failed_text`), so that a test goes on with the bench, not with a gap.
"""

from __future__ import annotations

import time

from looper.application.bench_port import BenchInspector
from looper.application.ports import Inspector, SimulationRefusedError, SimulationUnreachableError
from looper.domain.model.bench import BenchPhase, BenchState

#: How long to wait between two looks at a join or a leave under way.
BENCH_POLL_SECONDS = 0.25


def settled_bench(
    inspector: BenchInspector, answered: BenchState, wanted: BenchPhase, timeout_s: float
) -> BenchState:
    """The bench once the join or leave that was answered with `answered` reached `wanted`.

    Raises:
        SimulationRefusedError: If the join or the leave did not go through;
            the message is the server's `failed_text`.
        TimeoutError: If the bench did not get there in time.
    """
    _refuse_if_failed(answered)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        state = _looked_at(inspector)
        if state is not None and _arrived(state, wanted):
            _refuse_if_failed(state)
            return state
        time.sleep(BENCH_POLL_SECONDS)
    raise TimeoutError(f"the bench did not reach {wanted.value} within {timeout_s:g} s")


def answering(inspector: Inspector, timeout_s: float) -> None:
    """Return once the device answers again; its server may say the bench before it does.

    Raises:
        TimeoutError: If it does not answer in time.
    """
    deadline = time.monotonic() + timeout_s
    while True:
        try:
            inspector.run_state()
            inspector.read_buses()
        except SimulationUnreachableError:
            if time.monotonic() > deadline:
                raise TimeoutError("the device did not answer again in time") from None
            time.sleep(BENCH_POLL_SECONDS)
        else:
            return


def _arrived(state: BenchState, wanted: BenchPhase) -> bool:
    """Whether the bench got where it was asked to, or the server gave up on it.

    A server that gave up is out of its joining or leaving phase with a
    sentence; the restarts in between show neither.
    """
    if state.phase == wanted:
        return True
    under_way = state.phase in (BenchPhase.JOINING, BenchPhase.LEAVING)
    return not under_way and bool(state.failed_text)


def _refuse_if_failed(state: BenchState) -> None:
    """A state that says the request did not go through, as a refusal."""
    if state.failed_text:
        raise SimulationRefusedError(state.failed_text)


def _looked_at(inspector: BenchInspector) -> BenchState | None:
    """The bench, or None while the connection is down for the restart."""
    try:
        return inspector.read_bench()
    except SimulationUnreachableError:
        return None
