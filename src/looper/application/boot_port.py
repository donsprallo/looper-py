"""What the port answers about the bootloader: images, headers, chains, the power, the OTP (Pro).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. Whether the licence allows a call is the server's to say: a
locked part comes back as `ProFeatureLockedError`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model import BootChain, Image, PartitionHeader


class BootInspector(ABC):
    """Images and the headers of the flash's partitions."""

    @abstractmethod
    def read_images(self) -> tuple[Image, ...]:
        """Every image of the project in every variant.

        Raises:
            ProFeatureLockedError: Without a licence for the bootloader.
        """

    @abstractmethod
    def read_headers(self) -> dict[str, PartitionHeader]:
        """What each partition holds, by name; without the licence no state."""

    @abstractmethod
    def write_image(self, partition: str, image: str) -> None:
        """Erase a partition and write a built image into it, ``app@2.1``.

        The server builds the variant first when it is not built yet.

        Raises:
            ProFeatureLockedError: Without a licence for the bootloader.
            SimulationRefusedError: If there is no such image or partition.
        """

    @abstractmethod
    def write_image_file(self, partition: str, path: str) -> None:
        """Erase a partition and write an image file, whatever its header names.

        The path is the server's: it reads the file.
        """

    @abstractmethod
    def read_boot_chains(self) -> tuple[BootChain, ...]:
        """The run's lives as boot chains, oldest first."""

    @abstractmethod
    def cut_power(
        self, after_bytes: int | None, during: str, off_for_us: int, seed: int, disarm: bool = False
    ) -> None:
        """Arm a power cut after so many bytes of the firmware's flash calls, or cut it now.

        Args:
            after_bytes: Bytes programmed or erased from now; ``None`` cuts at once.
            during: ``flash.write``, ``flash.erase`` or ``any``.
            off_for_us: How long the board stays without power.
            seed: Which bits of the word in flight change.
            disarm: Take an armed cut back instead.

        Raises:
            ValueError: If ``during`` is none of the three; nothing is sent.
        """

    @abstractmethod
    def read_otp(self) -> bytes:
        """The whole OTP; empty when there is none."""

    @abstractmethod
    def burn_otp(self, offset: int, data: bytes) -> None:
        """Burn the bits that are 1 in the data; nothing takes a burned bit back."""
