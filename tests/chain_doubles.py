"""The chain half of the scripted inspector: fixed block states, switches written down."""

from __future__ import annotations

from looper.application.chain_port import ChainInspector
from looper.domain.model import ChainBlockState


class ScriptedChains(ChainInspector):
    """Answers with the block states it was given and notes every switch."""

    def __init__(self) -> None:
        self.chain_states: tuple[ChainBlockState, ...] = ()
        self.switched: list[tuple[str, bool]] = []

    def read_chains(self) -> tuple[ChainBlockState, ...]:
        return self.chain_states

    def switch_chain(self, group: str, enabled: bool) -> None:  # noqa: FBT001
        self.switched.append((group, enabled))
