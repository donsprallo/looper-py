"""Chains through the gRPC adapter, against a scripted server in this process."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import BusReceived, BusReply, BusSend, Edge, Polarity, SetPin, SignalGraph
from looper.domain.model import PinDo
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector
from looper.infrastructure.signal_graph_translation import signal_graph_request_of

BUTTON = 4


class ChainServicer(service.InspectorServicer):  # type: ignore[misc]
    """Lists one block and notes the switch it is asked for."""

    def __init__(self) -> None:
        self.switch: contract.ChainGroupSwitch | None = None

    def ObserveChains(self, request: Any, context: Any) -> contract.ChainList:
        node = contract.ChainNodeView(
            node_key="falls",
            group_key="echo",
            installed=True,
            fire_count=3,
            last_fire_us=1_500_000,
            state_text="✶ fired 3× · last 1.500000 s",
            summary_text="BUTTON falls",
        )
        return contract.ChainList(nodes=[node])

    def SwitchChainGroup(self, request: Any, context: Any) -> contract.Ack:
        self.switch = request
        return contract.Ack()


@pytest.fixture
def servicer() -> ChainServicer:
    return ChainServicer()


@pytest.fixture
def inspector(servicer: ChainServicer) -> Iterator[GrpcInspector]:
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_a_graph_s_chains_go_out_as_event_blocks_links_and_groups() -> None:
    graph = (
        SignalGraph()
        .when("falls", Edge(BUTTON, Polarity.FALL), group="echo")
        .set_pin("press", SetPin(5, PinDo.HIGH), after="falls", group="echo")
        .send("tell", BusSend(1, 0x7E8, b"\x02\x41"), after="falls")
        .group("echo", "Echo")
    )

    request = signal_graph_request_of(graph)

    assert [(node.key, node.kind) for node in request.nodes] == [
        ("falls", "pin_edge"),
        ("press", "set_pin"),
        ("tell", "bus_send"),
    ]
    assert request.nodes[0].block.condition.edge.polarity == contract.EDGE_FALL
    assert request.nodes[1].block.action.pin.action == contract.PinAction.HIGH
    assert request.nodes[2].block.action.send.message.payload == b"\x02\x41"
    assert [(link.from_node, link.to_node) for link in request.event_links] == [
        ("falls", "press"),
        ("falls", "tell"),
    ]
    assert [(group.group_key, group.name) for group in request.groups] == [("echo", "Echo")]


def test_the_chains_are_read_in_the_server_s_words(inspector: GrpcInspector) -> None:
    (state,) = inspector.read_chains()

    assert state.key == "falls"
    assert state.fires == 3
    assert state.summary_text == "BUTTON falls"


def test_a_switch_names_the_group(inspector: GrpcInspector, servicer: ChainServicer) -> None:
    inspector.switch_chain("echo", False)

    assert servicer.switch is not None
    assert (servicer.switch.group_key, servicer.switch.enabled) == ("echo", False)


def test_a_reply_answers_what_a_bus_received_fired_on() -> None:
    graph = (
        SignalGraph()
        .when("request", BusReceived(1, 0x7E0, pattern=b"\x02"))
        .reply("answer", BusReply(1, 0x7E8, b"\x41", answer_after_us=5_000), after="request")
    )

    request = signal_graph_request_of(graph)

    received = request.nodes[0].block.condition.bus_received
    assert (request.nodes[0].kind, received.address, received.pattern) == (
        "bus_received",
        0x7E0,
        b"\x02",
    )
    assert received.direction == contract.DIRECTION_OUTBOUND
    assert request.nodes[1].kind == "bus_reply"
    assert request.nodes[1].block.action.reply.answer_after_us == 5_000
