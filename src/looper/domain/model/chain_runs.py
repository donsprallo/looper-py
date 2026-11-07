"""How a chain's Sequence is getting on, and what came of running until it ended."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class SequenceProgress(IntEnum):
    """Where a Sequence stands; the contract's numbers."""

    WAITING = 0
    RUNNING = 1
    DONE = 2
    FAILED = 3


@dataclass(frozen=True)
class SequenceState:
    """One Sequence, in the server's words.

    Attributes:
        key: The Sequence block's key.
        group: The key of its group.
        group_name: The name of its group, which is the chain's name.
        progress: Waiting, running, done or failed.
        step: The step it is at, from 1; 0 before the start.
        step_count: How many steps it has.
        step_text: ``▸ step 3 of 6``, ``✓ done · 6 steps``.
        failure_text: Why it failed and when; empty unless it did.
    """

    key: str
    group: str
    group_name: str
    progress: SequenceProgress
    step: int = 0
    step_count: int = 0
    step_text: str = ""
    failure_text: str = ""

    @property
    def ended(self) -> bool:
        """Whether it is done or failed."""
        return self.progress in (SequenceProgress.DONE, SequenceProgress.FAILED)


@dataclass(frozen=True)
class ChainRun:
    """What came of running a chain until its Sequence ended, or until the time was up.

    Attributes:
        chain: The chain's name.
        passed: Its Sequence came to the end of its steps.
        failure_text: Why it did not, in the server's words; or that time ran out.
        sequence: The last state read; None if the chain has no Sequence.
    """

    chain: str
    passed: bool
    failure_text: str = ""
    sequence: SequenceState | None = None

    def __bool__(self) -> bool:
        """True when it passed, so that ``assert run`` reads naturally."""
        return self.passed


@dataclass(frozen=True)
class ChainExport:
    """A chain written by the server as a pytest against this library (looper Pro).

    Attributes:
        file_name: The name the server gives the file, such as ``test_boost_test.py``.
        text: The file's text.
        warnings: What the file could not carry over, one sentence each.
    """

    file_name: str
    text: str
    warnings: tuple[str, ...] = ()
