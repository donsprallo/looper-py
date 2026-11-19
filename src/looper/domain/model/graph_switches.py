"""Switching parts of the applied signal graph, and the switches the event stream records.

A switch names groups and single blocks with the state each is to have; the
server takes them all in one step at one microsecond, so that a swap -- one
variant off, the other on -- never passes through a moment with both or
with neither. Who may switch what, and two writers of a label left on, is
the server's to refuse.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GraphPartSwitch:
    """One group, or one block on its own, and whether it is to be on.

    Exactly one of `group_key` and `node_key` names the part.

    Attributes:
        group_key: The group switched, with every block in it.
        node_key: The block switched on its own.
        enabled: On or off.
    """

    group_key: str = ""
    node_key: str = ""
    enabled: bool = True


@dataclass(frozen=True)
class SwitchTime:
    """When a switch takes effect: now, at a microsecond, or some microseconds from now.

    Attributes:
        at_us: The simulated microsecond it takes effect at; None for none.
        after_us: Microseconds from where the server accepts it; None for none.
    """

    at_us: int | None = None
    after_us: int | None = None


@dataclass(frozen=True)
class GraphSwitchMark:
    """A group or a single block of the graph switched, as the event stream records it.

    It follows the runtime's record of the switch under the same
    ``event_seq``, so the number does not tell two events apart.

    Attributes:
        sim_us: When it switched.
        event_seq: Its place in the stream, shared with the record before it.
        group_key: The group switched; empty when a block was switched alone.
        node_key: The block switched alone; empty for a group.
        enabled: Whether it went on.
        by_text: Who switched it: ``chain "Mains loss"``, ``a client``.
    """

    sim_us: int
    event_seq: int
    group_key: str = ""
    node_key: str = ""
    enabled: bool = False
    by_text: str = ""
