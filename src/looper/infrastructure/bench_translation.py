"""The contract's bench messages as the domain's bench."""

from __future__ import annotations

from looper.domain.model.bench import (
    BenchDevice,
    BenchMark,
    BenchPhase,
    BenchState,
    JoinBusChoice,
    JoinCandidate,
    JoinCandidates,
    JoinedBus,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def bench_state_of(state: contract.BenchState) -> BenchState:
    """The bench as the server sees it."""
    return BenchState(
        revision=state.revision,
        revision_text=state.revision_text,
        phase=phase_of(state.phase),
        name=state.name,
        title=state.title,
        devices=tuple(device_of(device) for device in state.devices),
        buses=tuple(joined_bus_of(bus) for bus in state.buses),
        waiting_for_text=state.waiting_for_text,
        waiting_share_text=state.waiting_share_text,
        failed_text=state.failed_text,
        step_text=state.step_text,
        restart_text=state.restart_text,
        marks=tuple(BenchMark(one.sim_us, one.device, one.life, one.text) for one in state.marks),
        file_path=state.file_path,
    )


def phase_of(phase: int) -> BenchPhase:
    """``BENCH_PHASE_ON_BENCH`` as `BenchPhase.ON_BENCH`."""
    return BenchPhase(contract.BenchPhase.Name(phase).removeprefix("BENCH_PHASE_").lower())


def device_of(device: contract.BenchDevice) -> BenchDevice:
    """One device of the bench."""
    return BenchDevice(
        name=device.name,
        mcu=device.mcu,
        where_text=device.where_text,
        state_text=device.state_text,
        now_us=device.now_us,
        now_text=device.now_text,
        leader=device.leader,
        this_device=device.this_device,
        address=device.address,
        index=device.index,
        fault=device.fault,
        hover_text=device.hover_text,
    )


def joined_bus_of(bus: contract.JoinedBus) -> JoinedBus:
    """One joined bus of this device."""
    return JoinedBus(
        bus_id=bus.bus_id,
        label=bus.label,
        join=bus.join,
        peers_text=bus.peers_text,
        bitrate=bus.bitrate,
        frames=bus.frames,
        text=bus.text,
    )


def join_candidates_of(listing: contract.JoinCandidates) -> JoinCandidates:
    """What the Join dialog shows."""
    return JoinCandidates(
        title=listing.title,
        candidates=tuple(candidate_of(one) for one in listing.candidates),
    )


def candidate_of(candidate: contract.JoinCandidate) -> JoinCandidate:
    """One other server, joinable or not."""
    return JoinCandidate(
        instance_id=candidate.instance_id,
        address=candidate.address,
        firmware_name=candidate.firmware_name,
        definition_path=candidate.definition_path,
        joinable=candidate.joinable,
        reason_text=candidate.reason_text,
        buses=tuple(choice_of(bus) for bus in candidate.buses),
        joining_text=candidate.joining_text,
    )


def choice_of(bus: contract.JoinBusChoice) -> JoinBusChoice:
    """One bus of the other server."""
    return JoinBusChoice(
        bus_id=bus.bus_id,
        label=bus.label,
        text=bus.text,
        bitrate=bus.bitrate,
        preselected=bus.preselected,
        mismatch_text=bus.mismatch_text,
    )
