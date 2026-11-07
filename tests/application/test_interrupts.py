"""A test reads the interrupt sources and raises one by its name."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper.application.ports import ProFeatureLockedError
from looper.application.simulation import Simulation
from looper.domain.model.interrupt_facts import RunFindingReading


def _simulation() -> tuple[Simulation, ScriptedInspector]:
    inspector = ScriptedInspector()
    return Simulation(inspector), inspector


def test_the_sources_are_read_with_the_server_s_texts() -> None:
    simulation, _ = _simulation()

    interrupts = simulation.interrupts()

    assert interrupts.source("TIM2").kind_text == "timer, every 1 ms"
    assert interrupts.source("TIM2").handled == 9


def test_a_source_is_raised_by_its_name_now_or_later() -> None:
    simulation, inspector = _simulation()

    simulation.raise_interrupt("EXTI0")
    simulation.raise_interrupt("TIM2", after_us=500)

    assert inspector.raised == [(1, 0), (2, 500)]


def test_a_source_that_is_not_there_is_named() -> None:
    simulation, _ = _simulation()

    with pytest.raises(KeyError, match="EXTI9"):
        simulation.raise_interrupt("EXTI9")


def test_an_interrupt_check_reads_the_server_s_findings_and_is_pro() -> None:
    simulation, inspector = _simulation()
    check = simulation.expect()
    check.interrupt("TIM2").never_lost()
    inspector.findings_locked = True

    with pytest.raises(ProFeatureLockedError, match="part of looper Pro"):
        check.evaluate(for_seconds=0.01)


def test_with_the_licence_the_run_findings_are_checked() -> None:
    simulation, inspector = _simulation()
    inspector.run_findings = (RunFindingReading("IRQ_LOST", "TIM2 was lost"),)
    check = simulation.expect()
    check.run_findings().none()

    report = check.evaluate(for_seconds=0.01)

    assert not report.outcomes[0].met
    assert report.outcomes[0].observed == "TIM2 was lost"


def test_the_dma_channels_are_read_with_the_server_s_texts() -> None:
    simulation, _ = _simulation()

    channel = simulation.dma().channel("USART2_RX")

    assert (channel.peripheral_text, channel.buffer_name) == ("UART 2 -> rx_buf", "rx_buf")


def test_a_dma_check_reads_the_channels_and_the_findings() -> None:
    simulation, inspector = _simulation()
    inspector.run_findings = (RunFindingReading("DMA_OVERRUN", "USART2_RX overran", dma_id=1),)
    check = simulation.expect()
    check.dma("USART2_RX").no_overrun()
    check.dma("USART2_RX").length_fits()

    overrun, length = check.evaluate(for_seconds=0.01).outcomes

    assert (overrun.met, overrun.observed) == (False, "USART2_RX overran")
    assert length.met


def test_the_race_mode_runs_for_a_block_on_a_source_by_its_name() -> None:
    simulation, inspector = _simulation()

    with simulation.race("TIM2") as race:
        coverage = race.coverage()

    assert inspector.races == [(True, 2), (False, 0)]
    assert coverage.complete
    assert coverage.text == "3 of 3 points, 1 cycle"


def test_the_race_mode_is_pro() -> None:
    simulation, inspector = _simulation()
    inspector.findings_locked = True

    with pytest.raises(ProFeatureLockedError), simulation.race("TIM2"):
        pass


def test_the_interrupt_dma_and_race_readings_are_part_of_the_package() -> None:
    import looper

    exported = {
        "Interrupts",
        "InterruptSource",
        "InterruptLock",
        "DmaChannels",
        "DmaChannel",
        "RaceCoverage",
    }

    assert exported <= set(looper.__all__)
    assert all(hasattr(looper, name) for name in exported)
