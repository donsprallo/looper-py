"""What the stream says happened to the firmware as a whole: resets and flash operations.

The words are the server's -- causes such as ``watchdog``, operations such
as ``violation`` -- so a test reads like the window does.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResetMark:
    """A reset, at a simulated time.

    Attributes:
        sim_us: When.
        cause: ``power-on``, ``software``, ``watchdog``, ``pin`` or ``brown-out``.
        life: The life that ended.
    """

    sim_us: int
    cause: str
    life: int


@dataclass(frozen=True)
class FlashMark:
    """A flash operation, at a simulated time.

    Attributes:
        sim_us: When.
        kind: ``write``, ``erase``, ``violation`` or ``cut``.
        offset: Where, from the flash's beginning.
        length: How many bytes.
        partition: The partition it lies in, or empty.
        by_client: Whether a client did it rather than the firmware.
    """

    sim_us: int
    kind: str
    offset: int
    length: int
    partition: str = ""
    by_client: bool = False
