"""The bench part of the scripted inspector: a bench that forms after a few looks, or a refusal."""

from __future__ import annotations

from dataclasses import replace

from looper.application.ports import ProFeatureLockedError, SimulationRefusedError
from looper.domain.model.bench import (
    BenchDevice,
    BenchPhase,
    BenchState,
    JoinBusChoice,
    JoinCandidate,
    JoinCandidates,
)

FREE = "Bench is part of looper Pro - this is the free download."

#: The thermostat leading, the gateway on CAN1 with it.
ON_BENCH = BenchState(
    revision=3,
    phase=BenchPhase.ON_BENCH,
    name="lab",
    title="BENCH · one clock · thermostat leads",
    devices=(
        BenchDevice("thermostat", state_text="held", leader=True, this_device=True),
        BenchDevice("gateway", state_text="held", index=1),
    ),
)
ALONE = BenchState(revision=1)
GATEWAY = JoinCandidate(
    instance_id="gw-1",
    firmware_name="gateway",
    joinable=True,
    buses=(JoinBusChoice(7, "CAN2"), JoinBusChoice(5, "CAN1", preselected=True)),
)


class ScriptedBench:
    """Answers the bench questions; a join or leave is under way for `looks_until_done` looks."""

    def __init__(self) -> None:
        self.bench = ALONE
        self.bench_refusal = ""
        self.bench_locked = False
        self.looks_until_done = 2
        self.bench_failure = ""
        self.joins: list[tuple[int, str, int]] = []
        self._target: BenchState | None = None

    def read_bench(self) -> BenchState:
        self._refuse_bench_if_asked()
        if self._target is not None:
            self.looks_until_done -= 1
            if self.looks_until_done <= 0:
                self.bench, self._target = self._target, None
        return self.bench

    def read_join_candidates(self, bus_id: int) -> JoinCandidates:
        self._refuse_bench_if_asked()
        return JoinCandidates(title=f"Join bus {bus_id}", candidates=(GATEWAY,))

    def join_bus(self, bus_id: int, peer_instance_id: str, peer_bus_id: int) -> BenchState:
        self._refuse_bench_if_asked()
        self.joins.append((bus_id, peer_instance_id, peer_bus_id))
        return self._under_way(BenchPhase.JOINING, ON_BENCH)

    def leave_bench(self) -> BenchState:
        self._refuse_bench_if_asked()
        return self._under_way(BenchPhase.LEAVING, replace(ALONE, revision=9))

    def _under_way(self, phase: BenchPhase, done: BenchState) -> BenchState:
        """The answer at once; `done` after the looks, or back alone with the failure."""
        self.bench = replace(self.bench, phase=phase)
        self._target = done
        if self.bench_failure:
            self._target = replace(ALONE, revision=5, failed_text=self.bench_failure)
        return self.bench

    def _refuse_bench_if_asked(self) -> None:
        if self.bench_locked:
            raise ProFeatureLockedError(FREE)
        if self.bench_refusal:
            raise SimulationRefusedError(self.bench_refusal)
