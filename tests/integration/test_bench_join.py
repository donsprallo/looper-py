"""Joining two running simulations on one bench and leaving it again, run in looper-srv (#9).

The thermostat and the gateway of looper-docs are started apart, as the
development edition (a bench is Pro). The thermostat's server lists the
gateway as a candidate for CAN1, joins it, and both restart into one bench
host: the gateway then hears the thermostat's status. Leaving restarts both
alone.

Needs a looper-docs checkout beside this one with the thermostat and gateway
fixtures, a C compiler, and a debug build of looper-srv that runs benches;
skips without them. Each fixture is locked as srv's conformance suite locks it.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from contextlib import ExitStack

import pytest

import looper
from fixture_lock import simulation_of
from server_under_test import FIXTURES, SRV_EXE, server_command

THERMOSTAT = FIXTURES / "thermostat" / "looper.toml"
GATEWAY = FIXTURES / "gateway" / "looper.toml"
STATUS = 0x120


@pytest.fixture(scope="module")
def pair() -> Iterator[tuple[looper.Simulation, looper.Simulation]]:
    """The thermostat and the gateway, each started alone on a held clock."""
    if not (THERMOSTAT.is_file() and GATEWAY.is_file()):
        pytest.skip(f"no thermostat and gateway fixtures in {FIXTURES}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    if not SRV_EXE.is_file():
        pytest.skip(f"no looper-srv at {SRV_EXE}")
    with ExitStack() as stack, pytest.MonkeyPatch.context() as environment:
        stack.enter_context(simulation_of(THERMOSTAT))
        stack.enter_context(simulation_of(GATEWAY))
        environment.setenv("LOOPER_DEV_EDITION", "pro")
        thermostat = stack.enter_context(
            looper.run(THERMOSTAT, virtual=True, server=server_command())
        )
        gateway = stack.enter_context(looper.run(GATEWAY, virtual=True, server=server_command()))
        yield thermostat, gateway


def test_the_gateway_is_a_candidate_for_can1(
    pair: tuple[looper.Simulation, looper.Simulation],
) -> None:
    thermostat, _ = pair

    candidates = thermostat.join_candidates("CAN1")
    gateway = candidates.running("gateway")

    assert gateway.joinable, gateway.reason_text
    assert gateway.preselected_bus is not None
    assert gateway.preselected_bus.label == "CAN1"
    assert candidates.title == "Join CAN1 of thermostat with another device"


def test_a_join_puts_both_on_one_bench_and_a_leave_parts_them(
    pair: tuple[looper.Simulation, looper.Simulation],
) -> None:
    thermostat, gateway = pair

    joined = thermostat.join_bus("CAN1", thermostat.join_candidates("CAN1").running("gateway"))
    gateway.wait_for_bench()
    thermostat.advance(0.25)
    heard = gateway.bus_records("CAN1", sender="thermostat")
    thermostat.leave_bench()
    gateway.wait_for_bench(looper.BenchPhase.ALONE)

    assert joined.device_names == ("thermostat", "gateway")
    assert joined.leader is not None
    assert joined.leader.name == "thermostat"
    assert any(frame.address == STATUS for frame in heard)
    assert gateway.bench_state().phase is looper.BenchPhase.ALONE
