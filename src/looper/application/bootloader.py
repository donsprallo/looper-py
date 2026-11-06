"""The bootloader's parts as a test reaches them: the OTP, and power cuts in turn (Pro).

``simulation.otp()`` hands out the OTP. ``sweep_power_cuts`` is the
systematic power cut (``reset-and-bootloader.md`` 3.5): the flash is saved
once, and for every point in turn it is laid down again, the firmware reset,
the cut armed after that many bytes, and the scenario run -- the test checks
after each. It needs nothing new of the server; a scenario that is
deterministic cuts the same word with the same bits every time.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from looper.application.boot_port import BootInspector

if TYPE_CHECKING:
    from looper.application.simulation import Simulation


class Otp:
    """The one-time-programmable memory: anti-rollback counters, key hashes."""

    def __init__(self, inspector: BootInspector) -> None:
        self._inspector = inspector

    def read(self, offset: int = 0, length: int = 0) -> bytes:
        """Bytes from an offset; length 0 reads to the end."""
        content = self._inspector.read_otp()
        return content[offset : offset + length] if length else content[offset:]

    def burn(self, offset: int, data: bytes) -> None:
        """Burn the bits that are 1 in the data, for good, as a change at the next point."""
        self._inspector.burn_otp(offset, data)


def sweep_power_cuts(
    simulation: Simulation,
    scenario: Callable[[Simulation], None],
    total_bytes: int,
    every: int = 4096,
    during: str = "flash.write",
) -> Iterator[int]:
    """Run a scenario once for every point a power cut can come at, every so many bytes.

    Yields the number of bytes after which the power went, once the scenario
    ran for it, so that the test checks the outcome before the next point.
    The flash is laid down as it was before the first run each time, and
    the firmware reset with a power-on before the cut is armed.

    Args:
        simulation: The simulation to cut the power of.
        scenario: What the firmware is made to do: start an update, say.
        total_bytes: How many bytes the scenario programs at most.
        every: The step between two points; a sector is a good one.
        during: ``flash.write``, ``flash.erase`` or ``any``.
    """
    if every <= 0:
        raise ValueError("power cuts come every one byte or more")
    flash = simulation.flash()
    saved = flash.save()
    for after in range(0, total_bytes, every):
        flash.load(saved)
        simulation.reset("power-on")
        simulation.power_cut(after_bytes=after, during=during)
        scenario(simulation)
        yield after
