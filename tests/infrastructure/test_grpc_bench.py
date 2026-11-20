"""The bench calls, a frame's sender and RunState's bench texts through the gRPC adapter (#9)."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import BenchPhase, BoardNodeKind, ProFeatureLockedError, SimulationRefusedError
from looper.infrastructure import board_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

FREE = "Bench is part of looper Pro - this is the free download."
ON_A_PROBE = "A board at a probe is on no bench – a bench is for simulations."


class BenchServicer(service.InspectorServicer):  # type: ignore[misc]
    """A thermostat leading a bench with a gateway; refuses or locks once told to."""

    def __init__(self) -> None:
        self.refuse = ""
        self.locked = False
        self.joined: list[Any] = []

    def _refuse_if_told(self, context: Any) -> None:
        if self.locked:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, FREE)
        if self.refuse:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, self.refuse)

    def ObserveBench(self, request: Any, context: Any) -> contract.BenchState:
        self._refuse_if_told(context)
        devices = [
            contract.BenchDevice(name="thermostat", leader=True, this_device=True),
            contract.BenchDevice(
                name="gateway", index=1, state_text="held", now_text="0.250 s", windows=1
            ),
        ]
        bus = contract.JoinedBus(bus_id=1, label="CAN1", join="CAN1", bitrate=500_000, frames=4)
        mark = contract.BenchMark(sim_us=300_000, device="gateway", life=2, text="gateway reset")
        return contract.BenchState(
            revision=4,
            phase=contract.BENCH_PHASE_ON_BENCH,
            name="lab",
            devices=devices,
            buses=[bus],
            marks=[mark],
        )

    def DescribeJoinCandidates(self, request: Any, context: Any) -> contract.JoinCandidates:
        self._refuse_if_told(context)
        choice = contract.JoinBusChoice(bus_id=5, label="CAN1", bitrate=500_000, preselected=True)
        candidate = contract.JoinCandidate(
            instance_id="gw-1", firmware_name="gateway", joinable=True, buses=[choice]
        )
        return contract.JoinCandidates(title=f"bus {request.bus_id}", candidates=[candidate])

    def JoinBus(self, request: Any, context: Any) -> contract.BenchState:
        self._refuse_if_told(context)
        self.joined.append(request)
        return contract.BenchState(revision=2, phase=contract.BENCH_PHASE_JOINING)

    def LeaveBench(self, request: Any, context: Any) -> contract.BenchState:
        self._refuse_if_told(context)
        return contract.BenchState(revision=5, phase=contract.BENCH_PHASE_LEAVING)

    def ObserveRun(self, request: Any, context: Any) -> contract.RunState:
        return contract.RunState(bench_text="bench", bench_chip_text="⇄ gateway")

    def ReadEvents(self, request: Any, context: Any) -> contract.EventBatch:
        frame = contract.Exchange(
            bus_id=1,
            address_value=0x120,
            accepted=True,
            source=contract.SOURCE_LINK,
            sender_text="thermostat",
            sender_device="thermostat",
            acknowledged_by_text="acknowledged by gateway",
        )
        event = contract.Event(event_seq=1, sim_us=100, exchange=frame)
        return contract.EventBatch(events=[event], next_event_seq=2)


@pytest.fixture
def servicer() -> BenchServicer:
    return BenchServicer()


@pytest.fixture
def inspector(servicer: BenchServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_the_bench_comes_with_its_devices_buses_and_marks(inspector: GrpcInspector) -> None:
    state = inspector.read_bench()

    assert (state.phase, state.name, state.device_names) == (
        BenchPhase.ON_BENCH,
        "lab",
        ("thermostat", "gateway"),
    )
    assert state.leader == state.this_device
    assert state.device("gateway").now_text == "0.250 s"
    assert state.device("gateway").windows == 1
    assert (state.buses[0].label, state.buses[0].frames) == ("CAN1", 4)
    assert (state.marks[0].device, state.marks[0].life) == ("gateway", 2)


def test_a_join_names_both_buses_and_the_peer(
    inspector: GrpcInspector, servicer: BenchServicer
) -> None:
    candidates = inspector.read_join_candidates(1)
    peer = candidates.running("gateway")

    answered = inspector.join_bus(1, peer.instance_id, peer.buses[0].bus_id)

    assert candidates.title == "bus 1"
    assert answered.phase is BenchPhase.JOINING
    joined = servicer.joined[0]
    assert (joined.bus_id, joined.peer_instance_id, joined.peer_bus_id) == (1, "gw-1", 5)
    assert inspector.leave_bench().phase is BenchPhase.LEAVING


def test_the_free_download_is_a_pro_lock_with_its_sentence(
    inspector: GrpcInspector, servicer: BenchServicer
) -> None:
    servicer.locked = True

    with pytest.raises(ProFeatureLockedError) as locked:
        inspector.read_bench()
    assert str(locked.value) == FREE


def test_a_board_at_a_probe_is_refused_with_its_sentence(
    inspector: GrpcInspector, servicer: BenchServicer
) -> None:
    servicer.refuse = ON_A_PROBE

    with pytest.raises(SimulationRefusedError) as refused:
        inspector.join_bus(1, "gw-1", 5)
    assert str(refused.value) == ON_A_PROBE


def test_a_frame_names_its_sender_and_who_acknowledged_it(inspector: GrpcInspector) -> None:
    frame = inspector.read_events(epoch=0, from_event_seq=0).exchanges[0]

    assert (frame.sender_device, frame.sender_text, frame.from_peer) == (
        "thermostat",
        "thermostat",
        True,
    )
    assert frame.acknowledged_by_text == "acknowledged by gateway"


def test_the_run_state_carries_the_bench_s_texts(inspector: GrpcInspector) -> None:
    state = inspector.run_state()

    assert (state.bench_text, state.bench_chip_text, state.peer_stop_text) == (
        "bench",
        "⇄ gateway",
        "",
    )


def test_a_peer_on_the_device_page_is_a_node_of_its_own() -> None:
    peer = contract.BoardNode(key="peer:gateway", kind=contract.BoardNode.PEER, title="gateway")
    rail = contract.BoardNode(key="bus:CAN1", kind=contract.BoardNode.BUS, joined_text="joined")
    state = contract.BoardNodeState(key="peer:gateway", frames_text="3 frames")

    assert board_translation.node_of(peer).kind is BoardNodeKind.PEER
    assert board_translation.node_of(rail).joined_text == "joined"
    assert board_translation.node_state_of(state).frames_text == "3 frames"
