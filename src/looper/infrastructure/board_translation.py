"""The board and its live state, from the contract into the domain."""

from __future__ import annotations

from looper.domain.model.board import (
    Board,
    BoardEdge,
    BoardEdgeKind,
    BoardGraphRef,
    BoardNode,
    BoardNodeKind,
    BoardNote,
)
from looper.domain.model.board_state import BoardNodeState, BoardState, BoardTapState
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def board_of(view: contract.BoardView) -> Board:
    """The whole picture at its revision."""
    return Board(
        title=view.title,
        nodes=tuple(node_of(node) for node in view.nodes),
        edges=tuple(edge_of(edge) for edge in view.edges),
        notes=tuple(BoardNote(text=note.text, node_key=note.node_key) for note in view.notes),
        revision=view.revision,
        revision_text=view.revision_text,
        empty_text=view.empty_text,
    )


def node_of(node: contract.BoardNode) -> BoardNode:
    """One part, its kind named as the contract's enum names it."""
    return BoardNode(
        key=node.key,
        kind=BoardNodeKind(contract.BoardNode.Kind.Name(node.kind).lower()),
        title=node.title,
        parent_key=node.parent_key,
        subtitle=node.subtitle,
        bus_kind=node.bus_kind,
        runtime_id=node.runtime_id,
        registered=node.registered,
        unregistered_text=node.unregistered_text,
        hand_wired=node.hand_wired,
        hand_wired_text=node.hand_wired_text,
        is_input=node.is_input,
        graph_can_drive=node.graph_can_drive,
        graph_can_read=node.graph_can_read,
        drive_text=node.drive_text,
        hover_text=node.hover_text,
        driven_by_text=node.driven_by_text,
        driven_by_node_key=node.driven_by_node_key,
        read_by=tuple(graph_ref_of(reader) for reader in node.read_by),
        read_by_text=node.read_by_text,
        reference_text=node.reference_text,
        reference_node_key=node.reference_node_key,
        endpoint_node_keys=tuple(node.endpoint_node_keys),
        second_driver_text=node.second_driver_text,
    )


def graph_ref_of(reader: contract.BoardGraphRef) -> BoardGraphRef:
    """A block or probe that reads a port."""
    return BoardGraphRef(text=reader.text, node_key=reader.node_key, probe=reader.probe)


def edge_of(edge: contract.BoardEdge) -> BoardEdge:
    """One wire."""
    return BoardEdge(
        from_key=edge.from_key,
        to_key=edge.to_key,
        kind=BoardEdgeKind(contract.BoardEdge.Kind.Name(edge.kind).lower()),
        text=edge.text,
        dashed=edge.dashed,
        hover_text=edge.hover_text,
    )


def board_state_of(state: contract.BoardState) -> BoardState:
    """The live state of the parts and taps that have one."""
    return BoardState(
        revision=state.revision,
        sim_us=state.sim_us,
        nodes=tuple(node_state_of(node) for node in state.nodes),
        taps=tuple(tap_state_of(edge) for edge in state.edges),
    )


def node_state_of(node: contract.BoardNodeState) -> BoardNodeState:
    """One part's live state; a value only where the server set one."""
    return BoardNodeState(
        key=node.key,
        state_text=node.state_text,
        active=node.active,
        fault=node.fault,
        fault_text=node.fault_text,
        driver_off=node.driver_off,
        reference_state_text=node.reference_state_text,
        value=node.value if node.HasField("value") else None,
        exchanges=node.exchanges,
        last_us=node.last_us,
    )


def tap_state_of(edge: contract.BoardEdgeState) -> BoardTapState:
    """One tap's live state."""
    return BoardTapState(
        from_key=edge.from_key,
        to_key=edge.to_key,
        state_text=edge.state_text,
        active=edge.active,
        fault=edge.fault,
        fault_text=edge.fault_text,
        hover_text=edge.hover_text,
        exchanges=edge.exchanges,
        unanswered=edge.unanswered,
        last_us=edge.last_us,
    )
