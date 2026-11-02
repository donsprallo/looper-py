"""Triggers between the domain and the inspector contract, both ways.

The contract numbers its enumerations; the domain names them. Both tables
are written out here, one entry per value, so that a new value in either
place fails loudly instead of meaning something else.
"""

from __future__ import annotations

from looper.domain.model import (
    Comparison,
    Edge,
    EdgeWhile,
    Pattern,
    PinLevel,
    Polarity,
    Quiet,
    Trigger,
    TriggerCondition,
    TriggerMode,
    TriggerRequest,
    TriggerState,
    Value,
    Width,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract

POLARITIES = {
    Polarity.RISE: contract.EDGE_RISE,
    Polarity.FALL: contract.EDGE_FALL,
    Polarity.ANY: contract.EDGE_ANY,
}

COMPARISONS = {
    Comparison.EQ: contract.CMP_EQ,
    Comparison.NE: contract.CMP_NE,
    Comparison.LT: contract.CMP_LT,
    Comparison.LE: contract.CMP_LE,
    Comparison.GT: contract.CMP_GT,
    Comparison.GE: contract.CMP_GE,
}

MODES = {
    TriggerMode.SINGLE: contract.TRIGGER_MODE_SINGLE,
    TriggerMode.NORMAL: contract.TRIGGER_MODE_NORMAL,
}

STATES = {
    contract.TriggerView.ARMED: TriggerState.ARMED,
    contract.TriggerView.FIRED: TriggerState.FIRED,
    contract.TriggerView.HELD: TriggerState.HELD,
    contract.TriggerView.DISARMED: TriggerState.DISARMED,
    contract.TriggerView.REFUSED: TriggerState.REFUSED,
}


def spec_of(request: TriggerRequest, armed_by: str) -> contract.TriggerSpec:
    """The request as the server is asked to arm it."""
    spec = contract.TriggerSpec(
        label=request.label,
        condition=condition_of(request.condition),
        mode=MODES[request.mode],
        pre_us=request.pre_us,
        post_us=request.post_us,
        capture_us=request.pre_us + request.post_us,
        armed_by=armed_by,
    )
    if request.replaces_trigger_id is not None:
        spec.replaces_trigger_id = request.replaces_trigger_id
    return spec


def condition_of(condition: TriggerCondition) -> contract.TriggerCondition:
    """One condition of the domain as the contract's oneof."""
    match condition:
        case Edge():
            return contract.TriggerCondition(edge=_edge_of(condition))
        case Pattern(levels):
            return contract.TriggerCondition(
                pattern=contract.PatternCondition(levels=_levels_of(levels))
            )
        case EdgeWhile(edge, levels):
            edge_while = contract.EdgeWhileCondition(edge=_edge_of(edge), levels=_levels_of(levels))
            return contract.TriggerCondition(edge_while=edge_while)
        case Width():
            return contract.TriggerCondition(width=_width_of(condition))
        case Quiet(pin_id, duration_us):
            quiet = contract.QuietCondition(pin_id=pin_id, duration_us=duration_us)
            return contract.TriggerCondition(quiet=quiet)
        case Value():
            return contract.TriggerCondition(value=_value_of(condition))


def trigger_of(view: contract.TriggerView) -> Trigger:
    """What the server said of one trigger."""
    single = view.spec.mode == contract.TRIGGER_MODE_SINGLE
    return Trigger(
        trigger_id=view.trigger_id,
        label=view.spec.label,
        description=view.description,
        state=STATES[view.state],
        mode=TriggerMode.SINGLE if single else TriggerMode.NORMAL,
        fires=view.fires,
        armed_at_us=view.armed_at_us,
        last_fired_at_us=view.last_fired_at_us,
        hold_at_us=view.hold_at_us,
        armed_by=view.spec.armed_by,
        disarmed_by=view.disarmed_by,
    )


def _edge_of(edge: Edge) -> contract.EdgeCondition:
    return contract.EdgeCondition(pin_id=edge.pin_id, polarity=POLARITIES[edge.polarity])


def _levels_of(levels: tuple[PinLevel, ...]) -> list[contract.PinLevelCondition]:
    return [contract.PinLevelCondition(pin_id=level.pin_id, high=level.high) for level in levels]


def _width_of(width: Width) -> contract.WidthCondition:
    return contract.WidthCondition(
        pin_id=width.pin_id,
        high=width.high,
        op=COMPARISONS[width.comparison],
        duration_us=width.duration_us,
    )


def _value_of(value: Value) -> contract.ValueCondition:
    return contract.ValueCondition(
        channel_id=value.channel_id,
        op=COMPARISONS[value.comparison],
        value=value.value,
        mask=value.mask,
        on_change=value.on_change,
    )
