"""Hypothesis strategies for what a test puts on a bus.

A property test says what must hold for *every* input of a kind -- "for
every well-formed command the firmware stays alive and the bus refuses
nothing" -- and Hypothesis draws the inputs, and shrinks a failing one to
the smallest that still fails. These strategies draw messages and their
payloads field by field, so that a test can describe a format once and let
Hypothesis vary it::

    from hypothesis import given
    from looper import strategies

    command = strategies.with_checksum(
        strategies.fields(
            strategies.one_of_values([0x01, 0x02, 0x10], size=1),  # the command
            strategies.length_prefixed(strategies.raw(max_size=6)),  # its argument
        ),
        strategies.sum8,
    )

    @given(message=strategies.bus_messages(can, payloads=command, addresses=[0x6FF]))
    def test_every_command_is_survived(message): ...

This is black-box testing: Hypothesis does not see which code an input
reached. It needs the optional dependency ``hypothesis``
(``pip install looper-py[hypothesis]``); ``import looper`` does not.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal

try:
    from hypothesis import strategies as st
except ImportError as missing:  # pragma: no cover - depends on the environment
    raise ImportError(
        "looper.strategies needs Hypothesis: pip install looper-py[hypothesis]"
    ) from missing

from looper.domain.model.readings import Bus
from looper.domain.model.requests import BusMessage

#: Byte order of a field, as ``int.to_bytes`` names it.
ByteOrder = Literal["little", "big"]
#: The most bytes a classic CAN frame carries, used when a bus does not say.
CLASSIC_CAN_PAYLOAD = 8
#: The largest 11-bit and 29-bit CAN identifiers.
STANDARD_ID_MAX = 0x7FF
EXTENDED_ID_MAX = 0x1FFF_FFFF


def unsigned(
    size: int,
    *,
    min_value: int = 0,
    max_value: int | None = None,
    byteorder: ByteOrder = "little",
) -> st.SearchStrategy[bytes]:
    """An unsigned field of ``size`` bytes; Hypothesis likes its bounds."""
    top = (1 << (8 * size)) - 1 if max_value is None else max_value
    return st.integers(min_value, top).map(lambda value: value.to_bytes(size, byteorder))


def signed(
    size: int,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
    byteorder: ByteOrder = "little",
) -> st.SearchStrategy[bytes]:
    """A two's complement field of ``size`` bytes."""
    half = 1 << (8 * size - 1)
    low = -half if min_value is None else min_value
    high = half - 1 if max_value is None else max_value
    return st.integers(low, high).map(lambda value: value.to_bytes(size, byteorder, signed=True))


def one_of_values(
    values: Sequence[int], size: int = 1, byteorder: ByteOrder = "little"
) -> st.SearchStrategy[bytes]:
    """A field that holds one of the ``values`` an enumeration names."""
    return st.sampled_from(list(values)).map(lambda value: value.to_bytes(size, byteorder))


def raw(min_size: int = 0, max_size: int = CLASSIC_CAN_PAYLOAD) -> st.SearchStrategy[bytes]:
    """Bytes nobody describes: any of them, between the two sizes."""
    return st.binary(min_size=min_size, max_size=max_size)


def fields(*parts: st.SearchStrategy[bytes]) -> st.SearchStrategy[bytes]:
    """The parts one after the other, as a message lays out its fields."""
    return st.tuples(*parts).map(b"".join)


def length_prefixed(
    body: st.SearchStrategy[bytes], size: int = 1, byteorder: ByteOrder = "little"
) -> st.SearchStrategy[bytes]:
    """A body behind a field of ``size`` bytes that says how long the body is."""
    return body.map(lambda drawn: len(drawn).to_bytes(size, byteorder) + drawn)


def with_checksum(
    payload: st.SearchStrategy[bytes], checksum: Callable[[bytes], bytes]
) -> st.SearchStrategy[bytes]:
    """A payload with its checksum after it, computed from what was drawn.

    Computed after drawing, so that every message gets past the firmware's
    check and reaches what lies behind it. To test the check itself, draw
    the payload without this.
    """
    return payload.map(lambda drawn: drawn + checksum(drawn))


def sum8(data: bytes) -> bytes:
    """The sum of the bytes, modulo 256, as one byte."""
    return bytes([sum(data) & 0xFF])


def xor8(data: bytes) -> bytes:
    """Every byte exclusive-or'd together, as one byte."""
    result = 0
    for byte in data:
        result ^= byte
    return bytes([result])


def bus_messages(
    bus: Bus | int,
    *,
    payloads: st.SearchStrategy[bytes] | None = None,
    addresses: Sequence[int] | st.SearchStrategy[int] | None = None,
    extended: bool = False,
) -> st.SearchStrategy[BusMessage]:
    """Messages for one bus, as ``Simulation.send_bus_message`` takes them.

    Given the ``Bus`` a simulation lists, a payload is never longer than
    one message on it may carry, which the simulation would refuse.

    Args:
        bus: The bus, or its number.
        payloads: What the messages carry; any bytes a message may hold
            when not given.
        addresses: The identifiers or addresses to send to, as a list or a
            strategy; any standard (or, with ``extended``, extended) CAN
            identifier when not given.
        extended: Whether the addresses are 29-bit CAN identifiers.
    """
    longest = _longest_payload(bus)
    drawn_payloads = raw(0, longest) if payloads is None else payloads
    fitting = drawn_payloads.filter(lambda payload: len(payload) <= longest)
    bus_id = bus.bus_id if isinstance(bus, Bus) else bus
    return st.builds(
        BusMessage,
        bus_id=st.just(bus_id),
        address=_addresses(addresses, extended),
        payload=fitting,
        extended=st.just(extended),
    )


def _longest_payload(bus: Bus | int) -> int:
    """The most a message on the bus may carry; a classic CAN frame when it does not say."""
    if isinstance(bus, Bus) and bus.max_payload_bytes > 0:
        return bus.max_payload_bytes
    return CLASSIC_CAN_PAYLOAD


def _addresses(
    addresses: Sequence[int] | st.SearchStrategy[int] | None, extended: bool
) -> st.SearchStrategy[int]:
    """The addresses as a strategy, whatever form they were given in."""
    if addresses is None:
        return st.integers(0, EXTENDED_ID_MAX if extended else STANDARD_ID_MAX)
    if isinstance(addresses, st.SearchStrategy):
        return addresses
    return st.sampled_from(list(addresses))
