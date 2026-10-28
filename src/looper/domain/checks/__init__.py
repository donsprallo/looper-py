"""The individual things one can expect of a running firmware."""

from __future__ import annotations

from looper.domain.checks.bus_checks import BusCarriedAtLeast, BusNothingRefused
from looper.domain.checks.call_checks import (
    CallHappened,
    CallRate,
    CallWasAnswered,
    FirmwareIsAlive,
)
from looper.domain.checks.channel_checks import ChannelReaches, ChannelStaysBetween
from looper.domain.checks.check import Check
from looper.domain.checks.memory_checks import (
    HeapStaysBelow,
    NeverAllocates,
    NothingLeaked,
    StackNoDeeperThan,
    StackStaysBelow,
)

__all__ = [
    "BusCarriedAtLeast",
    "BusNothingRefused",
    "CallHappened",
    "CallRate",
    "CallWasAnswered",
    "ChannelReaches",
    "ChannelStaysBetween",
    "Check",
    "FirmwareIsAlive",
    "HeapStaysBelow",
    "NeverAllocates",
    "NothingLeaked",
    "StackNoDeeperThan",
    "StackStaysBelow",
]
