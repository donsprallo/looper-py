"""A DBC file as the server read it: its CAN messages and their signals.

The server only reads the file; a bus block of the signal graph takes its
identifier, length and fields from one message. Reading is free.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DbcSignal:
    """One signal of a message, laid out as the DBC numbers its bits.

    Attributes:
        name: What the file calls it.
        start_bit: Where it begins: the least significant bit for Intel,
            the most significant for Motorola.
        length: Its width in bits.
        big_endian: Motorola order; otherwise Intel.
        is_signed: Whether its raw value is signed.
        scale: Physical = raw × scale + offset.
        offset: See ``scale``.
        unit: What it is measured in; empty for none.
        minimum: The least physical value the file allows, if it says.
        maximum: The greatest, if it says.
    """

    name: str
    start_bit: int
    length: int
    big_endian: bool = False
    is_signed: bool = False
    scale: float = 1.0
    offset: float = 0.0
    unit: str = ""
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class DbcMessage:
    """One CAN message of the file.

    Attributes:
        name: What the file calls it.
        identifier: Its CAN identifier.
        extended: A 29 bit identifier.
        length: Its length in bytes.
        cycle_us: How often it is sent, in microseconds; 0 when the file does not say.
        signals: Its signals, in the file's order.
    """

    name: str
    identifier: int
    extended: bool
    length: int
    cycle_us: int
    signals: tuple[DbcSignal, ...] = ()


@dataclass(frozen=True)
class DbcFile:
    """What the server made of a DBC file.

    Attributes:
        path: The file, on the server's disk.
        messages: Its CAN messages, in the file's order.
        problem: Why it could not be read, in the server's words; empty when it could.
    """

    path: str
    messages: tuple[DbcMessage, ...] = ()
    problem: str = ""

    def message(self, name: str) -> DbcMessage:
        """The message of a name.

        Raises:
            KeyError: If the file has no such message.
        """
        for message in self.messages:
            if message.name == name:
                return message
        raise KeyError(name)
