"""The two memories that survive a reset, as a test reaches them.

``simulation.retained()`` and ``simulation.flash()`` hand these out. A
tester lays data down where the firmware will find it -- a boot argument, a
configuration, a header broken on purpose -- reads back what the firmware
wrote, and saves and loads the whole flash to hold a state and come back to
it (F-RB4).
"""

from __future__ import annotations

from pathlib import Path

from looper.application.life_port import LifeInspector
from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import PartitionHeader


class Retained:
    """The retained memory: backup registers, a ``.noinit`` stand-in."""

    def __init__(self, inspector: LifeInspector) -> None:
        self._inspector = inspector

    def read(self, offset: int = 0, length: int = 0) -> bytes:
        """Bytes from an offset; length 0 reads to the end."""
        content = self._inspector.read_retained()
        return content[offset : offset + length] if length else content[offset:]

    def word(self, offset: int, width: int = 4) -> int:
        """One little endian word, as the firmware writes it."""
        return int.from_bytes(self.read(offset, width), "little")

    def write(self, offset: int, data: bytes) -> None:
        """Write bytes, as a change at the simulation's next point."""
        self._inspector.write_retained(offset, data)


class FlashPartition:
    """A named stretch of the flash, addressed from its own beginning."""

    def __init__(self, flash: Flash, name: str, offset: int, size: int) -> None:
        self._flash = flash
        self.name = name
        self.offset = offset
        self.size = size

    def read(self, offset: int = 0, length: int = 0) -> bytes:
        """Bytes from an offset within the partition; length 0 reads to its end."""
        return self._flash.read(self.offset + offset, length or self.size - offset)

    def write(self, offset: int, data: bytes, raw: bool = False) -> None:
        """Write bytes at an offset within the partition."""
        if offset + len(data) > self.size:
            raise SimulationRefusedError(f"{self.name} is {self.size} bytes long")
        self._flash.write(self.offset + offset, data, raw=raw)

    def erase(self) -> None:
        """Erase every sector of the partition."""
        self._flash.erase_partition(self.name)

    def write_image(self, image: str) -> None:
        """Erase the partition and write a built image into it: ``app@2.1`` (Pro).

        The server builds the variant first when it is not built yet.
        """
        self._flash.inspector.write_image(self.name, image)

    def write_image_file(self, path: Path | str) -> None:
        """Erase the partition and write an image file into it, whatever its header names (Pro).

        The server reads the file; a header that names no built image is
        what a jump into it then finds.
        """
        self._flash.inspector.write_image_file(self.name, str(Path(path).resolve()))

    def header(self) -> PartitionHeader:
        """What the partition holds, as the server reads its header (Pro)."""
        return self._flash.inspector.read_headers()[self.name]


class Flash:
    """The simulated flash: bits go 1 to 0, erasing is by sector."""

    def __init__(self, inspector: Inspector) -> None:
        self._inspector = inspector

    @property
    def inspector(self) -> Inspector:
        """The port the flash is reached through."""
        return self._inspector

    def headers(self) -> dict[str, PartitionHeader]:
        """What each partition holds, by name; without the licence no state (Pro)."""
        return self._inspector.read_headers()

    def read(self, offset: int = 0, length: int = 0) -> bytes:
        """Bytes from the flash's beginning; length 0 reads to its end."""
        return self._inspector.read_flash(offset, length)

    def write(self, offset: int, data: bytes, raw: bool = False) -> None:
        """Write bytes, by the flash's rules, or ``raw`` as they are."""
        self._inspector.write_flash(offset, data, raw)

    def partition(self, name: str) -> FlashPartition:
        """A partition by its name in looper.toml.

        Raises:
            SimulationRefusedError: If there is none of that name.
        """
        found = self._inspector.flash_partitions().get(name)
        if found is None:
            raise SimulationRefusedError(f"the flash has no partition called {name}")
        return FlashPartition(self, name, *found)

    def erase(self, sector: int | None = None) -> None:
        """Erase one sector, or with none the whole flash."""
        self._inspector.erase_flash(sector=sector)

    def erase_partition(self, name: str) -> None:
        """Erase a partition."""
        self._inspector.erase_flash(partition=name)

    def save(self) -> bytes:
        """The whole flash, to be loaded again."""
        return self._inspector.save_flash()

    def load(self, content: bytes) -> None:
        """Lay a saved flash down, but for its read-only partitions."""
        self._inspector.load_flash(content)

    def save_file(self, path: Path | str) -> Path:
        """Save the whole flash into a file."""
        target = Path(path)
        target.write_bytes(self.save())
        return target

    def load_file(self, path: Path | str) -> None:
        """Load a flash saved into a file."""
        self.load(Path(path).read_bytes())
