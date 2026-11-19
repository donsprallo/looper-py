"""The builder steps of a signal graph that limit a signal: Limit and Slew rate.

`SignalGraph` takes these steps on, as it takes the operations. A limit's
``low`` and ``high`` are each a number or a node to read it from, the way
a comparator's threshold is; looper-srv's pytest export writes them so
(``.limit('clamp', 'sine', low=0.0, high='ref')``). Whether a rate is
above zero, or a linked node exists, is the server's to say.
"""

from __future__ import annotations

from typing import Self, TypeIs

from looper.domain.model.signal_operations import NodeBuilding
from looper.domain.model.signal_parts import (
    InputSpec,
    LimitSettings,
    NodeOutput,
    SignalNode,
    SignalNodeKind,
    SlewSettings,
    outputs_of,
)

#: A limit as a test gives it: a number, or the node whose output it is.
LimitSpec = float | InputSpec


class LimitBuilding(NodeBuilding):
    """Builder steps for limits and slew rates."""

    def limit(
        self, key: str, reads: InputSpec, low: LimitSpec, high: LimitSpec, group: str = ""
    ) -> Self:
        """Add a limit: `reads` held between `low` and `high`, ``min(max(in, low), high)``.

        A limit given as a key or a `NodeOutput` is linked: it follows that
        node, ``high="ref"``. A low limit above the high one is no refusal;
        the limit gives the low one, and its `GraphNodeState.fault_text`
        says why.
        """
        settings = LimitSettings(
            low=_number(low),
            high=_number(high),
            low_linked=_is_linked(low),
            high_linked=_is_linked(high),
        )
        linked = [side for side in (low, high) if _is_linked(side)]
        reading = outputs_of((reads, *linked))
        node = SignalNode(key, SignalNodeKind.LIMIT, inputs=reading, limit=settings, group=group)
        return self._with(node)

    def slew_rate(
        self, key: str, reads: InputSpec, rise: float, fall: float = 0.0, group: str = ""
    ) -> Self:
        """Add a slew rate: it follows `reads`, never faster than `rise` up and `fall` down.

        Both are in units of the input per second; a `fall` of 0 falls as
        fast as it rises. A comparator behind it plans its edges to the
        microsecond: a step of D is crossed D / rise after it.
        """
        settings = SlewSettings(rise=rise, fall=fall)
        node = SignalNode(
            key, SignalNodeKind.SLEW_RATE, inputs=outputs_of((reads,)), slew=settings, group=group
        )
        return self._with(node)


def _is_linked(side: LimitSpec) -> TypeIs[InputSpec]:
    """A limit named by a node, not given as a number."""
    return isinstance(side, str | NodeOutput)


def _number(side: LimitSpec) -> float:
    """The limit as a number; 0 where it is linked, as the contract leaves it unused."""
    if _is_linked(side):
        return 0.0
    return float(side)
