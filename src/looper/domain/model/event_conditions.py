"""Conditions on the firmware's life: an interrupt and a reset seen (free, also for triggers)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interrupt:
    """An interrupt source becomes pending, or with `on_entry` its handler is entered."""

    source_id: int
    on_entry: bool = False


@dataclass(frozen=True)
class ResetSeen:
    """A life begins after a reset of `cause` (the contract's numbers; 0 any cause)."""

    cause: int = 0
