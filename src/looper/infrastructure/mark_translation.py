"""Resets and flash operations in the stream, from the contract's messages."""

from __future__ import annotations

from looper.domain.model import FlashMark, ResetMark
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The contract's flash operations, in the words a test uses.
FLASH_KINDS = {
    contract.FLASH_MARK_WRITE: "write",
    contract.FLASH_MARK_ERASE: "erase",
    contract.FLASH_MARK_VIOLATION: "violation",
    contract.FLASH_MARK_CUT: "cut",
}


def reset_of(event: contract.Event) -> ResetMark:
    """A reset in the stream."""
    return ResetMark(sim_us=event.sim_us, cause=event.reset.cause_text, life=event.reset.life)


def flash_mark_of(event: contract.Event) -> FlashMark:
    """A flash operation in the stream."""
    mark = event.flash
    return FlashMark(
        sim_us=event.sim_us,
        kind=FLASH_KINDS.get(mark.kind, ""),
        offset=mark.offset,
        length=mark.length,
        partition=mark.partition,
        by_client=mark.source == contract.CHANGE_SOURCE_CLIENT,
    )
