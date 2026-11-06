"""What the port answers about the firmware's lives and the memories that survive them.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it, and a test double answers it from a script like the rest.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model import LifeDump, Lives


class LifeInspector(ABC):
    """Resets, lives, the retained memory and the flash."""

    @abstractmethod
    def reset_firmware(self, cause: str) -> None:
        """Reset the firmware from outside: ``pin``, ``power-on`` or ``brown-out``.

        Raises:
            ValueError: If the word is no cause of a reset at all.
            SimulationRefusedError: If the server refuses the cause, as it
                does ``software`` and ``watchdog``.
        """

    @abstractmethod
    def read_lives(self) -> Lives:
        """Every life of the run."""

    @abstractmethod
    def read_life_dump(self, life: int) -> LifeDump:
        """What a life that ended left behind.

        Raises:
            SimulationRefusedError: If there is no such life, or it is not kept.
        """

    @abstractmethod
    def read_retained(self) -> bytes:
        """The whole retained memory; empty when there is none."""

    @abstractmethod
    def write_retained(self, offset: int, data: bytes) -> None:
        """Write bytes into the retained memory."""

    @abstractmethod
    def read_flash(self, offset: int, length: int) -> bytes:
        """Bytes of the flash from its beginning."""

    @abstractmethod
    def flash_partitions(self) -> dict[str, tuple[int, int]]:
        """Every partition of the flash: its offset and size, by name."""

    @abstractmethod
    def write_flash(self, offset: int, data: bytes, raw: bool) -> None:
        """Write bytes into the flash, by its rules or past them."""

    @abstractmethod
    def erase_flash(self, partition: str = "", sector: int | None = None) -> None:
        """Erase a partition, a sector, or with neither the whole flash."""

    @abstractmethod
    def save_flash(self) -> bytes:
        """The whole flash."""

    @abstractmethod
    def load_flash(self, content: bytes) -> None:
        """Lay a saved flash down, but for its read-only partitions."""
