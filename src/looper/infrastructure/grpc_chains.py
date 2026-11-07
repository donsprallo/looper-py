"""The chain calls over gRPC, mixed into `GrpcInspector`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.chain_port import ChainInspector
from looper.domain.model.chain_blocks import ChainBlockState
from looper.infrastructure import chain_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

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
