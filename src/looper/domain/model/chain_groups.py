"""A group of the graph as the server reports it: its switch, what it holds, who switched it.

A group holds chain blocks, signal blocks or both; switching it switches all
of them. Every text is the server's.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChainGroupState:
    """One group of the applied graph or of a Logic trigger, as it is now.

    Attributes:
        key: The group's key.
        name: What the graph calls it.
        enabled: Whether it is on now.
        state_text: Its chip, as the server words it.
        event_blocks: How many chain blocks it holds.
        signal_blocks: How many signal blocks it holds.
        needs_pro: It holds a part of looper Pro the licence does not unlock.
        problem_text: Why it does not run; empty when it does.
        switched_by_text: Who switched it last, when that was not the applied
            graph: ``chain "Mains loss" at 2.500000 s``; empty as applied.
        switched_at_us: When that was; 0 as applied.
        off_text: What its being off does: ``4 blocks off · SPEED gives its
            fallback 0``; empty while it is on.
    """

    key: str
    name: str = ""
    enabled: bool = True
    state_text: str = ""
    event_blocks: int = 0
    signal_blocks: int = 0
    needs_pro: bool = False
    problem_text: str = ""
    switched_by_text: str = ""
    switched_at_us: int = 0
    off_text: str = ""
