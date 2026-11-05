"""The signal graph and the models it can use, between the domain and the contract.

A graph goes out as the contract's request, field for field; the models
come back as the project lists them. Nothing is checked here: whether a
graph holds together is the simulation's to say, and it says so in its
acknowledgement.
"""

from __future__ import annotations

from looper.domain.model import (
    ModelParameter,
    NodeOutput,
    SignalGraph,
    SignalModel,
    SignalNode,
    SignalNodeKind,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def signal_graph_request_of(graph: SignalGraph) -> contract.SignalGraphRequest:
    """A whole graph, as the contract carries it."""
    return contract.SignalGraphRequest(
        nodes=[_node_request_of(one) for one in graph.nodes],
        targets=[
            contract.SignalTargetRequest(
                channel_id=one.channel_id, node=one.node, output=one.output
            )
            for one in graph.targets
        ],
        probes=[
            contract.SignalProbeRequest(name=one.name, node=one.node, output=one.output)
            for one in graph.probes
        ],
    )


def models_of(message: contract.ModelList) -> tuple[SignalModel, ...]:
    """The models the project offers, usable or not."""
    return tuple(_model_of(one) for one in message.models)


def _node_request_of(node: SignalNode) -> contract.SignalNodeRequest:
    """One node; a generator carries its signal, the others leave it out."""
    request = contract.SignalNodeRequest(
        key=node.key,
        kind=node.kind.value,
        source=node.source,
        inputs=[_input_request_of(one) for one in node.inputs],
        model=node.model,
        parameters=dict(node.parameters),
        interpreted=node.interpreted,
    )
    if node.kind is SignalNodeKind.GENERATOR:
        request.signal.CopyFrom(_signal_view_of(node))
    return request


def _input_request_of(read: NodeOutput) -> contract.SignalInputRequest:
    return contract.SignalInputRequest(node=read.node, output=read.output)


def _signal_view_of(node: SignalNode) -> contract.SignalView:
    signal = node.signal
    return contract.SignalView(
        waveform=signal.waveform,
        amplitude=signal.amplitude,
        offset=signal.offset,
        frequency_hz=signal.frequency_hz,
        phase_degrees=signal.phase_degrees,
    )


def _model_of(message: contract.ModelView) -> SignalModel:
    return SignalModel(
        name=message.name,
        description=message.description,
        inputs=tuple(message.inputs),
        outputs=tuple(message.outputs),
        parameters=tuple(
            ModelParameter(name=one.name, default_value=one.default_value, unit=one.unit)
            for one in message.parameters
        ),
        kind=message.kind,
        origin=message.origin,
        problem=message.problem,
    )
