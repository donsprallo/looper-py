"""The individual things one can expect of a running firmware."""

from __future__ import annotations

from looper.domain.checks.boot_checks import BootChainWent, PartitionHolds
from looper.domain.checks.bus_checks import (
    BusCarriedAtLeast,
    BusNothingRefused,
    MessageCount,
    MessageFilter,
    MessageRate,
)
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
from looper.domain.checks.profile_checks import HeaviestFunctionIs
from looper.domain.checks.reset_checks import NoFlashViolation, NoResetLoop, ResetHappened

__all__ = [
    "BootChainWent",
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
    "HeaviestFunctionIs",
    "MessageCount",
    "MessageFilter",
    "MessageRate",
    "NeverAllocates",
    "NoFlashViolation",
    "NoResetLoop",
    "PartitionHolds",
    "ResetHappened",
    "NothingLeaked",
    "StackNoDeeperThan",
    "StackStaysBelow",
]
