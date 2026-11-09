"""The chain calls over gRPC, mixed into `GrpcInspector`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.chain_port import ChainInspector
from looper.domain.model.chain_blocks import ChainBlockState
from looper.domain.model.chain_runs import ChainExport, SequenceState
from looper.domain.model.dbc import DbcFile, DbcMessage, DbcSignal
from looper.infrastructure import chain_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.scenario_translation import sequence_states_of

EMPTY = contract.Empty()


class GrpcChainCalls(ChainInspector):
    """The chains and a group's switch, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    @staticmethod
    def _taken(ack: contract.Ack) -> None:
        raise NotImplementedError

    def read_chains(self) -> tuple[ChainBlockState, ...]:
        """Every event block, in the server's words."""
        return chain_translation.block_states_of(self._call(self._stub.ObserveChains, EMPTY))

    def switch_chain(self, group: str, enabled: bool) -> None:  # noqa: FBT001
        """Switch one group on or off."""
        request = contract.ChainGroupSwitch(group_key=group, enabled=enabled)
        self._taken(self._call(self._stub.SwitchChainGroup, request))

    def read_sequences(self) -> tuple[SequenceState, ...]:
        """Every Sequence, in the server's words."""
        return sequence_states_of(self._call(self._stub.ObserveChains, EMPTY))

    def export_chain(self, group: str, run_for_us: int) -> ChainExport:
        """One group's chain as a pytest (looper Pro)."""
        request = contract.PytestExportRequest(group_key=group, run_for_us=run_for_us)
        written = self._call(self._stub.ExportChainAsPytest, request)
        return ChainExport(written.file_name, written.text, tuple(written.warnings))

    def read_dbc(self, path: str) -> DbcFile:
        """A DBC file, read by the server."""
        return dbc_file_of(self._call(self._stub.ReadDbc, contract.DbcRequest(path=path)))


def dbc_file_of(view: contract.DbcView) -> DbcFile:
    """The file as the domain keeps it."""
    return DbcFile(
        view.path, tuple(_message_of(message) for message in view.messages), view.problem
    )


def _message_of(view: contract.DbcMessageView) -> DbcMessage:
    signals = tuple(_signal_of(signal) for signal in view.signals)
    return DbcMessage(view.name, view.address, view.extended, view.length, view.cycle_us, signals)


def _signal_of(view: contract.DbcSignalView) -> DbcSignal:
    return DbcSignal(
        name=view.name,
        start_bit=view.start_bit,
        length=view.length,
        big_endian=view.big_endian,
        is_signed=view.is_signed,
        scale=view.scale,
        offset=view.offset,
        unit=view.unit,
        minimum=view.minimum if view.HasField("minimum") else None,
        maximum=view.maximum if view.HasField("maximum") else None,
    )
