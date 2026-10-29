"""The firmware's own variables, as a simulation can reach them.

Reading the debug information is the server's work; what arrives here is
the catalogue entry and the sampled value, nothing to decode further.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    """One global of the firmware, as the catalogue lists it.

    Attributes:
        variable_id: Identifies it in this server's catalogue. Paths are
            not unique: two translation units may declare a static of one name.
        path: Where it lives, such as ``config.gain[2]``.
        name: Its last step.
        encoding: How its bytes read, such as ``uint``.
        byte_width: How many bytes it occupies.
        runtime_address: Where it lives in the running simulation.
        is_writable: Whether a value may be stored in it.
        bit_offset: Where a bit field begins, zero otherwise.
        bit_width: How wide a bit field is, zero otherwise.
        display_type: Encoding and width, such as ``uint 4 B``.
        display_address: The link time address in hexadecimal.
    """

    variable_id: int
    path: str
    name: str
    encoding: str
    byte_width: int
    runtime_address: int
    is_writable: bool
    bit_offset: int = 0
    bit_width: int = 0
    display_type: str = ""
    display_address: str = ""


@dataclass(frozen=True)
class Watch:
    """One variable that is being sampled.

    Attributes:
        channel_id: The number the watch is known by; it is what writing
            and removing take, not the variable's own id.
        path: Where the variable lives.
        name: Its last step.
        encoding: How its bytes read.
        byte_width: How many bytes it occupies.
        runtime_address: Where it lives in the running simulation.
        is_writable: Whether a value may be stored in it.
        value: The value now.
        bit_offset: Where a bit field begins, zero otherwise.
        bit_width: How wide a bit field is, zero otherwise.
        display_value: The value written the way its own type reads.
        range_text: What the variable can hold, such as ``uint8, 0 to 255``.
    """

    channel_id: int
    path: str
    name: str
    encoding: str
    byte_width: int
    runtime_address: int
    is_writable: bool
    value: float
    bit_offset: int = 0
    bit_width: int = 0
    display_value: str = ""
    range_text: str = ""
