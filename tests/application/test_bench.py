"""A bench of devices and a simulation on one, through the port (#9)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from bench_doubles import FREE, ON_BENCH
from doubles import ScriptedInspector
from looper import (
    Bench,
    BenchPhase,
    Bus,
    ClockMode,
    Exchange,
    ProFeatureLockedError,
    Simulation,
    SimulationRefusedError,
)

CAN1 = Bus(bus_id=1, kind="can", name="CAN1", accepts_messages=True)
CAN2 = Bus(bus_id=2, kind="can", name="CAN2", accepts_messages=True)


def a_frame(event_seq: int, address: int, bus_id: int = 1, sender: str = "") -> Exchange:
    """A frame on a bus, sent by `sender` on the bench or by this device."""
    return Exchange(
        bus_id=bus_id,
        sim_us=event_seq * 100,
        address=address,
        display_address=f"0x{address:X}",
        direction="inbound" if sender else "outbound",
        payload=b"\x01",
        response=b"",
        length=1,
        accepted=True,
        event_seq=event_seq,
        sender_device=sender,
        sender_text=sender,
        acknowledged_by_text="acknowledged by thermostat",
    )


def a_device() -> tuple[ScriptedInspector, Simulation]:
    inspector = ScriptedInspector()
    inspector.buses = (CAN1, CAN2)
    return inspector, Simulation(inspector)


def a_bench() -> tuple[dict[str, ScriptedInspector], Bench, list[str]]:
    inspectors = {"thermostat": ScriptedInspector(), "gateway": ScriptedInspector()}
    stopped: list[str] = []
    members = {name: Simulation(inspector) for name, inspector in inspectors.items()}
    bench = Bench(members, "thermostat", on_close=lambda: stopped.append("leader"))
    return inspectors, bench, stopped


def test_a_member_is_found_by_its_name_and_an_unknown_one_names_those_there_are() -> None:
    inspectors, bench, _ = a_bench()

    assert bench.member_names == ("thermostat", "gateway")
    assert bench.member("gateway").firmware_name == "blinky"
    with pytest.raises(KeyError, match="'dashboard'.*thermostat"):
        bench.member("dashboard")


def test_the_bench_advances_through_its_leader() -> None:
    inspectors, bench, _ = a_bench()

    bench.advance(0.25)

    assert inspectors["thermostat"].run.now_us == 250_000
    assert inspectors["gateway"].run.now_us == 0


def test_a_hold_waits_until_every_device_followed() -> None:
    inspectors, bench, _ = a_bench()
    for inspector in inspectors.values():
        inspector.run = replace(inspector.run, clock_mode=ClockMode.PACED)
    inspectors["gateway"].run = replace(inspectors["gateway"].run, clock_mode=ClockMode.HELD)

    bench.hold()

    assert {inspector.run.clock_mode for inspector in inspectors.values()} == {ClockMode.HELD}


def test_a_device_that_does_not_follow_is_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("looper.application.bench.FOLLOW_TIMEOUT_SECONDS", 0.1)
    inspectors, bench, _ = a_bench()
    inspectors["gateway"].run = replace(inspectors["gateway"].run, clock_mode=ClockMode.PACED)

    with pytest.raises(TimeoutError, match="gateway"):
        bench._followed(ClockMode.HELD)


def test_the_state_is_the_leader_s_and_closing_stops_the_bench_once() -> None:
    inspectors, bench, stopped = a_bench()
    inspectors["thermostat"].bench = ON_BENCH

    with bench:
        assert bench.state().leader is not None
        assert bench.state().device("gateway").index == 1
    bench.close()

    assert stopped == ["leader"]


def test_joining_takes_the_preselected_bus_and_waits_for_the_bench() -> None:
    inspector, simulation = a_device()

    peer = simulation.join_candidates("CAN1").running("gateway")
    state = simulation.join_bus("CAN1", peer)

    assert inspector.joins == [(1, "gw-1", 5)]
    assert state.phase is BenchPhase.ON_BENCH
    assert state.this_device is not None
    assert state.this_device.name == "thermostat"


def test_joining_takes_the_peer_s_bus_by_its_label() -> None:
    inspector, simulation = a_device()

    simulation.join_bus("CAN2", simulation.join_candidates("CAN2").running("gateway"), "CAN2")

    assert inspector.joins == [(2, "gw-1", 7)]


def test_a_join_that_did_not_go_through_is_a_refusal_with_the_server_s_sentence() -> None:
    inspector, simulation = a_device()
    inspector.bench_failure = "gateway has no CAN bus CAN1."
    peer = simulation.join_candidates("CAN1").running("gateway")

    with pytest.raises(SimulationRefusedError, match="gateway has no CAN bus CAN1"):
        simulation.join_bus("CAN1", peer)


def test_leaving_waits_until_the_device_is_alone() -> None:
    inspector, simulation = a_device()
    inspector.bench = ON_BENCH

    assert simulation.leave_bench().phase is BenchPhase.ALONE


def test_the_free_download_s_sentence_is_raised() -> None:
    inspector, simulation = a_device()
    inspector.bench_locked = True

    with pytest.raises(ProFeatureLockedError) as locked:
        simulation.bench_state()
    assert str(locked.value) == FREE


def test_bus_records_are_picked_by_bus_and_by_sender() -> None:
    inspector, simulation = a_device()
    inspector.exchanges = (
        a_frame(1, 0x120),
        a_frame(2, 0x220, sender="gateway"),
        a_frame(3, 0x7E8, bus_id=2, sender="dashboard"),
    )

    assert [one.address for one in simulation.bus_records("CAN1")] == [0x120, 0x220]
    assert [one.address for one in simulation.bus_records(sender="gateway")] == [0x220]
    assert [one.address for one in simulation.bus_records(sender="peer")] == [0x220, 0x7E8]
    assert simulation.bus_records("CAN1", sender="peer")[0].sender_text == "gateway"


def test_a_bus_the_firmware_lacks_is_a_refusal_that_names_those_it_has() -> None:
    _, simulation = a_device()

    with pytest.raises(SimulationRefusedError, match="no bus named 'CAN3'; it has CAN1, CAN2"):
        simulation.bus_records("CAN3")


def test_the_other_device_of_a_join_is_waited_for_until_it_is_on_the_bench() -> None:
    inspector, simulation = a_device()
    inspector.join_bus(1, "gw-1", 5)

    assert simulation.wait_for_bench().phase is BenchPhase.ON_BENCH
