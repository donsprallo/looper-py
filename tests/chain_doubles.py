"""The chain half of the scripted inspector: fixed block states, switches written down."""

from __future__ import annotations

from looper.application.chain_port import ChainInspector
from looper.domain.model import ChainBlockState
from looper.domain.model.chain_runs import ChainExport, SequenceState
from looper.domain.model.dbc import DbcFile


class ScriptedChains(ChainInspector):
    """Answers with the block states it was given and notes every switch."""

    def __init__(self) -> None:
        self.chain_states: tuple[ChainBlockState, ...] = ()
        self.switched: list[tuple[str, bool]] = []
        self.sequence_states: list[tuple[SequenceState, ...]] = []
        self.exported: list[tuple[str, int]] = []

    def read_chains(self) -> tuple[ChainBlockState, ...]:
        return self.chain_states

    def switch_chain(self, group: str, enabled: bool) -> None:  # noqa: FBT001
        self.switched.append((group, enabled))

    def read_sequences(self) -> tuple[SequenceState, ...]:
        """The next of the states given, the last one again once they run out."""
        if len(self.sequence_states) > 1:
            return self.sequence_states.pop(0)
        return self.sequence_states[0] if self.sequence_states else ()

    def export_chain(self, group: str, run_for_us: int) -> ChainExport:
        self.exported.append((group, run_for_us))
        return ChainExport(f"test_{group}.py", "")

    def read_dbc(self, path: str) -> DbcFile:
        return DbcFile(path)
