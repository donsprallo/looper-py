"""The chains of a signal graph between the domain and the contract, both ways."""

from __future__ import annotations

from looper.domain.model.chain_blocks import (
    BusReply,
    BusSend,
    ChainAction,
    ChainBlockState,
    Counter,
    Delay,
    EventBlock,
    Field,
    Hold,
    Logic,
    Mark,
    SetPin,
    Threshold,
)
from looper.domain.model.chain_scenarios import (
    Fault,
    RaiseInterrupt,
    ResetFirmware,
    Sequence,
    SwitchSignal,
)
from looper.domain.model.triggers import Polarity
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.scenario_translation import scenario_action_of, sequence_of
from looper.infrastructure.trigger_translation import condition_of


def block_request_of(block: EventBlock) -> contract.SignalNodeRequest:
    """One event block, as a node of the graph request."""
    request = contract.SignalNodeRequest(key=block.key, kind=block.kind, group_key=block.group)
    request.block.min_gap_us = block.min_gap_us
    settings = block.settings
    if isinstance(settings, SwitchSignal | Fault | RaiseInterrupt | ResetFirmware):
        request.block.action.CopyFrom(scenario_action_of(settings))
    elif isinstance(settings, Sequence):
        request.block.logic.CopyFrom(sequence_of(settings))
    elif isinstance(settings, SetPin | BusSend | BusReply | Mark | Hold):
        request.block.action.CopyFrom(_action_of(settings))
        request.inputs.extend(_field_inputs(settings))
    elif isinstance(settings, Threshold):
        request.block.threshold.CopyFrom(_threshold_of(settings))
        request.inputs.append(contract.SignalInputRequest(node=settings.signal))
    elif isinstance(settings, Delay | Counter | Logic):
        request.block.logic.CopyFrom(_logic_of(settings))
    else:
        request.block.condition.CopyFrom(condition_of(settings))
    return request


THRESHOLD_DIRECTIONS = {
    Polarity.RISE: contract.EDGE_RISE,
    Polarity.FALL: contract.EDGE_FALL,
    Polarity.ANY: contract.EDGE_ANY,
}


def _threshold_of(threshold: Threshold) -> contract.ThresholdSettings:
    return contract.ThresholdSettings(
        level=threshold.level,
        hysteresis=threshold.hysteresis,
        direction=THRESHOLD_DIRECTIONS[threshold.direction],
        check_us=threshold.check_us,
    )


def _logic_of(logic: Delay | Counter | Logic) -> contract.ChainLogic:
    match logic:
        case Delay(delay_us, while_waiting):
            delay = contract.DelayLogic(delay_us=delay_us, while_waiting=int(while_waiting))  # type: ignore[arg-type]
            return contract.ChainLogic(delay=delay)
        case Counter(n, only_nth):
            return contract.ChainLogic(counter=contract.CounterLogic(n=n, only_nth=only_nth))
        case Logic(kind):
            field = {"once": "once", "and": "all_of", "or": "any_of", "gate": "gate"}[kind]
            chain_logic = contract.ChainLogic()
            getattr(chain_logic, field).SetInParent()
            return chain_logic


def _signals_of(fields: tuple[Field, ...]) -> list[str]:
    """The signal nodes a message's fields read, each once, in order."""
    return list(dict.fromkeys(one.signal for one in fields if one.signal))


def _field_inputs(action: ChainAction) -> list[contract.SignalInputRequest]:
    fields = action.fields if isinstance(action, BusSend | BusReply) else ()
    return [contract.SignalInputRequest(node=node) for node in _signals_of(fields)]


def _field_of(one: Field, signals: list[str]) -> contract.MessageField:
    field = contract.MessageField(
        name=one.name,
        start_bit=one.start_bit,
        length=one.length,
        big_endian=one.big_endian,
        is_signed=one.is_signed,
        scale=one.scale,
        offset=one.offset,
    )
    if one.signal:
        field.signal_input = signals.index(one.signal)
    elif one.count:
        field.count.SetInParent()
    elif one.request_bit is not None:
        field.request_bit = one.request_bit
    else:
        field.constant = one.constant
    return field


def _message_of(
    message: contract.BusMessage, fields: tuple[Field, ...], length: int
) -> contract.BusMessageAction:
    signals = _signals_of(fields)
    return contract.BusMessageAction(
        message=message, fields=[_field_of(one, signals) for one in fields], length=length
    )


def _action_of(action: SetPin | BusSend | BusReply | Mark | Hold) -> contract.ChainAction:
    match action:
        case SetPin(pin_id, do, press_us):
            return contract.ChainAction(
                pin=contract.PinAction(pin_id=pin_id, action=int(do), press_us=press_us)  # type: ignore[arg-type]
            )
        case BusSend(bus_id, address, payload, extended, text, fields, length):
            message = contract.BusMessage(
                bus_id=bus_id, address=address, payload=payload, extended=extended
            )
            send = _message_of(message, fields, length)
            send.text = text
            return contract.ChainAction(send=send)
        case BusReply(bus_id, address, payload, extended, after_us, fields, length):
            message = contract.BusMessage(
                bus_id=bus_id, address=address, payload=payload, extended=extended
            )
            answer = _message_of(message, fields, length)
            answer.answer_after_us = after_us
            return contract.ChainAction(reply=answer)
        case Mark(text):
            return contract.ChainAction(mark=contract.MarkAction(text=text))
        case Hold(after_us):
            return contract.ChainAction(hold=contract.HoldAction(after_us=after_us))


def block_states_of(listing: contract.ChainList) -> tuple[ChainBlockState, ...]:
    """Every block the server reports, in its words."""
    return tuple(
        ChainBlockState(
            key=node.node_key,
            group=node.group_key,
            installed=node.installed,
            fires=node.fire_count,
            last_fired_at_us=node.last_fire_us,
            state_text=node.state_text,
            summary_text=node.summary_text,
            problem=node.refusal_text,
        )
        for node in listing.nodes
    )
