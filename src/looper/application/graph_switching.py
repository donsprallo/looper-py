"""Switching groups and blocks of the applied signal graph, and reading its groups.

A mixin of `Simulation`, so that both files stay readable. A switch goes
out as one request however many parts it names, and the server takes it in
one step at one microsecond: a variant swap -- one group off, the other on
-- never passes through a moment with two writers of a label or none. What
may be switched, and whether a label would be left with two writers on, is
the server's to refuse; its sentence is the refusal's message.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from looper.application.event_stream import EventStream
from looper.application.expectations import MICROSECONDS_PER_SECOND
from looper.application.ports import Inspector
from looper.domain.model.chain_groups import ChainGroupState
from looper.domain.model.graph_switches import GraphPartSwitch, GraphSwitchMark, SwitchTime


class GraphSwitching:
    """Groups and single blocks of the applied graph switched without applying it again."""

    _inspector: Inspector
    _events: EventStream

    def switch_groups(
        self,
        groups: Mapping[str, bool],
        blocks: Mapping[str, bool] | None = None,
        *,
        at_s: float | None = None,
        after_s: float | None = None,
    ) -> None:
        """Switch groups, and blocks on their own, all in one step.

        ``switch_groups({"plant": False, "ideal": True})`` swaps two variants.

        Without a time it takes effect at once; `at_s` is a simulated
        second, `after_s` seconds from where the server takes it.

        Raises:
            ValueError: If both `at_s` and `after_s` are given.
            SimulationRefusedError: As a whole, for a key the applied graph
                does not have, or a label left with two writers on; the
                message is the server's sentence.
        """
        parts = (
            *(GraphPartSwitch(group_key=key, enabled=on) for key, on in groups.items()),
            *(GraphPartSwitch(node_key=key, enabled=on) for key, on in (blocks or {}).items()),
        )
        self._inspector.switch_graph_parts(parts, _switch_time(at_s, after_s))

    def switch_group(
        self,
        group: str,
        on: bool,  # noqa: FBT001 -- the switch, as the concept writes it
        *,
        at_s: float | None = None,
        after_s: float | None = None,
    ) -> None:
        """Switch one group -- its signal blocks and its chain blocks -- on or off.

        Raises:
            SimulationRefusedError: If the applied graph has no such group, or
                a label would be left with two writers on.
        """
        self.switch_groups({group: on}, at_s=at_s, after_s=after_s)

    def switch_block(
        self,
        key: str,
        on: bool,  # noqa: FBT001 -- the switch, as the concept writes it
        *,
        at_s: float | None = None,
        after_s: float | None = None,
    ) -> None:
        """Switch one signal block on or off on its own; what it feeds follows it.

        Raises:
            SimulationRefusedError: If the applied graph has no such block, or
                a label would be left with two writers on.
        """
        self.switch_groups({}, {key: on}, at_s=at_s, after_s=after_s)

    def graph_switches(self, since: int = 0) -> Iterator[GraphSwitchMark]:
        """Every recorded switch of a group or a block from event number `since` on, oldest first.

        A chain's Switch group and a client's switch alike, each with its
        microsecond and who switched it. A switch shares its ``event_seq``
        with the runtime's record before it.

        Raises:
            SimulationRefusedError: If another client cleared the recording
                while it was being read.
        """
        return self._events.graph_switches(since)

    def chain_groups(self) -> tuple[ChainGroupState, ...]:
        """Every group of the graph and of the Logic triggers, with who switched it last."""
        return self._inspector.read_chain_groups()

    def chain_group(self, key: str) -> ChainGroupState:
        """The group of that key, as the server reports it now.

        Raises:
            KeyError: If there is no such group.
        """
        for group in self.chain_groups():
            if group.key == key:
                return group
        raise KeyError(f"there is no group {key!r}")


def _switch_time(at_s: float | None, after_s: float | None) -> SwitchTime:
    """When a switch takes effect, in whole microseconds."""
    if at_s is not None and after_s is not None:
        raise ValueError("a switch takes effect at a time or after one, not both")
    return SwitchTime(
        at_us=None if at_s is None else round(at_s * MICROSECONDS_PER_SECOND),
        after_us=None if after_s is None else round(after_s * MICROSECONDS_PER_SECOND),
    )
