"""The Hypothesis strategies draw what they promise, and a simulation takes it.

Each property is checked over the drawn values themselves, with a fixed
derandomised profile so that ``uv run pytest`` runs the same examples every
time (``HYPOTHESIS_PROFILE=deep`` draws many more).
"""

from __future__ import annotations

import os

from hypothesis import given, settings
from hypothesis import strategies as st

from doubles import ScriptedInspector
from looper import strategies
from looper.application.simulation import Simulation
from looper.domain.model import Bus, BusMessage

settings.register_profile("ci", max_examples=60, derandomize=True, deadline=None)
settings.register_profile("deep", max_examples=5000, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "ci"))

UART = Bus(2, "uart", "UART1", accepts_messages=True, max_payload_bytes=64)


@given(strategies.unsigned(2, min_value=10, max_value=1000, byteorder="big"))
def test_an_unsigned_field_has_its_size_and_stays_in_its_range(field: bytes) -> None:
    assert len(field) == 2
    assert 10 <= int.from_bytes(field, "big") <= 1000


@given(strategies.signed(1))
def test_a_signed_field_covers_both_signs_of_its_size(field: bytes) -> None:
    assert -128 <= int.from_bytes(field, "little", signed=True) <= 127


@given(strategies.one_of_values([0x01, 0x10, 0x300], size=2))
def test_an_enumerated_field_holds_one_of_its_values(field: bytes) -> None:
    assert int.from_bytes(field, "little") in {0x01, 0x10, 0x300}


@given(strategies.fields(strategies.raw(1, 1), strategies.length_prefixed(strategies.raw(0, 5))))
def test_a_length_field_says_how_long_its_body_is(payload: bytes) -> None:
    assert payload[1] == len(payload) - 2


@given(strategies.with_checksum(strategies.raw(0, 7), strategies.sum8))
def test_a_checksum_is_computed_from_what_was_drawn(payload: bytes) -> None:
    assert payload[-1] == sum(payload[:-1]) % 256


@given(strategies.with_checksum(strategies.raw(0, 7), strategies.xor8))
def test_an_exclusive_or_checksum_cancels_out_over_the_whole(payload: bytes) -> None:
    assert strategies.xor8(payload) == b"\x00"


@given(strategies.bus_messages(UART, payloads=strategies.raw(0, 200)))
def test_a_message_never_carries_more_than_its_bus_takes(message: BusMessage) -> None:
    assert message.bus_id == UART.bus_id
    assert len(message.payload) <= UART.max_payload_bytes


@given(strategies.bus_messages(5))
def test_a_bus_that_does_not_say_gets_classic_can_frames(message: BusMessage) -> None:
    assert len(message.payload) <= strategies.CLASSIC_CAN_PAYLOAD
    assert 0 <= message.address <= strategies.STANDARD_ID_MAX
    assert not message.extended


@given(strategies.bus_messages(5, addresses=[0x6FF, 0x700], extended=True))
def test_given_addresses_are_the_ones_used(message: BusMessage) -> None:
    assert message.address in {0x6FF, 0x700}
    assert message.extended


@given(strategies.bus_messages(5, addresses=st.integers(0x100, 0x1FF)))
def test_addresses_may_come_as_a_strategy(message: BusMessage) -> None:
    assert 0x100 <= message.address <= 0x1FF


@given(strategies.bus_messages(UART))
def test_a_simulation_takes_every_message_drawn_for_its_bus(message: BusMessage) -> None:
    inspector = ScriptedInspector()
    inspector.buses = (UART,)

    Simulation(inspector).send_bus_message(message)

    assert inspector.messages == [message]
