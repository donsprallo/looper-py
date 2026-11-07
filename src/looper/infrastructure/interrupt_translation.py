"""The contract's interrupt and DMA messages, as the library's readings."""

from __future__ import annotations

from looper.domain.model.dma import DmaChannel, DmaChannels
from looper.domain.model.interrupt_facts import InterruptMark, RunFindingReading
from looper.domain.model.interrupts import InterruptLock, Interrupts, InterruptSource
from looper.domain.model.race import RaceCoverage
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def interrupts_of(report: contract.InterruptReport) -> Interrupts:
    """The report as readings."""
    return Interrupts(
        sources=tuple(_source(source) for source in report.sources),
        lock=InterruptLock(
            disabled_now=report.lock.disabled_now,
            sections=report.lock.sections,
            longest_us=report.lock.longest_us,
            total_us=report.lock.total_us,
        ),
        installed=report.installed,
        note=report.note,
    )


def _source(source: contract.InterruptSourceView) -> InterruptSource:
    return InterruptSource(
        source_id=source.source_id,
        name=source.name,
        kind_text=source.kind_text,
        handler=source.handler,
        priority=source.priority,
        enabled=source.enabled,
        pending=source.pending,
        raised=source.raised,
        handled=source.handled,
        lost=source.lost,
        latency_max_us=source.latency_max_us,
        latency_mean_us=source.latency_mean_us,
        duration_max_us=source.duration_max_us,
        duration_mean_us=source.duration_mean_us,
        period_us=source.period_us,
        is_raisable=source.is_raisable,
        state_text=source.state_text,
    )


#: The contract's words for the kinds of interrupt event.
EVENT_KINDS = {
    contract.INTERRUPT_EVENT_PENDING: "pending",
    contract.INTERRUPT_EVENT_ENTERED: "entered",
    contract.INTERRUPT_EVENT_LEFT: "left",
    contract.INTERRUPT_EVENT_LOST: "lost",
    contract.INTERRUPT_EVENT_LOCKED: "locked",
    contract.INTERRUPT_EVENT_STORM: "storm",
}
SEVERITIES = {
    contract.TIER_GOOD: "note",
    contract.TIER_NOTICEABLE: "noticeable",
    contract.TIER_CRITICAL: "critical",
}


def marks_of(message: contract.EventBatch) -> tuple[InterruptMark, ...]:
    """The interrupt events of a page."""
    return tuple(
        InterruptMark(
            sim_us=one.sim_us,
            source_id=one.interrupt.source_id,
            kind=EVENT_KINDS.get(one.interrupt.kind, "pending"),
            latency_us=one.interrupt.latency_us,
            duration_us=one.interrupt.duration_us,
            by_race=one.interrupt.by_race,
        )
        for one in message.events
        if one.HasField("interrupt")
    )


def findings_of(message: contract.RunFindingList) -> tuple[RunFindingReading, ...]:
    """The run's findings, in the server's words."""
    return tuple(
        RunFindingReading(
            kind=one.kind,
            title=one.title,
            severity=SEVERITIES.get(one.severity, "critical"),
            occurrences=one.occurrences,
            check_text=one.check_text,
            source_id=one.source_id,
            dma_id=one.dma_id,
        )
        for one in message.findings
    )


def raise_request(source_id: int, after_us: int) -> contract.InterruptRaise:
    """Raising a source, now or so long after the server takes it."""
    if after_us <= 0:
        return contract.InterruptRaise(source_id=source_id)
    return contract.InterruptRaise(source_id=source_id, when=contract.When(after_us=after_us))


#: The contract's words for the guard over a channel's buffer.
GUARDS = {
    contract.DMA_GUARD_OFF: "off",
    contract.DMA_GUARD_PRECISE: "precise",
    contract.DMA_GUARD_COARSE: "coarse",
    contract.DMA_GUARD_DOWNGRADED: "downgraded",
    contract.DMA_GUARD_UNAVAILABLE: "unavailable",
    contract.DMA_GUARD_DEBUGGER: "debugger",
    contract.DMA_GUARD_STACK: "stack",
    contract.DMA_GUARD_LOCKED: "locked",
}


def dma_of(report: contract.DmaReport) -> DmaChannels:
    """The channels as readings."""
    return DmaChannels(
        channels=tuple(_channel(one) for one in report.channels),
        installed=report.installed,
        note=report.note,
    )


def _channel(channel: contract.DmaChannelView) -> DmaChannel:
    return DmaChannel(
        dma_id=channel.dma_id,
        name=channel.name,
        peripheral_text=channel.peripheral_text,
        direction=channel.direction,
        mode=channel.mode,
        running=channel.running,
        buffer_name=channel.buffer_name,
        buffer_bytes=channel.buffer_bytes,
        length=channel.length,
        width=channel.width,
        position=channel.position,
        announced=channel.announced,
        laps=channel.laps,
        elements=channel.elements,
        overruns=channel.overruns,
        unclaimed=channel.unclaimed,
        guard=GUARDS.get(channel.guard, "off"),
        guard_text=channel.guard_text,
        neighbours=tuple(channel.neighbours),
        state_text=channel.state_text,
    )


def race_of(view: contract.RaceView) -> RaceCoverage:
    """The race mode as a reading."""
    return RaceCoverage(
        on=view.on,
        source=view.source_name,
        points_seen=view.points_seen,
        points_covered=view.points_covered,
        cycles=view.cycles,
        text=view.coverage_text,
        uncovered=tuple(place.what for place in view.uncovered),
    )
