"""The applied signal graph, from the contract's view into the domain.

Field for field: the trace channels of the probes, the pin targets with
their levels and sentences, the block texts and values of the comparators,
linked generators, selects and sample and hold nodes. Nothing is
worked out here; every text is the server's. The starters a graph can
begin with come the same way.
"""

from __future__ import annotations

from looper.domain.model import GraphNodeState, GraphProbe, PinTargetState, SignalGraphState
from looper.domain.model.signal_starters import Starter, StarterNeeds, Starters
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def graph_state_of(message: contract.SignalGraphView) -> SignalGraphState:
    """What the applied graph records and drives now."""
    return SignalGraphState(
        probes=tuple(
            GraphProbe(one.name, one.channel_id, one.node, one.output) for one in message.probes
        ),
        pin_targets=tuple(_pin_target_of(one) for one in message.pin_targets),
        nodes=tuple(_node_of(one) for one in message.nodes),
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
