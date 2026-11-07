"""The scenario blocks of a chain and the Sequences' states, between the domain and the contract."""

from __future__ import annotations

from looper.domain.model.chain_runs import SequenceProgress, SequenceState
from looper.domain.model.chain_scenarios import (
    Fault,
    RaiseInterrupt,
    ResetFirmware,
    Sequence,
    SwitchSignal,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract

ScenarioAction = SwitchSignal | Fault | RaiseInterrupt | ResetFirmware


def scenario_action_of(action: ScenarioAction) -> contract.ChainAction:
    """A Switch signal, an Inject fault, a Raise interrupt or a Reset as the contract's action."""
    match action:
        case SwitchSignal(node, channel_id, do, to, over_us):
            switch = contract.SignalSwitchAction(
                node=node,
                channel_id=channel_id,
                action=int(do),  # type: ignore[arg-type]
                to=to,
                over_us=over_us,
            )
            return contract.ChainAction(signal=switch)
        case Fault():
            return contract.ChainAction(fault=_fault_of(action))
        case RaiseInterrupt(source_id):
            raised = contract.InterruptRaiseAction(source_id=source_id)
            return contract.ChainAction(interrupt=raised)
        case ResetFirmware(cause):
            reset = contract.ResetAction(cause=cause)  # type: ignore[arg-type]
            return contract.ChainAction(reset=reset)


def _fault_of(fault: Fault) -> contract.FaultAction:
    return contract.FaultAction(
        kind=int(fault.kind),  # type: ignore[arg-type]
        channel_id=fault.channel_id,
        for_us=fault.for_us,
        amplitude=fault.amplitude,
        bus_id=fault.bus_id,
        address=fault.address,
        address_mask=fault.address_mask,
        next=fault.next,
        byte_index=fault.byte_index,
        bit=fault.bit,
    )


def sequence_of(sequence: Sequence) -> contract.ChainLogic:
    """A Sequence as the contract's logic."""
    steps = [
        contract.SequenceStepRequest(
            kind=int(step.kind),  # type: ignore[arg-type]
            label=step.label,
            duration_us=step.duration_us,
        )
        for step in sequence.steps
    ]
    logic = contract.SequenceLogic(steps=steps, restart_on_start=sequence.restart_on_start)
    return contract.ChainLogic(sequence=logic)


def sequence_states_of(listing: contract.ChainList) -> tuple[SequenceState, ...]:
    """Every Sequence the server reports, with its group's key and name."""
    groups = {node.node_key: node.group_key for node in listing.nodes}
    names = {group.group_key: group.name for group in listing.groups}
    return tuple(
        SequenceState(
            key=one.node_key,
            group=groups.get(one.node_key, ""),
            group_name=names.get(groups.get(one.node_key, ""), ""),
            progress=SequenceProgress(one.state),
            step=one.step_index,
            step_count=one.step_count,
            step_text=one.step_text,
            failure_text=one.failure_text,
        )
        for one in listing.sequences
    )
