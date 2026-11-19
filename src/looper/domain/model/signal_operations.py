"""The builder steps of a signal graph that combine nodes: operations, comparators, selects.

`SignalGraph` takes these steps on; each returns a new graph with one more
node. Every step takes ``group=``, the key of the group the block is in.
How many inputs an operation may take at most, and whether a sign fits its
kind, is the server's to say; here only the shape of the call is checked.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from typing import Self

from looper.domain.model.signal_parts import (
    MANY_INPUT_OPERATIONS,
    ONE_INPUT_OPERATIONS,
    OPERATIONS,
    TWO_INPUT_OPERATIONS,
    CompareSettings,
    InputSpec,
    SampleMode,
    SampleSettings,
    SignalNode,
    SignalNodeKind,
    outputs_of,
)

#: The signs a sum's input may have.
SIGNS = (1, -1)


class NodeBuilding:
    """The one way a builder step adds a node."""

    nodes: tuple[SignalNode, ...]

    def _with(self, node: SignalNode) -> Self:
        return replace(self, nodes=(*self.nodes, node))  # type: ignore[type-var]


class OperationBuilding(NodeBuilding):
    """Builder steps for operations, sums, comparators, selects and sample and hold nodes."""

    def operation(
        self,
        key: str,
        kind: SignalNodeKind,
        *inputs: InputSpec,
        negated: Iterable[bool] = (),
        group: str = "",
    ) -> Self:
        """Add a node that combines others, or takes the size of one.

        ``ADD``, ``MULTIPLY``, ``MIN``, ``MAX`` and ``SUM`` read two inputs
        or more, up to the server's 8; ``SUBTRACT`` and ``DIVIDE`` read two
        and ``ABS`` one. A ``SUM`` subtracts the inputs `negated` marks, one
        sign per input, as the server's export writes it
        (``negated=(False, True)``); `sum` takes the signs beside the inputs.

        Raises:
            ValueError: If `kind` is no operation, or the number of inputs does not fit it.
        """
        _check_operands(kind, len(inputs))
        node = SignalNode(
            key, kind, inputs=outputs_of(inputs), negated_inputs=tuple(negated), group=group
        )
        return self._with(node)

    def sum(self, key: str, *signed: tuple[InputSpec, int], group: str = "") -> Self:
        """Add a sum: each input added or subtracted by its sign, ``("a", +1), ("b", -1)``.

        Raises:
            ValueError: If a sign is neither +1 nor -1, or fewer than two inputs are given.
        """
        for read, sign in signed:
            if sign not in SIGNS:
                raise ValueError(f"the sign of {read!r} is {sign}; a sum takes +1 or -1")
        reads = [read for read, _ in signed]
        negated = [sign < 0 for _, sign in signed]
        return self.operation(key, SignalNodeKind.SUM, *reads, negated=negated, group=group)

    def compare(  # noqa: PLR0913 -- the export writes every setting by name
        self,
        key: str,
        reads: InputSpec,
        level: float = 0.0,
        hysteresis: float = 0.0,
        below: bool = False,
        threshold: InputSpec | None = None,
        check_us: int = 0,
        group: str = "",
    ) -> Self:
        """Add a comparator: one while `reads` is above the threshold (or `below` it), else zero.

        It goes back only when the input has gone `hysteresis` past the
        threshold the other way. `threshold` names a node to compare with
        instead of the constant `level`. Its edges are planned to the
        microsecond where the runtime can; where it cannot -- noise or a
        divide upstream -- it is checked every `check_us` (0: the server's
        Auto). A negative hysteresis is the server's to refuse.
        """
        settings = CompareSettings(level, hysteresis, below, threshold is not None, check_us)
        reading = (reads,) if threshold is None else (reads, threshold)
        node = SignalNode(
            key, SignalNodeKind.COMPARE, inputs=outputs_of(reading), compare=settings, group=group
        )
        return self._with(node)

    def select(
        self, key: str, select: InputSpec, when_1: InputSpec, when_0: InputSpec, group: str = ""
    ) -> Self:
        """Add a select: `when_1` while `select` gives 0.5 or more, else `when_0`.

        It switches at the microsecond `select` crosses 0.5, without hysteresis.
        """
        reading = outputs_of((select, when_1, when_0))
        return self._with(SignalNode(key, SignalNodeKind.SELECT, inputs=reading, group=group))

    def sample_hold(  # noqa: PLR0913 -- the export writes every setting by name
        self,
        key: str,
        reads: InputSpec,
        trigger: InputSpec,
        mode: SampleMode = SampleMode.RISING,
        initial: float = 0.0,
        group: str = "",
    ) -> Self:
        """Add a sample and hold node: `reads` as it was when `trigger` rose (or fell).

        With ``SampleMode.TRACK`` it follows `reads` while the trigger is
        high and holds it from the falling edge on. It gives `initial` until
        its first sample.
        """
        settings = SampleSettings(SampleMode(mode), initial)
        reading = outputs_of((reads, trigger))
        node = SignalNode(
            key, SignalNodeKind.SAMPLE_HOLD, inputs=reading, sample=settings, group=group
        )
        return self._with(node)


def _check_operands(kind: SignalNodeKind, count: int) -> None:
    """Refuse a call whose inputs cannot fit the operation, whatever the server allows."""
    if kind in ONE_INPUT_OPERATIONS and count != 1:
        raise ValueError(f"{kind} reads one input; give it exactly one")
    if kind in TWO_INPUT_OPERATIONS and count != 2:  # noqa: PLR2004 -- the two of a subtract
        raise ValueError(f"{kind} reads two inputs; give it exactly two")
    if kind in MANY_INPUT_OPERATIONS and count < 2:  # noqa: PLR2004 -- an operation of one
        raise ValueError(f"{kind} reads two inputs or more; name the second")
    if kind not in OPERATIONS | ONE_INPUT_OPERATIONS:
        known = sorted(OPERATIONS | ONE_INPUT_OPERATIONS)
        raise ValueError(f"{kind} is not an operation; use one of {known}")
