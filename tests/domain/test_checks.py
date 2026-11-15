"""The checks on the numbers of one window, without any simulation."""

from __future__ import annotations

from looper.domain.checks import BusCarriedAtLeast, ChannelReaches
from looper.domain.model import Exchange, Observation, Sample
from looper.domain.model.event_loss import EventLoss, RingCount


def a_sample(sim_us: int, value: float) -> Sample:
    """One sample of channel zero."""
    return Sample(channel_id=0, sim_us=sim_us, value=value, event_seq=sim_us)


def an_exchange(event_seq: int) -> Exchange:
    """One accepted frame on bus two."""
    return Exchange(
        bus_id=2,
        sim_us=event_seq,
        address=0x701,
        display_address="0x701",
        direction="inbound",
        payload=b"",
        response=b"",
        length=0,
        accepted=True,
        event_seq=event_seq,
    )


def test_reaching_a_value_is_timed_in_whole_microseconds() -> None:
    observed = Observation(
        samples=(a_sample(100_000, 0.0), a_sample(350_000, 1.0)),
        exchanges=(),
        timings=(),
        elapsed_seconds=1.0,
    )

    outcome = ChannelReaches(0, "P1A", 1.0, 0.01, 0.5).evaluate(observed)

    assert outcome.met
    assert "reached after 0.25 s" in outcome.line


def test_events_the_recording_lost_are_named_but_not_counted_as_exchanges() -> None:
    observed = Observation(
        samples=(),
        exchanges=(an_exchange(1),),
        timings=(),
        elapsed_seconds=1.0,
        lost=EventLoss(in_the_ring=5),
    )

    outcome = BusCarriedAtLeast(2, "CAN2", 3).evaluate(observed)

    assert not outcome.met
    assert "saw 1, and 5 events the recording could not keep" in outcome.line


def test_the_note_says_where_the_events_were_lost() -> None:
    lost = EventLoss(in_the_ring=650, by_the_client=50)

    assert lost.note() == (
        ", and 700 events the recording could not keep (650 overwritten in the "
        "simulation's ring, 50 not read in time by this client)"
    )
    assert EventLoss().note() == ""


def test_the_note_names_the_rings_that_dropped_events_added_up_over_the_gaps() -> None:
    interrupts = RingCount(
        "interrupts", 600, "interrupt events; a larger [interrupts] ring keeps more"
    )
    first = EventLoss(in_the_ring=600, rings=(interrupts,))
    second = EventLoss(
        in_the_ring=50,
        rings=(
            RingCount("interrupts", 40, interrupts.text),
            RingCount("exchanges", 10, "bus exchanges"),
        ),
    )

    assert (first + second).note() == (
        ", and 650 events the recording could not keep (650 overwritten in the simulation's ring"
        " – 640 interrupt events; a larger [interrupts] ring keeps more, 10 bus exchanges)"
    )
