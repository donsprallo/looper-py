"""The applied signal graph, from the contract's view into the domain.

Field for field: the trace channels of the probes, the pin targets with
their levels and sentences, the block texts and values of the comparators,
linked generators, selects and sample and hold nodes. Nothing is
worked out here; every text is the server's. The starters a graph can
begin with come the same way.
"""

from __future__ import annotations

from looper.domain.model import GraphNodeState, GraphProbe, PinTargetState, SignalGraphState
from looper.domain.model.graph_liveness import (
    BlockLiveness,
    BlockState,
    GraphCapacity,
    GraphValueState,
    LabelState,
)
from looper.domain.model.signal_starters import Starter, StarterNeeds, Starters
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def graph_state_of(message: contract.SignalGraphView) -> SignalGraphState:
    """What the applied graph records and drives now."""
    return SignalGraphState(
        probes=tuple(
            GraphProbe(one.name, one.channel_id, one.node, one.output, one.is_live)
            for one in message.probes
        ),
        pin_targets=tuple(_pin_target_of(one) for one in message.pin_targets),
        nodes=tuple(_node_of(one) for one in message.nodes),
        node_states=tuple(_block_state_of(one) for one in message.node_states),
        labels=tuple(_label_of(one) for one in message.labels),
        capacity=_capacity_of(message.capacity),
        values=tuple(_value_of(one) for one in message.values),
        liveness_fault=message.liveness_fault,
    )


#: Whether a block runs, by the contract's numbers.
LIVENESS = {
    contract.SignalNodeStateView.LIVE: BlockLiveness.LIVE,
    contract.SignalNodeStateView.SWITCHED_OFF: BlockLiveness.SWITCHED_OFF,
    contract.SignalNodeStateView.LEFT_OUT: BlockLiveness.LEFT_OUT,
}


def _block_state_of(message: contract.SignalNodeStateView) -> BlockState:
    return BlockState(message.node, LIVENESS[message.state], message.state_text)


def _label_of(message: contract.SignalLabelView) -> LabelState:
    """One label; its value and fallback only where the server gives them."""
    return LabelState(
        name=message.name,
        writer_node=message.writer_node,
        on_fallback=message.on_fallback,
        is_live=message.is_live,
        value=message.value if message.HasField("value") else None,
        unit=message.unit,
        writer_nodes=tuple(message.writer_nodes),
        reader_nodes=tuple(message.reader_nodes),
        state_text=message.state_text,
        fallback=message.fallback if message.HasField("fallback") else None,
    )


def _capacity_of(message: contract.SignalCapacityView) -> GraphCapacity:
    return GraphCapacity(
        nodes_used=message.nodes_used,
        nodes_max=message.nodes_max,
        models_used=message.models_used,
        models_max=message.models_max,
        linear_used=message.linear_used,
        linear_max=message.linear_max,
        probes_used=message.probes_used,
        probes_max=message.probes_max,
        text=message.text,
    )


def _value_of(message: contract.GraphValueView) -> GraphValueState:
    return GraphValueState(
        node=message.node,
        value=message.value,
        unit=message.unit,
        feeds_text=message.feeds_text,
        last_writer_text=message.last_writer_text,
        state_text=message.state_text,
    )


def _node_of(message: contract.SignalNodeView) -> GraphNodeState:
    """One reported node; the value only where the server gives one."""
    return GraphNodeState(
        node=message.node,
        summary_text=message.summary_text,
        value_text=message.value_text,
        hover_lines=tuple(message.hover_lines),
        passing_port=message.passing_port,
        value=message.value if message.HasField("value") else None,
        samples=message.samples,
        sampled_us=message.sampled_us,
        fault_text=message.fault_text,
    )


def _pin_target_of(message: contract.PinTargetView) -> PinTargetState:
    return PinTargetState(
        pin_id=message.pin_id,
        pin_name=message.pin_name,
        node=message.node,
        output=message.output,
        high=message.high,
        value_text=message.value_text,
        edges=message.edges,
        fault_text=message.fault_text,
        resolution_text=message.resolution_text,
        check_text=message.check_text,
        level_text=message.level_text,
    )


def starters_of(message: contract.StarterList) -> Starters:
    """The starters in the library's order, or why there are none."""
    return Starters(
        starters=tuple(_starter_of(one) for one in message.starters),
        unavailable_reason=message.unavailable_reason,
    )


def _starter_of(message: contract.StarterView) -> Starter:
    needs = message.needs
    return Starter(
        name=message.name,
        display_name=message.display_name,
        description=message.description,
        search_words=tuple(message.search_words),
        graph_text=message.graph_text,
        needs=StarterNeeds(
            needs.input_pins, needs.output_pins, needs.analog_inputs, tuple(needs.models)
        ),
        needs_text=message.needs_text,
        is_available=message.is_available,
        unavailable_text=message.unavailable_text,
    )
