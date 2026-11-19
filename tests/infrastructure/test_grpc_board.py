"""The board and its live state through the gRPC adapter, against a scripted server."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import BoardEdgeKind, BoardNodeKind, SimulationRefusedError
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

NO_BOARD = "The device of a project without a simulation is not shown yet – it is coming."

ZC = contract.BoardNode(
    key="pin:ZC",
    kind=contract.BoardNode.PIN,
    parent_key="mcu",
    title="ZC",
    is_input=True,
    graph_can_drive=True,
    driven_by_text="Comparator",
    driven_by_node_key="zero_cross",
    read_by=[contract.BoardGraphRef(text='Probe "ZC"', probe="ZC")],
    reference_text="◁ Comparator",
    endpoint_node_keys=["zc_in"],
)
AS8510 = contract.BoardNode(key="device:SPI1:0", kind=contract.BoardNode.DEVICE, title="AS8510")
SPI1 = contract.BoardNode(key="bus:SPI1", kind=contract.BoardNode.BUS, title="SPI1", bus_kind="spi")
TAP = contract.BoardEdge(
    from_key="device:SPI1:0", to_key="bus:SPI1", kind=contract.BoardEdge.ON_BUS, text="CS 0"
)


class BoardServicer(service.InspectorServicer):  # type: ignore[misc]
    """Describes a board with one pin and one tap, or refuses once told to."""

    def __init__(self) -> None:
        self.refuse = False

    def Describe(self, request: Any, context: Any) -> contract.Description:
        return contract.Description(capabilities=[contract.CAPABILITY_BOARD])

    def DescribeBoard(self, request: Any, context: Any) -> contract.BoardView:
        if self.refuse:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, NO_BOARD)
        notes = [contract.BoardNote(text="AS8510 is wired in board code.", node_key=AS8510.key)]
        return contract.BoardView(
            title="blinky", nodes=[ZC, SPI1, AS8510], edges=[TAP], notes=notes, revision=3
        )

    def ObserveBoard(self, request: Any, context: Any) -> contract.BoardState:
        if self.refuse:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, NO_BOARD)
        nodes = [
            contract.BoardNodeState(key="pin:ZC", state_text="high", value=1.0),
            contract.BoardNodeState(key="bus:SPI1", exchanges=6, last_us=500_000),
        ]
        tap = contract.BoardEdgeState(
            from_key="device:SPI1:0", to_key="bus:SPI1", exchanges=6, unanswered=2
        )
        return contract.BoardState(revision=3, sim_us=600_000, nodes=nodes, edges=[tap])


@pytest.fixture
def servicer() -> BoardServicer:
    return BoardServicer()


@pytest.fixture
def inspector(servicer: BoardServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_the_capability_is_named_board(inspector: GrpcInspector) -> None:
    assert inspector.describe().capabilities == ("board",)


def test_a_port_comes_with_its_driver_its_readers_and_their_keys(inspector: GrpcInspector) -> None:
    board = inspector.read_board()
    zc = board.port("ZC")

    assert (board.title, board.revision, zc.kind) == ("blinky", 3, BoardNodeKind.PIN)
    assert (zc.driven_by_text, zc.driven_by_node_key, zc.reference_text) == (
        "Comparator",
        "zero_cross",
        "◁ Comparator",
    )
    assert (zc.read_by[0].text, zc.read_by[0].probe, zc.endpoint_node_keys) == (
        'Probe "ZC"',
        "ZC",
        ("zc_in",),
    )


def test_a_device_hangs_on_its_bus_at_its_tap(inspector: GrpcInspector) -> None:
    board = inspector.read_board()

    assert board.edges[0].kind == BoardEdgeKind.ON_BUS
    assert board.bus("SPI1").tap("AS8510").text == "CS 0"
    assert board.notes[0].node_key == "device:SPI1:0"


def test_the_state_keeps_an_unset_value_apart_from_zero(inspector: GrpcInspector) -> None:
    state = inspector.read_board_state()

    assert (state.revision, state.sim_us) == (3, 600_000)
    assert state.pin("ZC").value == 1.0  # type: ignore[union-attr]
    assert state.rail("SPI1").value is None  # type: ignore[union-attr]
    assert (state.rail("SPI1").exchanges, state.rail("SPI1").last_us) == (6, 500_000)  # type: ignore[union-attr]
    assert state.tap("device:SPI1:0").unanswered == 2  # type: ignore[union-attr]


def test_a_refusal_is_raised_with_the_server_s_sentence(
    inspector: GrpcInspector, servicer: BoardServicer
) -> None:
    servicer.refuse = True

    for read in (inspector.read_board, inspector.read_board_state):
        with pytest.raises(SimulationRefusedError) as refused:
            read()
        assert str(refused.value) == NO_BOARD
