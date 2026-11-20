"""The thermostat and the gateway of looper-docs on one bench, run in looper-srv (#9).

``looper.run_bench`` starts ``looper-srv run --bench`` for the pair as the
development edition (a bench is Pro; ``LOOPER_DEV_EDITION=pro`` counts only
in a debug build), each device with a server of its own on held virtual
clocks:

- the gateway hears the thermostat's status 0x120, named by its sender and
  acknowledged by the gateway;
- a press of the gateway's BUTTON sends a set point 0x220 that the
  thermostat takes: its next status says 21.5 degC;
- an OBD-II request 0x7DF put on the gateway's bus is answered with 0x7E8;
- a reset of the gateway is a mark on the thermostat's bench;
- a held bench stands: neither device's time moves;
- without a licence the bench is refused with the server's sentence.

Needs a looper-docs checkout beside this one with the thermostat and gateway
fixtures, a C compiler, and a debug build of looper-srv that runs benches;
skips without them. Each fixture is locked as srv's conformance suite locks
it, so the two suites can run side by side.
"""

from __future__ import annotations

import os
import shutil
import time
from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path

import pytest

import looper
from fixture_lock import simulation_of
from server_under_test import FIXTURES, SRV_EXE, server_command

THERMOSTAT = FIXTURES / "thermostat" / "looper.toml"
GATEWAY = FIXTURES / "gateway" / "looper.toml"
#: The bench's name, this run's own: the host's pipes and the bench's room on this PC are
#: named after it, and a bench started again under the name of one that just ended can
#: find the room as that one left it.
BENCH_NAME = f"py-pair-{os.getpid()}"
STATUS, SET_POINT, OBD_REQUEST, OBD_ANSWER = 0x120, 0x220, 0x7DF, 0x7E8
#: Mode 01, PID 05 (coolant temperature), as an ISO 15765-2 single frame.
COOLANT_REQUEST = bytes([0x02, 0x01, 0x05, 0, 0, 0, 0, 0])
#: How long another server takes at most to say what changed: it writes five times a second.
FOLLOW_SECONDS = 5.0


def _skip_without_what_a_bench_needs() -> None:
    if not (THERMOSTAT.is_file() and GATEWAY.is_file()):
        pytest.skip(f"no thermostat and gateway fixtures in {FIXTURES}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    if not SRV_EXE.is_file():
        pytest.skip(f"no looper-srv at {SRV_EXE}")


def bench_toml(folder: Path, name: str) -> Path:
    """A bench file of the pair, the thermostat leading, joined on CAN1."""
    path = folder / "bench.toml"
    path.write_text(
        f'[bench]\nname = "{name}"\n\n'
        f'[[members]]\nname = "thermostat"\nproject = "{THERMOSTAT.resolve().as_posix()}"\n\n'
        f'[[members]]\nname = "gateway"\nproject = "{GATEWAY.resolve().as_posix()}"\n\n'
        '[[joins]]\nbus = "CAN1"\nmembers = { thermostat = "CAN1", gateway = "CAN1" }\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture(scope="module")
def bench(tmp_path_factory: pytest.TempPathFactory) -> Iterator[looper.Bench]:
    """The pair on one bench as the development edition, held at 0 s, for this module."""
    _skip_without_what_a_bench_needs()
    path = bench_toml(tmp_path_factory.mktemp("bench"), BENCH_NAME)
    with ExitStack() as stack, pytest.MonkeyPatch.context() as environment:
        stack.enter_context(simulation_of(THERMOSTAT))
        stack.enter_context(simulation_of(GATEWAY))
        environment.setenv("LOOPER_DEV_EDITION", "pro")
        started = stack.enter_context(looper.run_bench(path, server=server_command()))
        yield started


def _set_point_dc(status: looper.Exchange) -> int:
    """The set point a status 0x120 carries, in 0.1 degC."""
    return int.from_bytes(status.payload[2:4], "little", signed=True)


def _marks_within(bench: looper.Bench, seconds: float) -> tuple[looper.BenchMark, ...]:
    """The leader's marks once it has one: the servers tell each other five times a second."""
    deadline = time.monotonic() + seconds
    marks = bench.state().marks
    while not marks and time.monotonic() < deadline:
        time.sleep(0.1)
        marks = bench.state().marks
    return marks


def _press(simulation: looper.Simulation, bench: looper.Bench) -> None:
    """Press BUTTON (active low) for 100 ms and let it go."""
    button = simulation.pin("BUTTON")
    if button.level == "low":
        simulation.toggle_pin(button.pin_id)
        bench.advance(0.05)
    simulation.toggle_pin(button.pin_id)
    bench.advance(0.1)
    simulation.toggle_pin(button.pin_id)


def test_both_devices_see_one_bench_the_thermostat_leading(bench: looper.Bench) -> None:
    state = bench.state()

    assert bench.member_names == ("thermostat", "gateway")
    assert state.phase is looper.BenchPhase.ON_BENCH
    assert state.name == BENCH_NAME
    assert state.leader is not None
    assert state.leader.name == "thermostat"
    assert bench.member("gateway").bench_state().device("gateway").this_device
    addresses = [device.address for device in state.devices]
    assert all(addresses) and len(set(addresses)) == 2, addresses
    assert [device.windows for device in state.devices] == [0, 0]


def test_the_gateway_hears_the_thermostat_s_status(bench: looper.Bench) -> None:
    bench.advance(0.25)

    heard = bench.member("gateway").bus_records("CAN1", sender="thermostat")
    statuses = [frame for frame in heard if frame.address == STATUS]

    assert statuses, "the gateway hears the thermostat's status"
    assert statuses[0].sender_text == "thermostat"
    assert statuses[0].acknowledged_by_text == "acknowledged by gateway"
    assert bench.member("thermostat").run_state().bench_text == "bench"


def test_a_press_on_the_gateway_moves_the_thermostat_s_set_point(bench: looper.Bench) -> None:
    gateway, thermostat = bench.member("gateway"), bench.member("thermostat")
    bench.advance(0.2)
    since = gateway.run_state().next_event_seq

    _press(gateway, bench)
    bench.advance(0.3)

    sent = thermostat.bus_records("CAN1", sender="gateway")
    set_points = [frame for frame in sent if frame.address == SET_POINT]
    statuses = [one for one in gateway.bus_records("CAN1", since=since) if one.address == STATUS]
    assert set_points, "the thermostat hears the gateway's set point"
    assert statuses
    assert _set_point_dc(statuses[-1]) == 215


def test_an_obd_request_is_answered(bench: looper.Bench) -> None:
    gateway = bench.member("gateway")
    since = gateway.run_state().next_event_seq
    can1 = gateway.bus("CAN1")

    gateway.send_bus_message(looper.BusMessage(can1.bus_id, OBD_REQUEST, COOLANT_REQUEST))
    bench.advance(0.05)

    answers = [one for one in gateway.bus_records("CAN1", since=since) if one.address == OBD_ANSWER]
    assert answers, "the gateway answers 0x7DF with 0x7E8"
    assert answers[0].payload[:3] == bytes([0x03, 0x41, 0x05])
    heard = bench.member("thermostat").bus_records("CAN1", sender="gateway")
    assert any(frame.address == OBD_ANSWER for frame in heard)


def test_a_reset_of_the_gateway_is_a_mark_on_the_thermostat_s_bench(bench: looper.Bench) -> None:
    gateway = bench.member("gateway")
    reset_at_us = gateway.run_state().now_us

    gateway.reset("pin")
    lives = gateway.lives()
    marks = _marks_within(bench, FOLLOW_SECONDS)

    assert lives[-1].number == 2, "the reset is done when it returns"
    assert lives[-1].started_at_us >= reset_at_us
    assert [(mark.device, mark.life) for mark in marks] == [("gateway", 2)]
    assert marks[0].text == "gateway reset · pin · life 2"


def test_a_paced_bench_runs_and_a_held_one_stands(bench: looper.Bench) -> None:
    thermostat, gateway = bench.member("thermostat"), bench.member("gateway")
    paced_from = gateway.run_state().now_us
    bench.pace(1.0)
    time.sleep(0.5)
    assert gateway.run_state().now_us > paced_from, "a paced bench moves"

    bench.hold()
    before = (thermostat.run_state().now_us, gateway.run_state().now_us)
    time.sleep(0.5)
    after = (thermostat.run_state().now_us, gateway.run_state().now_us)

    assert gateway.clock_mode is looper.ClockMode.HELD
    assert before == after


def test_without_a_licence_the_bench_is_refused_with_the_server_s_sentence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _skip_without_what_a_bench_needs()
    monkeypatch.delenv("LOOPER_DEV_EDITION", raising=False)
    monkeypatch.setenv("LOOPER_LICENSE", str(tmp_path / "no-licence.toml"))

    with pytest.raises(looper.BenchProLockedError, match="Bench is part of looper Pro"):
        looper.run_bench(bench_toml(tmp_path, f"py-free-{os.getpid()}"), server=server_command())
