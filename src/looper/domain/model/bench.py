"""A bench: devices on this PC whose CAN buses are joined, on one clock (Pro).

Each device keeps its own server; the bench host runs them in lockstep and
plays the bus between them. What a bench is, who leads it and what each
device is doing are the server's to say, so every text here is the
server's; this only keeps them in the shape a test reads. Times are
simulated microseconds.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BenchPhase(StrEnum):
    """Where a server stands with a bench."""

    #: On no bench.
    ALONE = "alone"
    #: Building both devices, then restarting them together.
    JOINING = "joining"
    ON_BENCH = "on_bench"
    #: Restarting alone.
    LEAVING = "leaving"


@dataclass(frozen=True)
class BenchDevice:
    """One device of a bench, as the answering server sees it.

    Attributes:
        name: Its name on the bench, ``gateway``.
        mcu: ``STM32G474``; empty when its project names none.
        where_text: ``own window`` for another device whose server has a
            window attached, ``this PC`` otherwise; decide by `windows`, not
            by this text.
        state_text: ``runs``, ``held``, ``held · at a breakpoint``,
            ``stopped · HardFault``, ``reset · life 2``, ``not answering``.
        now_us: Its simulated time; every device of a bench stands at the
            same moment.
        now_text: The same, ``4.214 s``.
        leader: Whether it leads the bench.
        this_device: Whether it is the device of the server that answered.
        address: Where its server listens; empty while unknown.
        index: Its index on the bench, the ``source_id`` of its frames.
        fault: Whether it stopped or does not answer.
        hover_text: The device in one line with its bus and frames.
        windows: How many windows are attached to that device's server now;
            for this device, those attached to the answering server.
    """

    name: str
    mcu: str = ""
    where_text: str = ""
    state_text: str = ""
    now_us: int = 0
    now_text: str = ""
    leader: bool = False
    this_device: bool = False
    address: str = ""
    index: int = 0
    fault: bool = False
    hover_text: str = ""
    windows: int = 0


@dataclass(frozen=True)
class JoinedBus:
    """One of this device's buses, joined with other devices' on the bench.

    Attributes:
        bus_id: This device's bus.
        label: ``CAN1``.
        join: The join's name in the bench file.
        peers_text: The other ends, ``gateway · CAN1``.
        bitrate: Bits per second.
        frames: Every frame this device recorded on it, its own and the others'.
        text: ``CAN1 ⇄ gateway · CAN1 · 500 kbit/s · 1 240 frames``.
    """

    bus_id: int
    label: str
    join: str = ""
    peers_text: str = ""
    bitrate: int = 0
    frames: int = 0
    text: str = ""


@dataclass(frozen=True)
class BenchMark:
    """Another device's reset, at its simulated time.

    Attributes:
        sim_us: When its new life began.
        device: The device that reset.
        life: The life that began.
        text: ``gateway reset · watchdog · life 2``.
    """

    sim_us: int
    device: str
    life: int
    text: str = ""


@dataclass(frozen=True)
class BenchState:
    """The bench as one server sees it.

    Attributes:
        revision: Starts at 1, one more whenever a device comes or goes,
            changes its state, or the phase changes.
        revision_text: What changed last, in the server's words.
        phase: Where this server stands with a bench.
        name: The bench's name; empty when alone.
        title: ``BENCH · one clock · thermostat leads``.
        devices: Every device, the leader first.
        buses: This device's joined buses.
        waiting_for_text: ``waiting for gateway`` while the bench waits for
            another device; empty otherwise.
        waiting_share_text: How much of the last seconds it waited.
        failed_text: Why the last join or leave did not go through.
        step_text: The tooltip of Step.
        restart_text: The tooltip of Restart.
        marks: The other devices' resets, oldest first.
        file_path: The bench file the devices run from.
    """

    revision: int = 0
    revision_text: str = ""
    phase: BenchPhase = BenchPhase.ALONE
    name: str = ""
    title: str = ""
    devices: tuple[BenchDevice, ...] = ()
    buses: tuple[JoinedBus, ...] = ()
    waiting_for_text: str = ""
    waiting_share_text: str = ""
    failed_text: str = ""
    step_text: str = ""
    restart_text: str = ""
    marks: tuple[BenchMark, ...] = ()
    file_path: str = ""

    def device(self, name: str) -> BenchDevice:
        """The device of that name.

        Raises:
            KeyError: If no device of the bench is called so.
        """
        for device in self.devices:
            if device.name == name:
                return device
        raise KeyError(f"no device {name!r} on the bench; it has {self.device_names}")

    @property
    def device_names(self) -> tuple[str, ...]:
        """The devices' names, the leader first."""
        return tuple(device.name for device in self.devices)

    @property
    def this_device(self) -> BenchDevice | None:
        """The device of the server that answered; None off a bench."""
        return next((device for device in self.devices if device.this_device), None)

    @property
    def leader(self) -> BenchDevice | None:
        """The device that leads the bench; None off a bench."""
        return next((device for device in self.devices if device.leader), None)


@dataclass(frozen=True)
class JoinBusChoice:
    """One bus of another server that this device's bus could be joined with.

    Attributes:
        bus_id: Its runtime bus id on the other device.
        label: ``CAN1``.
        text: ``CAN1 · 500 kbit/s``.
        bitrate: Bits per second; 0 while its firmware has set none.
        preselected: The one that fits: the same label, else the same bit rate.
        mismatch_text: A bit-rate mismatch in a sentence; it does not block.
    """

    bus_id: int
    label: str
    text: str = ""
    bitrate: int = 0
    preselected: bool = False
    mismatch_text: str = ""


@dataclass(frozen=True)
class JoinCandidate:
    """Another server on this PC, and whether this device's bus can be joined with it.

    Attributes:
        instance_id: Its registry entry, which a join names.
        address: Where it listens.
        firmware_name: The firmware it runs.
        definition_path: Its ``looper.toml``.
        joinable: Whether it can be joined.
        reason_text: Why not, ``has no CAN bus``; empty when it can be.
        buses: Its buses of this bus's kind, the one that fits first.
        joining_text: What joining does, in one or two sentences.
    """

    instance_id: str
    address: str = ""
    firmware_name: str = ""
    definition_path: str = ""
    joinable: bool = False
    reason_text: str = ""
    buses: tuple[JoinBusChoice, ...] = ()
    joining_text: str = ""

    @property
    def preselected_bus(self) -> JoinBusChoice | None:
        """The bus the server preselected, else the first; None without one."""
        chosen = next((bus for bus in self.buses if bus.preselected), None)
        return chosen or next(iter(self.buses), None)


@dataclass(frozen=True)
class JoinCandidates:
    """What the Join dialog shows: the other servers on this PC.

    Attributes:
        title: ``Join CAN1 of thermostat with another device``.
        candidates: Every other server, simulations first, joinable or not.
    """

    title: str = ""
    candidates: tuple[JoinCandidate, ...] = ()

    def running(self, firmware_name: str) -> JoinCandidate:
        """The candidate that runs a firmware of that name.

        Raises:
            KeyError: If no other server runs it.
        """
        for candidate in self.candidates:
            if candidate.firmware_name == firmware_name:
                return candidate
        names = [candidate.firmware_name for candidate in self.candidates]
        raise KeyError(f"no other server runs {firmware_name!r}; they run {names}")
