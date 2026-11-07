"""The checks of a firmware's DMA channels, on the server's findings about each channel."""

from __future__ import annotations

from looper.domain.checks.dma_checks import (
    NO_SUCH_CHANNEL,
    LengthFits,
    NoOverrun,
    NotAccessedWhileRunning,
)
from looper.domain.model import Observation
from looper.domain.model.dma import DmaChannel, DmaChannels
from looper.domain.model.interrupt_facts import RunFindingReading

CHANNELS = DmaChannels(channels=(DmaChannel(1, "USART2_RX"), DmaChannel(2, "USART3_RX")))


def _observed(*findings: RunFindingReading) -> Observation:
    return Observation(
        samples=(),
        exchanges=(),
        timings=(),
        elapsed_seconds=0.01,
        dma=CHANNELS,
        run_findings=findings,
    )


def test_a_read_the_guard_caught_fails_its_channel_only() -> None:
    read = RunFindingReading("DMA_READ_UNWRITTEN", "The firmware read it", dma_id=1)
    observed = _observed(read)

    caught = NotAccessedWhileRunning("USART2_RX").evaluate(observed)

    assert (caught.met, caught.observed) == (False, "The firmware read it")
    assert NotAccessedWhileRunning("USART3_RX").evaluate(observed).met


def test_an_overrun_and_a_too_long_transfer_fail_their_checks() -> None:
    observed = _observed(
        RunFindingReading("DMA_OVERRUN", "USART2_RX overran", dma_id=1),
        RunFindingReading("DMA_LENGTH", "USART3_RX moves 64 bytes", dma_id=2),
    )

    assert not NoOverrun("USART2_RX").evaluate(observed).met
    assert not LengthFits("USART3_RX").evaluate(observed).met
    assert LengthFits("USART2_RX").evaluate(observed).observed == "none found"


def test_a_channel_the_firmware_does_not_have_is_named() -> None:
    outcome = NoOverrun("SPI1_TX").evaluate(_observed())

    assert (outcome.met, outcome.observed) == (False, NO_SUCH_CHANNEL)
