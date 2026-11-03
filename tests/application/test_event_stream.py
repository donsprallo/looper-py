"""Walking the recorded event stream through the facade."""

from __future__ import annotations

import pytest

from doubles import PAGE_SIZE, ScriptedInspector
from looper import ClockMode, Exchange, Simulation, SimulationRefusedError
from looper.domain.model import RunStatus


def _exchange(event_seq: int, payload: bytes = b"\x01") -> Exchange:
    return Exchange(
        bus_id=1,
        sim_us=event_seq * 100,
        address=0x20,
        display_address="0x20",
        direction="outbound",
        payload=payload,
        response=b"",
        length=len(payload),
        accepted=True,
        event_seq=event_seq,
    )


def test_one_page_is_read_from_the_event_number_it_was_asked_for() -> None:
    inspector = ScriptedInspector()
    inspector.exchanges = tuple(_exchange(seq) for seq in range(5))

    page = Simulation(inspector).read_events(since=2)

    assert [one.event_seq for one in page.exchanges] == [2, 3]
    assert page.next_event_seq == 4
    assert "read events epoch 1 from 2" in inspector.asked


def test_the_whole_recording_is_walked_across_pages() -> None:
    inspector = ScriptedInspector()
    inspector.exchanges = tuple(_exchange(seq) for seq in range(5))

    walked = list(Simulation(inspector).exchanges())

    assert [one.event_seq for one in walked] == [0, 1, 2, 3, 4]
    assert inspector.reads > len(walked) // PAGE_SIZE


def test_reading_goes_on_from_one_beyond_the_last_exchange_seen() -> None:
    inspector = ScriptedInspector()
    inspector.exchanges = tuple(_exchange(seq) for seq in range(5))
    simulation = Simulation(inspector)

    first = next(iter(simulation.exchanges()))
    rest = list(simulation.exchanges(since=first.event_seq + 1))

    assert [one.event_seq for one in rest] == [1, 2, 3, 4]


def test_a_recording_with_nothing_on_it_yields_nothing() -> None:
    assert list(Simulation(ScriptedInspector()).exchanges()) == []


def test_only_exchanges_are_yielded_and_samples_stay_on_the_page() -> None:
    inspector = ScriptedInspector()
    inspector.exchanges = (_exchange(1),)

    page = Simulation(inspector).read_events()

    assert len(page.exchanges) == 1
    assert page.samples == ()


def test_a_clear_by_another_client_while_reading_is_a_refusal() -> None:
    inspector = ScriptedInspector()
    inspector.exchanges = (_exchange(0),)
    inspector.epoch_changes_while_reading = True

    with pytest.raises(SimulationRefusedError, match="cleared while it was being read"):
        list(Simulation(inspector).exchanges())


def test_the_epoch_is_read_from_the_simulation_and_not_asked_of_the_test() -> None:
    inspector = ScriptedInspector()
    inspector.run = RunStatus(now_us=0, clock_mode=ClockMode.HELD, epoch=7, next_event_seq=0)

    Simulation(inspector).read_events()

    assert "read events epoch 7 from 0" in inspector.asked
