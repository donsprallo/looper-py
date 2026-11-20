"""A simulation on a bench: the bench it sees, joining and leaving one, and who sent a frame.

A mixin of `Simulation`, so that both files stay readable. Whether a bench
can be joined, who leads it and who sent or acknowledged a frame are the
server's to say; this only asks, waits for a join or a leave to go
through, and picks a bus's frames out of the recording.
"""

from __future__ import annotations

from looper.application.bench_joining import answering, settled_bench
from looper.application.event_stream import EventStream
from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model.bench import (
    BenchPhase,
    BenchState,
    JoinBusChoice,
    JoinCandidate,
    JoinCandidates,
)
from looper.domain.model.readings import Exchange

#: What `bus_records(sender=...)` takes for a frame of any other device of the bench.
ANY_PEER = "peer"
#: How long a join may take: both devices are built as libraries first.
JOIN_TIMEOUT_SECONDS = 600.0
#: How long a leave may take: both devices restart alone.
LEAVE_TIMEOUT_SECONDS = 120.0


class BenchMembership:
    """The bench of one simulation, and the senders of its frames."""

    _inspector: Inspector
    _events: EventStream

    def bench_state(self) -> BenchState:
        """The bench as this simulation's server sees it.

        ``state.device("gateway").state_text`` is ``held`` or ``runs``,
        ``state.marks`` the other devices' resets.

        Raises:
            ProFeatureLockedError: In the free download; the message is its sentence.
            SimulationRefusedError: If the server answers no bench here.
        """
        return self._inspector.read_bench()

    def join_candidates(self, bus: str) -> JoinCandidates:
        """The other servers on this PC this simulation's `bus` could be joined with.

        Raises:
            ProFeatureLockedError: In the free download.
            SimulationRefusedError: If there is no such bus, or no bench here.
        """
        return self._inspector.read_join_candidates(self._bus_id(bus))

    def join_bus(
        self,
        bus: str,
        peer: JoinCandidate,
        peer_bus: str | None = None,
        timeout_s: float = JOIN_TIMEOUT_SECONDS,
    ) -> BenchState:
        """Join `bus` with a bus of another server, and wait until both are on one bench.

        The server builds both devices as libraries and restarts both into
        one bench host, this one leading; both connections drop and come
        back. The other server's bus is `peer_bus` by its label, else the
        one the server preselected.

        Raises:
            SimulationRefusedError: If the join cannot be carried out or did
                not go through; the message is the server's sentence.
            TimeoutError: If the bench did not form in time.
        """
        choice = _chosen_bus(peer, peer_bus)
        answered = self._inspector.join_bus(self._bus_id(bus), peer.instance_id, choice.bus_id)
        state = settled_bench(self._inspector, answered, BenchPhase.ON_BENCH, timeout_s)
        answering(self._inspector, timeout_s)
        return state

    def leave_bench(self, timeout_s: float = LEAVE_TIMEOUT_SECONDS) -> BenchState:
        """Leave the bench, and wait until this device runs alone again.

        Raises:
            SimulationRefusedError: If this server is on no bench, or the
                leave did not go through.
            TimeoutError: If the device did not come back alone in time.
        """
        answered = self._inspector.leave_bench()
        state = settled_bench(self._inspector, answered, BenchPhase.ALONE, timeout_s)
        answering(self._inspector, timeout_s)
        return state

    def wait_for_bench(
        self, phase: BenchPhase = BenchPhase.ON_BENCH, timeout_s: float = JOIN_TIMEOUT_SECONDS
    ) -> BenchState:
        """Wait until this simulation's server stands at `phase` and its device answers again.

        For the other device of a join or a leave: its server restarts too,
        and its connection drops and comes back, so a test waits on it as
        well before it goes on with that device.

        Raises:
            SimulationRefusedError: If the server gave up; the message is its sentence.
            TimeoutError: If it did not get there in time.
        """
        state = settled_bench(self._inspector, BenchState(), phase, timeout_s)
        answering(self._inspector, timeout_s)
        return state

    def bus_records(
        self, bus: str | None = None, *, sender: str | None = None, since: int = 0
    ) -> tuple[Exchange, ...]:
        """The recorded frames, oldest first: of `bus` if named, from `sender` if named.

        On a bench a frame another device sent names it in `sender_device`;
        `sender` picks those of one device, ``"peer"`` those of any other
        device. Reads the recording from event `since` until it reached the
        time the clock stands at now: right after `advance` a server, on a
        bench each one from its own device, may still be taking the last
        frames in.

        Raises:
            SimulationRefusedError: If there is no such bus.
        """
        bus_id = self._bus_id(bus) if bus is not None else None
        now_us = self._inspector.run_state().now_us
        return tuple(
            exchange
            for exchange in self._events.exchanges_until(since, now_us)
            if (bus_id is None or exchange.bus_id == bus_id) and _sent_by(exchange, sender)
        )

    def _bus_id(self, name: str) -> int:
        """The id of the bus the firmware calls `name`."""
        buses = self._inspector.read_buses()
        for bus in buses:
            if bus.name == name:
                return bus.bus_id
        known = ", ".join(sorted(bus.name for bus in buses)) or "none at all"
        raise SimulationRefusedError(
            f"the firmware registered no bus named {name!r}; it has {known}"
        )


def _sent_by(exchange: Exchange, sender: str | None) -> bool:
    """Whether a frame is one of `sender`'s: any for None, another device's for ``peer``."""
    if sender is None:
        return True
    if sender == ANY_PEER:
        return exchange.from_peer
    return exchange.sender_device == sender


def _chosen_bus(peer: JoinCandidate, label: str | None) -> JoinBusChoice:
    """The other server's bus to join: the one of that label, else the preselected one."""
    if label is not None:
        for choice in peer.buses:
            if choice.label == label:
                return choice
    chosen = peer.preselected_bus if label is None else None
    if chosen is None:
        offered = ", ".join(choice.label for choice in peer.buses) or "none"
        reason = peer.reason_text or f"it offers {offered}"
        raise SimulationRefusedError(f"{peer.firmware_name} has no bus to join here: {reason}")
    return chosen
