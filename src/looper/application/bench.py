"""What a test does with a bench: its devices, one clock for all, and the bench's state.

Each device of a bench keeps a server of its own, and each is a `Simulation`
here. Run control from any one of them acts on the whole bench -- the bench
host lets every device run to the furthest time any client waits for, and
the other servers follow a hold within a quarter of a second -- so the bench
moves its clock through the leader and waits, where it matters, until every
device says it followed.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from types import TracebackType

from looper.application.simulation import Simulation
from looper.domain.model import ClockMode
from looper.domain.model.bench import BenchState

#: How long the other servers take at most to follow an order: they look five times a second.
FOLLOW_TIMEOUT_SECONDS = 5.0
#: How long to wait between two looks at a device that has not followed yet.
FOLLOW_POLL_SECONDS = 0.05


class Bench:
    """A running bench of devices with joined buses, as a test sees it.

    Use it as a context manager, or call `close` when done: closing lets go
    of every connection and, for a bench started for the test, stops the
    leader's server, which ends the other servers and the bench host.
    """

    def __init__(
        self,
        members: Mapping[str, Simulation],
        leader: str,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        """A bench of `members` by their names on it, `leader` among them."""
        if leader not in members:
            raise ValueError(f"the leader {leader!r} is no member of {sorted(members)}")
        self._members = dict(members)
        self._leader = leader
        self._on_close = on_close
        self._closed = False

    @property
    def member_names(self) -> tuple[str, ...]:
        """The devices' names, the leader first."""
        return (self._leader, *(name for name in self._members if name != self._leader))

    @property
    def leader(self) -> Simulation:
        """The device that leads the bench."""
        return self._members[self._leader]

    def member(self, name: str) -> Simulation:
        """The device called `name` on the bench, through its own server.

        Raises:
            KeyError: If no member is called so; the message names those there are.
        """
        if name not in self._members:
            raise KeyError(f"no member {name!r} on the bench; it has {list(self.member_names)}")
        return self._members[name]

    def state(self) -> BenchState:
        """The bench as the leader's server sees it: its devices, joined buses and marks.

        Raises:
            ProFeatureLockedError: In the free download.
        """
        return self.leader.bench_state()

    def advance(self, seconds: float) -> None:
        """Run the held bench for a span of simulated time; every device gets there.

        Raises:
            SimulationRefusedError: If the clock is not held.
        """
        self.leader.advance(seconds)

    def advance_microseconds(self, microseconds: int) -> None:
        """`advance`, for a span given in whole simulated microseconds."""
        self.leader.advance_microseconds(microseconds)

    def hold(self) -> None:
        """Hold the whole bench, and return once every device's clock is held.

        Raises:
            SimulationRefusedError: If the server declines.
            TimeoutError: If a device did not follow in time.
        """
        self.leader.hold()
        self._followed(ClockMode.HELD)

    def pace(self, ratio: float = 1.0) -> None:
        """Let the whole bench run by itself at `ratio` times real time.

        Raises:
            ValueError: For a ratio of zero or less.
            SimulationRefusedError: If the server declines the pace.
            TimeoutError: If a device did not follow in time.
        """
        self.leader.pace(ratio)
        self._followed(ClockMode.PACED)

    def _followed(self, mode: ClockMode) -> None:
        """Wait until every device's clock goes as `mode`."""
        deadline = time.monotonic() + FOLLOW_TIMEOUT_SECONDS
        for name, simulation in self._members.items():
            while simulation.clock_mode != mode:
                if time.monotonic() > deadline:
                    raise TimeoutError(f"{name} did not follow the bench to {mode.value}")
                time.sleep(FOLLOW_POLL_SECONDS)

    def close(self) -> None:
        """Let go of every device and stop a bench that was started for the test."""
        if self._closed:
            return
        self._closed = True
        for simulation in self._members.values():
            simulation.close()
        if self._on_close is not None:
            self._on_close()

    def __enter__(self) -> Bench:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
