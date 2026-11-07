"""The chains of a signal graph between the domain and the contract, both ways."""

from __future__ import annotations

from looper.domain.model.chain_blocks import (
    BusSend,
    ChainAction,
    ChainBlockState,
    EventBlock,
    Hold,
    Mark,
    SetPin,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.trigger_translation import condition_of


def block_request_of(block: EventBlock) -> contract.SignalNodeRequest:
    """One event block, as a node of the graph request."""
    request = contract.SignalNodeRequest(key=block.key, kind=block.kind, group_key=block.group)
    request.block.min_gap_us = block.min_gap_us
    if isinstance(block.settings, SetPin | BusSend | Mark | Hold):
        request.block.action.CopyFrom(_action_of(block.settings))
    else:
        request.block.condition.CopyFrom(condition_of(block.settings))
    return request


def _action_of(action: ChainAction) -> contract.ChainAction:
    match action:
        case SetPin(pin_id, do, press_us):
            return contract.ChainAction(
                pin=contract.PinAction(pin_id=pin_id, action=int(do), press_us=press_us)  # type: ignore[arg-type]
            )
        case BusSend(bus_id, address, payload, extended, text):
            message = contract.BusMessage(
                bus_id=bus_id, address=address, payload=payload, extended=extended
            )
            return contract.ChainAction(send=contract.BusMessageAction(message=message, text=text))
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
