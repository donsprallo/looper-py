"""The signal graph and the models it can use, between the domain and the contract.

A graph goes out as the contract's request, field for field; the models
come back as the project lists them. Nothing is checked here: whether a
graph holds together is the simulation's to say, and it says so in its
acknowledgement.
"""

from __future__ import annotations

from looper.domain.model import (
    EventLink,
    ModelParameter,
    NodeOutput,
    SignalGraph,
    SignalLabel,
    SignalModel,
    SignalNode,
    SignalNodeKind,
    SignalProbe,
)
from looper.infrastructure.chain_translation import block_request_of
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.signal_translation import signal_view_of


def signal_graph_request_of(graph: SignalGraph) -> contract.SignalGraphRequest:
    """A whole graph, as the contract carries it."""
    return contract.SignalGraphRequest(
        nodes=[
            *(_node_request_of(one) for one in graph.nodes),
            *(block_request_of(one) for one in graph.event_blocks),
        ],
        event_links=[_link_request_of(one) for one in graph.event_links],
        groups=[
            contract.ChainGroupRequest(group_key=one.key, name=one.name, enabled=one.enabled)
            for one in graph.groups
        ],
        targets=[
            contract.SignalTargetRequest(
                channel_id=one.channel_id, node=one.node, output=one.output
            )
            for one in graph.targets
        ],
        probes=[_probe_request_of(one) for one in graph.probes],
        pin_targets=[
            contract.SignalPinTargetRequest(pin_id=one.pin_id, node=one.node, output=one.output)
            for one in graph.pin_targets
        ],
        labels=[_label_request_of(one) for one in graph.labels],
    )


def _label_request_of(label: SignalLabel) -> contract.SignalLabelRequest:
    """A label; one without a fallback leaves the field unset, which is not a fallback of 0."""
    request = contract.SignalLabelRequest(name=label.name)
    if label.fallback is not None:
        request.fallback = label.fallback
    return request


def _link_request_of(link: EventLink) -> contract.EventLinkRequest:
    return contract.EventLinkRequest(
        from_node=link.from_node,
        from_port=link.from_port,
        to_node=link.to_node,
        to_port=link.to_port,
    )


def _probe_request_of(probe: SignalProbe) -> contract.SignalProbeRequest:
    return contract.SignalProbeRequest(
        name=probe.name, node=probe.node, output=probe.output, sample_us=probe.sample_us
    )


def models_of(message: contract.ModelList) -> tuple[SignalModel, ...]:
    """The models the project offers, usable or not."""
    return tuple(_model_of(one) for one in message.models)


def _node_request_of(node: SignalNode) -> contract.SignalNodeRequest:
    """One node; a generator carries its signal, a comparator or a sample and hold its settings."""
    request = _plain_node_request_of(node)
    if node.kind is SignalNodeKind.GENERATOR:
        request.signal.CopyFrom(signal_view_of(node.signal))
    if node.kind is SignalNodeKind.COMPARE:
        request.compare.CopyFrom(_compare_settings_of(node))
    if node.kind is SignalNodeKind.SAMPLE_HOLD:
        sample = node.sample
        request.sample.CopyFrom(contract.SampleSettings(mode=sample.mode, initial=sample.initial))
    return request


def _plain_node_request_of(node: SignalNode) -> contract.SignalNodeRequest:
    """The fields every kind of node has, its group and its label among them."""
    return contract.SignalNodeRequest(
        key=node.key,
        kind=node.kind.value,
        source=node.source,
        inputs=[_input_request_of(one) for one in node.inputs],
        model=node.model,
        parameters=dict(node.parameters),
        interpreted=node.interpreted,
        value=node.value,
        parameter_sources=dict(node.parameter_sources),
        linked_fields=node.linked_fields,
        hold_pulses=node.hold_pulses,
        group_key=node.group,
        label=node.label,
        switched_off=node.switched_off,
        title=node.title,
        negated_inputs=node.negated_inputs,
    )


def _input_request_of(read: NodeOutput) -> contract.SignalInputRequest:
    return contract.SignalInputRequest(node=read.node, output=read.output)


def _compare_settings_of(node: SignalNode) -> contract.CompareSettings:
    settings = node.compare
    return contract.CompareSettings(
        level=settings.level,
        hysteresis=settings.hysteresis,
        below=settings.below,
        linked=settings.linked,
        check_us=settings.check_us,
    )


def _model_of(message: contract.ModelView) -> SignalModel:
    return SignalModel(
        name=message.name,
        description=message.description,
        inputs=tuple(message.inputs),
        outputs=tuple(message.outputs),
        parameters=tuple(_parameter_of(one) for one in message.parameters),
        kind=message.kind,
        origin=message.origin,
        problem=message.problem,
        group=message.group,
        keywords=tuple(message.keywords),
    )


def _parameter_of(message: contract.ModelParameterView) -> ModelParameter:
    """One parameter, with its limits where the model declares them."""
    return ModelParameter(
        name=message.name,
        default_value=message.default_value,
        unit=message.unit,
        lowest=message.lowest if message.HasField("lowest") else None,
        highest=message.highest if message.HasField("highest") else None,
        description=message.description,
    )
