"""Expectations on the messages of one kind, rather than on everything a bus carried."""

from __future__ import annotations

from looper.domain.checks import MessageCount, MessageFilter, MessageRate
from looper.domain.model import Exchange, Observation


def a_frame(address: int, payload: bytes = b"", direction: str = "outbound") -> Exchange:
    """One accepted frame on bus two."""
    return Exchange(
        bus_id=2,
        sim_us=0,
        address=address,
        display_address=hex(address),
        direction=direction,
        payload=payload,
        response=b"",
        length=len(payload),
        accepted=True,
        event_seq=0,
    )


def observed(*frames: Exchange, seconds: float = 1.0) -> Observation:
    """A window that saw these frames."""
    return Observation(samples=(), exchanges=frames, timings=(), elapsed_seconds=seconds)


STATUS = MessageFilter(address=0x321, direction="outbound")


def test_only_the_messages_of_the_kind_are_counted() -> None:
    window = observed(
        a_frame(0x321), a_frame(0x321), a_frame(0x320), a_frame(0x321, direction="inbound")
    )

    outcome = MessageCount(2, "CAN1", STATUS, 2).evaluate(window)

    assert outcome.met
    assert outcome.subject == "CAN1 id=0x321 outbound"


def test_a_rate_is_worked_out_from_the_messages_of_the_kind() -> None:
    window = observed(*(a_frame(0x321) for _ in range(20)), a_frame(0x100), seconds=2.0)

    assert MessageRate(2, "CAN1", STATUS, 10.0, 0.05).evaluate(window).met
    assert not MessageRate(2, "CAN1", STATUS, 20.0, 0.05).evaluate(window).met


def test_a_payload_prefix_narrows_the_kind() -> None:
    window = observed(a_frame(0x321, b"\x01\x02"), a_frame(0x321, b"\x02\x02"))
    wanted = MessageFilter(address=0x321, starts_with=b"\x01")

    assert MessageCount(2, "CAN1", wanted, 1, 1).evaluate(window).met


def test_never_fails_on_the_first_message_of_the_kind() -> None:
    outcome = MessageCount(2, "CAN1", STATUS, 0, 0).evaluate(observed(a_frame(0x321)))

    assert not outcome.met
    assert "expected no message" in outcome.line
