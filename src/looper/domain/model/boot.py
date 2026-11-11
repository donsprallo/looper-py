"""The bootloader's parts as a test reads them: images, partition headers, boot chains (Pro).

These are the server's words. Whether a header is valid, which image it
names, which way a boot went -- the server decides and says it; a test
only compares.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Image:
    """One image of the project in one variant.

    Attributes:
        ref: ``app@2.1``, as ``write_image`` takes it.
        built: Whether it is built.
        version_text: ``0x0201``.
        payload_size: Bytes of its payload, its size on the target.
        identity_hex: Its identity, once built.
        text: The server's line for it.
    """

    ref: str
    built: bool = False
    version_text: str = ""
    payload_size: int = 0
    identity_hex: str = ""
    text: str = ""


@dataclass(frozen=True)
class PartitionHeader:
    """What a partition holds, as the server reads its header.

    Attributes:
        name: The partition.
        state: ``valid``, ``empty``, ``broken``, ``unknown image``, ``no
            header`` for data (or a magic cut in its first word), or empty
            without the licence.
        text: The server's sentence: ``valid · app@2.1 · v0x0201``.
    """

    name: str
    state: str = ""
    text: str = ""


@dataclass(frozen=True)
class BootStep:
    """One life of a boot chain: one image, from one partition."""

    life: int
    image: str = ""
    partition: str = ""
    at_us: int = 0
    text: str = ""


@dataclass(frozen=True)
class BootChain:
    """The lives between two resets: the way one start of the board went.

    Attributes:
        steps: The lives, in order.
        started_by: What reset the board before the first: ``power-on``, ``pin``, ...
        text: ``stage0 → stage1_a 1.0 → app_b 2.1``.
    """

    steps: tuple[BootStep, ...] = ()
    started_by: str = ""
    text: str = ""

    @property
    def partitions(self) -> tuple[str, ...]:
        """The partitions it went through, as ``went`` names them."""
        return tuple(step.partition for step in self.steps)
