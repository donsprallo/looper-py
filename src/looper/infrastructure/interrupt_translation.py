"""The contract's interrupt messages, as the library's readings."""

from __future__ import annotations

from looper.domain.model.interrupt_facts import InterruptMark, RunFindingReading
from looper.domain.model.interrupts import InterruptLock, Interrupts, InterruptSource
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
SEVERITIES = {contract.TIER_NOTICEABLE: "noticeable", contract.TIER_CRITICAL: "critical"}


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
        )
        for one in message.findings
    )


def raise_request(source_id: int, after_us: int) -> contract.InterruptRaise:
    """Raising a source, now or so long after the server takes it."""
    if after_us <= 0:
        return contract.InterruptRaise(source_id=source_id)
    return contract.InterruptRaise(source_id=source_id, when=contract.When(after_us=after_us))
