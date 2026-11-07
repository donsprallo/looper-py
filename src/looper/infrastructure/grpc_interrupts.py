"""The interrupt calls over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.interrupt_port import InterruptInspector
from looper.domain.model.dma import DmaChannels
from looper.domain.model.interrupt_facts import RunFindingReading
from looper.domain.model.interrupts import Interrupts
from looper.domain.model.race import RaceCoverage
from looper.infrastructure import interrupt_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

EMPTY = contract.Empty()


class GrpcInterruptCalls(InterruptInspector):
    """The interrupt sources, the lock, and raising a source, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    @staticmethod
    def _taken(ack: contract.Ack) -> None:
        raise NotImplementedError

    def read_interrupts(self) -> Interrupts:
        """Every source and the lock."""
        report = self._call(self._stub.ObserveInterrupts, EMPTY)
        return interrupt_translation.interrupts_of(report)

    def read_run_findings(self) -> tuple[RunFindingReading, ...]:
        """The server's findings of the run."""
        listed = self._call(self._stub.ObserveRunFindings, contract.RunFindingFilter())
        return interrupt_translation.findings_of(listed)

    def read_dma(self) -> DmaChannels:
        """Every DMA channel."""
        return interrupt_translation.dma_of(self._call(self._stub.ObserveDma, EMPTY))

    def set_race(self, on: bool, source_id: int) -> RaceCoverage:  # noqa: FBT001
        """Switch the race mode."""
        request = contract.RaceRequest(on=on, source_id=source_id)
        return interrupt_translation.race_of(self._call(self._stub.SetRaceMode, request))

    def read_race(self) -> RaceCoverage:
        """What the race mode did."""
        return interrupt_translation.race_of(self._call(self._stub.ObserveRaceMode, EMPTY))

    def raise_interrupt(self, source_id: int, after_us: int = 0) -> None:
        """Make a source due, now or later."""
        request = interrupt_translation.raise_request(source_id, after_us)
        self._taken(self._call(self._stub.RaiseInterrupt, request))
