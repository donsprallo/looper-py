"""Triggers through the gRPC adapter, against a scripted server in this process."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import (
    Comparison,
    Edge,
    EdgeWhile,
    PinLevel,
    Polarity,
    Quiet,
    SimulationRefusedError,
    TriggerMode,
    TriggerState,
    Value,
    Width,
)
from looper.domain.model import TriggerCondition, TriggerRequest
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector
from looper.infrastructure.trigger_translation import condition_of

REFUSED_SEQUENCE = contract.Ack(
    refusal=contract.REFUSAL_INVALID, refusal_text="Sequence triggers are not supported yet"
)


class TriggerServicer(service.InspectorServicer):  # type: ignore[misc]
    """Arms what it is asked to, under the number 7, and remembers the spec."""

    def __init__(self) -> None:
        self.spec: contract.TriggerSpec | None = None
        self.choice: contract.TriggerChoice | None = None
        self.arm_ack = contract.Ack()

    def ArmTrigger(self, request: Any, context: Any) -> contract.TriggerView:
        self.spec = request
        return contract.TriggerView(
            trigger_id=7, spec=request, description="BUTTON falls", ack=self.arm_ack
        )

    def DisarmTrigger(self, request: Any, context: Any) -> contract.TriggerView:
        self.choice = request
        return contract.TriggerView(
            trigger_id=request.trigger_id,
            state=contract.TriggerView.DISARMED,
            disarmed_by=request.by_client,
        )

    def ObserveTriggers(self, request: Any, context: Any) -> contract.TriggerList:
        held = contract.TriggerView(
            trigger_id=7,
            state=contract.TriggerView.HELD,
            spec=contract.TriggerSpec(label="BUTTON:fall", armed_by="window 1"),
            fires=1,
            last_fired_at_us=2_500_000,
            hold_at_us=2_501_000,
        )
        return contract.TriggerList(triggers=[held])


@pytest.fixture
def servicer() -> TriggerServicer:
    return TriggerServicer()


@pytest.fixture
def inspector(servicer: TriggerServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_a_trigger_is_armed_as_the_contract_carries_it(
    inspector: GrpcInspector, servicer: TriggerServicer
) -> None:
    request = TriggerRequest(Edge(4, Polarity.FALL), label="press", pre_us=200, post_us=800)

    armed = inspector.arm_trigger(request, "looper-py 1")

    assert servicer.spec is not None
    assert servicer.spec.condition.edge.polarity == contract.EDGE_FALL
    assert (servicer.spec.pre_us, servicer.spec.post_us, servicer.spec.capture_us) == (
        200,
        800,
        1000,
    )
    assert servicer.spec.mode == contract.TRIGGER_MODE_SINGLE
    assert servicer.spec.armed_by == "looper-py 1"
    assert (armed.trigger_id, armed.description, armed.label) == (7, "BUTTON falls", "press")


def test_a_condition_the_simulation_cannot_watch_for_is_a_refusal_with_its_text(
    inspector: GrpcInspector, servicer: TriggerServicer
) -> None:
    servicer.arm_ack = REFUSED_SEQUENCE

    with pytest.raises(SimulationRefusedError, match="Sequence triggers are not supported yet"):
        inspector.arm_trigger(TriggerRequest(Edge(4)), "looper-py 1")


def test_a_disarm_says_who_disarmed(inspector: GrpcInspector, servicer: TriggerServicer) -> None:
    disarmed = inspector.disarm_trigger(7, "looper-py 1")

    assert servicer.choice == contract.TriggerChoice(trigger_id=7, by_client="looper-py 1")
    assert (disarmed.state, disarmed.disarmed_by) == (TriggerState.DISARMED, "looper-py 1")


def test_the_listing_keeps_when_a_trigger_fired_and_where_it_holds(
    inspector: GrpcInspector,
) -> None:
    (held,) = inspector.read_triggers()

    assert held.state is TriggerState.HELD
    assert held.mode is TriggerMode.SINGLE
    assert (held.fires, held.last_fired_at_us, held.hold_at_us) == (1, 2_500_000, 2_501_000)
    assert held.armed_by == "window 1"
    assert held.is_live


def test_every_kind_of_condition_lands_in_its_own_field() -> None:
    conditions: dict[str, TriggerCondition] = {
        "edge_while": EdgeWhile(Edge(17, Polarity.RISE), (PinLevel(4, high=False),)),
        "width": Width(17, high=True, comparison=Comparison.GT, duration_us=600),
        "quiet": Quiet(4, duration_us=5_000),
        "value": Value(1001, Comparison.GE, value=3, mask=0xF),
    }

    for field, condition in conditions.items():
        assert condition_of(condition).WhichOneof("kind") == field


def test_a_width_and_a_value_keep_their_comparison() -> None:
    width = condition_of(Width(17, high=False, comparison=Comparison.LT, duration_us=50)).width
    value = condition_of(Value(1001, on_change=True)).value

    assert (width.op, width.high, width.duration_us) == (contract.CMP_LT, False, 50)
    assert value.on_change
