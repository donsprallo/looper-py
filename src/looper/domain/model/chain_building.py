"""The builder steps of a signal graph's event half, apart from its signal half.

`SignalGraph` takes these steps on; each returns a new graph with one more
block, link or group. An action given ``after=`` is linked to that block's
``fires`` output at once.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Self

from looper.domain.model.chain_blocks import (
    BusReply,
    BusSend,
    ChainGroup,
    EventBlock,
    EventLink,
    Hold,
    Mark,
    SetPin,
)
from looper.domain.model.triggers import (
    BusReceived,
    BusTimeout,
    Edge,
    EdgeWhile,
    Pattern,
    Quiet,
    TriggerCondition,
    Value,
    Width,
)

#: The block kind of each condition, by the contract's name.
CONDITION_KINDS: dict[type, str] = {
    Edge: "pin_edge",
    EdgeWhile: "pin_edge",
    Pattern: "pin_pattern",
    Width: "pulse_width",
    Quiet: "quiet",
    Value: "variable_value",
    BusReceived: "bus_received",
    BusTimeout: "bus_timeout",
}


class ChainBuilding:
    """Builder steps for conditions, actions, links and groups."""

    event_blocks: tuple[EventBlock, ...]
    event_links: tuple[EventLink, ...]
    groups: tuple[ChainGroup, ...]

    def when(
        self, key: str, condition: TriggerCondition, group: str = "", min_gap_us: int = 0
    ) -> Self:
        """Add a condition: it fires at the simulated instant it becomes true."""
        kind = CONDITION_KINDS[type(condition)]
        return self._with_block(EventBlock(key, kind, condition, group, min_gap_us), "")

    def send(self, key: str, message: BusSend, after: str = "", group: str = "") -> Self:
        """Add a bus send: fixed bytes on a CAN or UART bus."""
        return self._with_block(EventBlock(key, "bus_send", message, group), after)

    def reply(self, key: str, answer: BusReply, after: str = "", group: str = "") -> Self:
        """Add a bus reply: answers the message a Bus received fired on (looper Pro)."""
        return self._with_block(EventBlock(key, "bus_reply", answer, group), after)

    def set_pin(self, key: str, action: SetPin, after: str = "", group: str = "") -> Self:
        """Add a Set pin: an input set high or low, or pressed for a time."""
        return self._with_block(EventBlock(key, "set_pin", action, group), after)

    def mark(self, key: str, text: str, after: str = "", group: str = "") -> Self:
        """Add a marker with a text on Logic's ruler."""
        return self._with_block(EventBlock(key, "mark", Mark(text), group), after)

    def hold(self, key: str, after_us: int = 0, after: str = "", group: str = "") -> Self:
        """Add a hold: the simulation holds `after_us` after the event."""
        return self._with_block(EventBlock(key, "hold", Hold(after_us), group), after)

    def link(self, from_node: str, to_node: str, from_port: int = 0, to_port: int = 0) -> Self:
        """Pass the events of one block's output to another block's input."""
        link = EventLink(from_node, to_node, from_port, to_port)
        return replace(self, event_links=(*self.event_links, link))  # type: ignore[type-var]

    def group(self, key: str, name: str, enabled: bool = True) -> Self:
        """Name a group: a chain with a switch; blocks join it by its key."""
        return replace(self, groups=(*self.groups, ChainGroup(key, name, enabled)))  # type: ignore[type-var]

    def _with_block(self, block: EventBlock, after: str) -> Self:
        graph = replace(self, event_blocks=(*self.event_blocks, block))  # type: ignore[type-var]
        return graph.link(after, block.key) if after else graph
