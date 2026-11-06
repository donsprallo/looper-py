"""The things one can expect of a bootloader: what a partition holds, which way a boot went (Pro).

The server reads the headers and puts the lives into chains; a check only
compares what it says with what the test expects. Without the licence the
server says no header state, and a check of one is not met -- with the
reason in what it saw.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome

#: What a header state is when the server gives none.
NO_STATE = "no header state (data, or looper Pro is not licensed)"


@dataclass(frozen=True)
class PartitionHolds(Check):
    """A partition's header is in a state, and names an image when one is given.

    Attributes:
        partition: The partition.
        states: The header states that meet it: ``valid``, ``broken``, ...
        image: The image a valid header has to name, ``app@2.1``; empty for any.
    """

    partition: str
    states: tuple[str, ...]
    image: str = ""

    def evaluate(self, observed: Observation) -> Outcome:
        """Look at the partition's header at the window's end."""
        header = observed.headers.get(self.partition)
        expected = " or ".join(self.states) + (f" · {self.image}" if self.image else "")
        subject = f"the header of {self.partition}"
        if header is None:
            return Outcome(subject, expected, "no such partition", met=False)
        seen = header.text or NO_STATE
        named = not self.image or f"· {self.image} ·" in f"{header.text} "
        return Outcome(subject, expected, seen, met=header.state in self.states and named)
