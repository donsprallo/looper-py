"""The interrupts part of the scripted inspector: a fixed report, and what was raised."""

from __future__ import annotations

from looper.application.ports import ProFeatureLockedError, SimulationRefusedError
from looper.domain.model.dma import DmaChannel, DmaChannels
from looper.domain.model.interrupt_facts import RunFindingReading
from looper.domain.model.interrupts import Interrupts, InterruptSource

#: The sources a scripted firmware has: a button and a timer.
BUTTON = InterruptSource(1, "EXTI0", kind_text="pin 1, falling edge", is_raisable=True)
TICK = InterruptSource(2, "TIM2", kind_text="timer, every 1 ms", is_raisable=True, handled=9)
#: The DMA channel a scripted firmware has: a UART receiving into rx_buf.
RX = DmaChannel(1, "USART2_RX", peripheral_text="UART 2 -> rx_buf", buffer_name="rx_buf")


class ScriptedInterrupts:
    """Answers the interrupt questions from a fixed report, and writes raises down."""

    def __init__(self) -> None:
        self.interrupt_report = Interrupts(sources=(BUTTON, TICK), installed=True)
        self.raised: list[tuple[int, int]] = []
        self.run_findings: tuple[RunFindingReading, ...] = ()
        self.findings_locked = False
        self.dma_report = DmaChannels(channels=(RX,), installed=True)

    def read_interrupts(self) -> Interrupts:
        return self.interrupt_report

    def read_dma(self) -> DmaChannels:
        return self.dma_report

    def read_run_findings(self) -> tuple[RunFindingReading, ...]:
        if self.findings_locked:
            raise ProFeatureLockedError("Run findings is part of looper Pro - no licence found.")
        return self.run_findings

    def raise_interrupt(self, source_id: int, after_us: int = 0) -> None:
        if all(source.source_id != source_id for source in self.interrupt_report.sources):
            raise SimulationRefusedError(f"there is no interrupt source {source_id}")
        self.raised.append((source_id, after_us))
