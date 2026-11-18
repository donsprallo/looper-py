"""The applied signal graph, from the contract's view into the domain.

Field for field: the trace channels of the probes, the pin targets with
their levels and sentences, the comparators' block texts. Nothing is
worked out here; every text is the server's.
"""

from __future__ import annotations

from looper.domain.model import GraphNodeState, GraphProbe, PinTargetState, SignalGraphState
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def graph_state_of(message: contract.SignalGraphView) -> SignalGraphState:
    """What the applied graph records and drives now."""
    return SignalGraphState(
        probes=tuple(
            GraphProbe(one.name, one.channel_id, one.node, one.output) for one in message.probes
        ),
        pin_targets=tuple(_pin_target_of(one) for one in message.pin_targets),
        nodes=tuple(
            GraphNodeState(one.node, one.summary_text, one.value_text, tuple(one.hover_lines))
            for one in message.nodes
        ),
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
