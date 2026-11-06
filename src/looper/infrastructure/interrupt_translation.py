"""The contract's interrupt messages, as the library's readings."""

from __future__ import annotations

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


def raise_request(source_id: int, after_us: int) -> contract.InterruptRaise:
    """Raising a source, now or so long after the server takes it."""
    if after_us <= 0:
        return contract.InterruptRaise(source_id=source_id)
    return contract.InterruptRaise(source_id=source_id, when=contract.When(after_us=after_us))
