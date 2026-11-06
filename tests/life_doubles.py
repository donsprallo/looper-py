"""The lives part of the scripted inspector: resets, lives, retained memory and flash.

The memories are byte arrays a test reads and writes; lives are a script.
"""

from __future__ import annotations

from looper.application.ports import SimulationRefusedError
from looper.domain.model import Life, LifeDump, Lives

FLASH_SIZE = 4096


class ScriptedLives:
    """Answers the life questions from fixed state, and writes down the requests."""

    def __init__(self) -> None:
        self.reset_causes: list[str] = []
        self.lives = Lives(lives=(Life(number=1, started_at_us=0),))
        self.dumps: dict[int, LifeDump] = {}
        self.retained = bytearray(32)
        self.flash = bytearray(b"\xff" * FLASH_SIZE)
        self.partitions: dict[str, tuple[int, int]] = {"config": (1024, 1024)}
        self.flash_writes: list[tuple[int, bytes, bool]] = []
        self.erased: list[tuple[str, int | None]] = []

    def reset_firmware(self, cause: str) -> None:
        if cause not in ("pin", "power-on"):
            raise SimulationRefusedError("a reset from outside is a pin reset or a power-on")
        self.reset_causes.append(cause)

    def read_lives(self) -> Lives:
        return self.lives

    def read_life_dump(self, life: int) -> LifeDump:
        if life not in self.dumps:
            raise SimulationRefusedError(f"Life {life} is no longer kept.")
        return self.dumps[life]

    def read_retained(self) -> bytes:
        return bytes(self.retained)

    def write_retained(self, offset: int, data: bytes) -> None:
        self.retained[offset : offset + len(data)] = data

    def read_flash(self, offset: int, length: int) -> bytes:
        return bytes(self.flash[offset : offset + (length or FLASH_SIZE)])

    def flash_partitions(self) -> dict[str, tuple[int, int]]:
        return self.partitions

    def write_flash(self, offset: int, data: bytes, raw: bool) -> None:
        self.flash_writes.append((offset, data, raw))
        self.flash[offset : offset + len(data)] = data

    def erase_flash(self, partition: str = "", sector: int | None = None) -> None:
        self.erased.append((partition, sector))

    def save_flash(self) -> bytes:
        return bytes(self.flash)

    def load_flash(self, content: bytes) -> None:
        self.flash[:] = content
