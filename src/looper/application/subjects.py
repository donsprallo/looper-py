"""What an expectation is about, before it says what it expects.

`check.channel(0, "P1A").reaches(1.0)` reads as a sentence because the
subject and the claim are separate objects. These are the subjects; the
claims they make are the checks of the domain.

Each of them only collects: nothing here reads the simulation, and
nothing is evaluated until the window has passed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from looper.domain.checks import (
    BusCarriedAtLeast,
    BusNothingRefused,
    CallHappened,
    CallRate,
    CallWasAnswered,
    ChannelReaches,
    ChannelStaysBetween,
    HeapStaysBelow,
    HeaviestFunctionIs,
    MessageCount,
    MessageFilter,
    MessageRate,
    NeverAllocates,
    NoFlashViolation,
    NoResetLoop,
    NothingLeaked,
    PartitionHolds,
    ResetHappened,
    StackNoDeeperThan,
    StackStaysBelow,
)
from looper.domain.model import FIRMWARE_ORIGIN

if TYPE_CHECKING:
    from looper.application.expectations import Expectations


class ChannelExpectation:
    """What is expected of one analog channel."""

    def __init__(self, expectations: Expectations, channel_id: int, name: str) -> None:
        self._expectations = expectations
        self._channel_id = channel_id
        self._name = name

    def stays_between(self, low: float, high: float) -> Expectations:
        """Expect every recorded sample to be within a range."""
        return self._expectations.add(ChannelStaysBetween(self._channel_id, self._name, low, high))

    def reaches(
        self, value: float, tolerance: float = 0.0, within_seconds: float = float("inf")
    ) -> Expectations:
        """Expect the channel to arrive at a value, and in time."""
        return self._expectations.add(
            ChannelReaches(self._channel_id, self._name, value, tolerance, within_seconds)
        )


class BusExpectation:
    """What is expected of one bus."""

    def __init__(self, expectations: Expectations, bus_id: int, name: str) -> None:
        self._expectations = expectations
        self._bus_id = bus_id
        self._name = name

    def nothing_refused(self) -> Expectations:
        """Expect everything that crossed to have been taken by something."""
        return self._expectations.add(BusNothingRefused(self._bus_id, self._name))

    def carried_at_least(self, count: int) -> Expectations:
        """Expect at least so many exchanges."""
        return self._expectations.add(BusCarriedAtLeast(self._bus_id, self._name, count))

    def message(
        self,
        address: int | None = None,
        *,
        direction: str | None = None,
        starts_with: bytes = b"",
    ) -> MessageExpectation:
        """Narrow the expectation to messages of one kind.

        ``check.bus("CAN1").message(0x321, direction="outbound").happened_at(10)``
        expects the firmware's status message ten times a second. The address
        is the CAN identifier, the I2C address or the chip select.
        """
        wanted = MessageFilter(address, direction, bytes(starts_with))
        return MessageExpectation(self._expectations, self._bus_id, self._name, wanted)


class MessageExpectation:
    """What is expected of the messages of one kind on a bus."""

    def __init__(
        self, expectations: Expectations, bus_id: int, name: str, wanted: MessageFilter
    ) -> None:
        self._expectations = expectations
        self._bus_id = bus_id
        self._name = name
        self._wanted = wanted

    def happened_at_least(self, count: int) -> Expectations:
        """Expect at least so many of them."""
        return self._add(MessageCount(self._bus_id, self._name, self._wanted, count))

    def happened_between(self, at_least: int, at_most: int) -> Expectations:
        """Expect their number to be within a range, both ends included."""
        return self._add(MessageCount(self._bus_id, self._name, self._wanted, at_least, at_most))

    def never(self) -> Expectations:
        """Expect none of them at all."""
        return self._add(MessageCount(self._bus_id, self._name, self._wanted, 0, 0))

    def happened_at(self, hertz: float, tolerance: float = 0.05) -> Expectations:
        """Expect them at about a given rate."""
        return self._add(MessageRate(self._bus_id, self._name, self._wanted, hertz, tolerance))

    def _add(self, check: MessageCount | MessageRate) -> Expectations:
        return self._expectations.add(check)


class CallExpectation:
    """What is expected of one adapter function."""

    def __init__(self, expectations: Expectations, function: str) -> None:
        self._expectations = expectations
        self._function = function

    def happened_at_least(self, count: int) -> Expectations:
        """Expect the firmware to have called it at least so many times."""
        return self._expectations.add(CallHappened(self._function, count))

    def was_answered(self) -> Expectations:
        """Expect something to implement it, rather than the zero value."""
        return self._expectations.add(CallWasAnswered(self._function))

    def happened_at(self, hertz: float, tolerance: float = 0.05) -> Expectations:
        """Expect it to have been called at about a given rate."""
        return self._expectations.add(CallRate(self._function, hertz, tolerance))


class MemoryExpectation:
    """What is expected of the heap."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations

    def never_allocates(self) -> Expectations:
        """Expect nothing to have asked the allocator for anything."""
        return self._expectations.add(NeverAllocates())

    def peak_below(self, bytes_allowed: int) -> Expectations:
        """Expect the heap never to have held more than so many bytes."""
        return self._expectations.add(HeapStaysBelow(bytes_allowed))

    def nothing_leaked(self) -> Expectations:
        """Expect everything taken over the window to have been given back."""
        return self._expectations.add(NothingLeaked())


class StackExpectation:
    """What is expected of the stack."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations

    def stays_below(self, bytes_allowed: int) -> Expectations:
        """Expect the stack never to have gone past so many host bytes."""
        return self._expectations.add(StackStaysBelow(bytes_allowed))

    def no_deeper_than(self, frames_allowed: int) -> Expectations:
        """Expect the calls never to have nested more than so deep."""
        return self._expectations.add(StackNoDeeperThan(frames_allowed))


class ProfileExpectation:
    """What is expected of where the firmware spends its time."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations

    def heaviest_is(self, function: str, origin: str = FIRMWARE_ORIGIN) -> Expectations:
        """Expect one function to spend more time in itself than any other of its origin."""
        return self._expectations.add(HeaviestFunctionIs(function, origin))


class ResetExpectation:
    """What is expected of the firmware's resets, of one cause or of any."""

    def __init__(self, expectations: Expectations, cause: str) -> None:
        self._expectations = expectations
        self._cause = cause

    def happened(self, times: int = 0) -> Expectations:
        """Expect such a reset in the window: exactly so many times, or with 0 at least once."""
        return self._expectations.add(ResetHappened(self._cause, times))

    def happened_once(self) -> Expectations:
        """Expect exactly one such reset in the window."""
        return self.happened(times=1)

    def no_loop(self) -> Expectations:
        """Expect no reset loop: the server finds none at the window's end."""
        return self._expectations.add(NoResetLoop())


class FlashExpectation:
    """What is expected of the flash."""

    def __init__(self, expectations: Expectations) -> None:
        self._expectations = expectations

    def no_violation(self) -> Expectations:
        """Expect every write in the window to keep the flash's rules."""
        return self._expectations.add(NoFlashViolation())

    def partition(self, name: str) -> PartitionExpectation:
        """Expect something of what a partition holds at the window's end (Pro)."""
        return PartitionExpectation(self._expectations, name)


class PartitionExpectation:
    """What is expected of one partition's header, as the server reads it (Pro)."""

    def __init__(self, expectations: Expectations, name: str) -> None:
        self._expectations = expectations
        self._name = name

    def is_valid(self, image: str = "") -> Expectations:
        """Expect a whole image of a built variant; of this one when it is named."""
        return self._add(PartitionHolds(self._name, ("valid",), image))

    def is_invalid(self) -> Expectations:
        """Expect no image a bootloader would start: broken, unknown or erased."""
        return self._add(PartitionHolds(self._name, ("broken", "unknown image", "empty")))

    def is_empty(self) -> Expectations:
        """Expect the partition erased."""
        return self._add(PartitionHolds(self._name, ("empty",)))

    def _add(self, check: PartitionHolds) -> Expectations:
        self._expectations.reads_headers()
        return self._expectations.add(check)
