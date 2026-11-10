"""The port answered by a server speaking the inspector contract over gRPC.

The contract has two ways to refuse and one to fail, and they become the
port's two. A change a server declines comes back acknowledged with a
refusal and its text; a read it declines, or any call while a debugger holds
the firmware, is `FAILED_PRECONDITION`. Both are `SimulationRefusedError`.
A part of looper Pro without a licence is `PERMISSION_DENIED`, which is
`ProFeatureLockedError`, a kind of refusal.
Anything else means the simulation can no longer be read.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import grpc

from looper.application.ports import (
    ContractNotServedError,
    Inspector,
    ProFeatureLockedError,
    SimulationRefusedError,
    SimulationUnreachableError,
)
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    Description,
    EventPage,
    Findings,
    LifeDump,
    Lives,
    MemoryUsage,
    Pin,
    Profile,
    RunStatus,
    Signal,
    SignalGraph,
    SignalModel,
    Trigger,
    TriggerRequest,
    Variable,
    Watch,
)
from looper.infrastructure import (
    analysis_translation,
    life_translation,
    signal_graph_translation,
    translation,
    trigger_translation,
)
from looper.infrastructure.client_identity import describe_request
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_boot import GrpcBootCalls
from looper.infrastructure.grpc_chains import GrpcChainCalls
from looper.infrastructure.grpc_interrupts import GrpcInterruptCalls

#: How long reaching a server may take before it counts as absent.
CONNECT_TIMEOUT_SECONDS = 5.0

#: The version of the contract this library was built against.
CONTRACT_VERSION = contract.CONTRACT_VERSION_CURRENT

#: The largest answer the channel takes. The catalogue of a firmware of
#: ordinary size is some 12 MB, three times gRPC's default.
MAX_MESSAGE_BYTES = 64 * 1024 * 1024

#: How long to wait between two looks at a run that is still under way.
RUN_POLL_SECONDS = 0.02

EMPTY = contract.Empty()

#: The kinds of event a test looks at; the stream also carries pin changes,
#: calls, applied commands and more.
EVENT_KINDS = [
    contract.EVENT_KIND_SAMPLE,
    contract.EVENT_KIND_EXCHANGE,
    contract.EVENT_KIND_RESET,
    contract.EVENT_KIND_FLASH,
    contract.EVENT_KIND_INTERRUPT,
]


class GrpcInspector(GrpcBootCalls, GrpcInterruptCalls, GrpcChainCalls, Inspector):
    """The inspector contract, spoken to a server at one address."""

    def __init__(self, address: str, timeout_seconds: float = CONNECT_TIMEOUT_SECONDS) -> None:
        """Connect to a server listening at `address`, such as ``127.0.0.1:50051``.

        Raises:
            SimulationUnreachableError: If nothing answers there in time.
        """
        self._channel = grpc.insecure_channel(
            address, options=[("grpc.max_receive_message_length", MAX_MESSAGE_BYTES)]
        )
        try:
            grpc.channel_ready_future(self._channel).result(timeout=timeout_seconds)
        except grpc.FutureTimeoutError as error:
            self._channel.close()
            raise SimulationUnreachableError(f"no inspector server at {address}") from error
        self._stub: Any = service.InspectorStub(self._channel)

    def describe(self) -> Description:
        """What the server is attached to."""
        return translation.description_of(self._call(self._stub.Describe, describe_request()))

    def read_events(self, epoch: int, from_event_seq: int) -> EventPage:
        """One page of samples and exchanges, from an event number on."""
        request = contract.ReadEventsRequest(
            epoch=epoch,
            from_event_seq=from_event_seq,
            filter=contract.EventFilter(kinds=EVENT_KINDS),
        )
        return translation.event_page_of(self._call(self._stub.ReadEvents, request))

    def read_timings(self) -> tuple[CallTiming, ...]:
        """How often each adapter function was called since the last reset."""
        return translation.timings_of(self._call(self._stub.ObserveTimings, EMPTY))

    def read_memory(self) -> MemoryUsage:
        """The heap and the stack."""
        return translation.memory_of(self._call(self._stub.ObserveMemory, EMPTY))

    def read_profile(self) -> Profile:
        """Where the simulation spent its time, function by function, since the last clearing."""
        return analysis_translation.profile_of(self._call(self._stub.ObserveProfile, EMPTY))

    def read_findings(self) -> Findings:
        """What the architecture analysis found in the project's code, so far."""
        listing = self._call(self._stub.ObserveFindings, contract.FindingFilter())
        return analysis_translation.findings_of(listing)

    def read_pins(self) -> tuple[Pin, ...]:
        """Every pin the firmware registered, with its level."""
        return translation.pins_of(self._call(self._stub.ObserveSimulation, EMPTY))

    def read_channels(self) -> tuple[Channel, ...]:
        """Every analog channel the firmware registered, with its value."""
        return translation.channels_of(self._call(self._stub.ObserveChannels, EMPTY))

    def read_buses(self) -> tuple[Bus, ...]:
        """Every bus the simulation models."""
        return translation.buses_of(self._call(self._stub.ObserveBuses, EMPTY))

    def run_state(self) -> RunStatus:
        """Where the clock is and how it goes now."""
        return translation.run_status_of(self._call(self._stub.ObserveRun, EMPTY))

    def run_for(self, microseconds: int) -> RunStatus:
        """Let time pass on a held clock, and return once it has.

        The server may answer at once with the run still under way; then the
        run is looked at until it has reached its end.
        """
        reply = self._call(self._stub.ControlRun, contract.RunControl(run_for_us=microseconds))
        _acknowledged(reply.ack)
        state = translation.run_status_of(reply.state)
        while state.target_us != 0:
            time.sleep(RUN_POLL_SECONDS)
            state = self.run_state()
        return state

    def clear_recordings(self, epoch: int) -> None:
        """Discard the recorded events, for every client, and begin the next epoch."""
        _acknowledged(self._call(self._stub.ClearRecordings, contract.ClearRequest(epoch=epoch)))

    def clear_measurements(self) -> None:
        """Begin the call counts, the profile and the heap again."""
        self._call(self._stub.ClearMeasurements, EMPTY)

    def toggle_pin(self, pin_id: int) -> str:
        """Drive the opposite of the level a pin is at, and say which."""
        drive = contract.PinDrive(pin_id=pin_id, toggle=EMPTY)
        driven = self._call(self._stub.DrivePin, drive)
        _acknowledged(driven.ack)
        return "high" if driven.high else "low"

    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        """Install a generated signal on an analog input."""
        request = translation.signal_request_of(channel_id, signal)
        _acknowledged(self._call(self._stub.ApplySignal, request))

    def apply_signal_graph(self, graph: SignalGraph) -> None:
        """Replace the graph of signals that drives the analog inputs."""
        request = signal_graph_translation.signal_graph_request_of(graph)
        _acknowledged(self._call(self._stub.ApplySignalGraph, request))

    def set_graph_value(self, node: str, value: float) -> None:
        """Change what one value node of the applied graph gives."""
        request = contract.GraphValueRequest(node=node, value=value)
        _acknowledged(self._call(self._stub.SetGraphValue, request))

    def list_models(self) -> tuple[SignalModel, ...]:
        """The models the project offers the signal graph."""
        listing = self._call(self._stub.ListModels, EMPTY)
        if listing.unavailable_reason:
            raise SimulationRefusedError(listing.unavailable_reason)
        return signal_graph_translation.models_of(listing)

    def send_bus_message(self, message: BusMessage) -> None:
        """Put one message on a bus."""
        request = translation.bus_message_request_of(message)
        _acknowledged(self._call(self._stub.SendBusMessage, request).ack)

    def list_variables(self) -> tuple[Variable, ...]:
        """The catalogue of the firmware's variables, read out of the build."""
        catalogue = self._call(self._stub.ListVariables, EMPTY)
        if catalogue.unavailable_reason:
            raise SimulationRefusedError(catalogue.unavailable_reason)
        return translation.variables_of(catalogue)

    def watch_variable(self, variable_id: int) -> Watch:
        """Begin sampling a variable from the catalogue."""
        choice = contract.VariableChoice(variable_id=variable_id)
        started = self._call(self._stub.WatchVariable, choice)
        _acknowledged(started.ack)
        return translation.watch_of(started.watch)

    def write_variable(self, channel_id: int, value: float) -> None:
        """Store a value in a watched variable."""
        write = contract.VariableWrite(channel_id=channel_id, value=value)
        _acknowledged(self._call(self._stub.WriteVariable, write))

    def remove_watch(self, channel_id: int) -> None:
        """Stop sampling a watched variable."""
        removal = contract.WatchChoice(channel_id=channel_id)
        _acknowledged(self._call(self._stub.RemoveWatch, removal))

    def read_watches(self) -> tuple[Watch, ...]:
        """Every variable being sampled, with its value now."""
        return translation.watches_of(self._call(self._stub.ObserveWatches, EMPTY))

    def arm_trigger(self, request: TriggerRequest, armed_by: str) -> Trigger:
        """Have the simulation watch for a condition."""
        spec = trigger_translation.spec_of(request, armed_by)
        view = self._call(self._stub.ArmTrigger, spec)
        _acknowledged(view.ack)
        return trigger_translation.trigger_of(view)

    def disarm_trigger(self, trigger_id: int, by_client: str) -> Trigger:
        """Stop a trigger, whichever client armed it."""
        choice = contract.TriggerChoice(trigger_id=trigger_id, by_client=by_client)
        view = self._call(self._stub.DisarmTrigger, choice)
        _acknowledged(view.ack)
        return trigger_translation.trigger_of(view)

    def read_triggers(self) -> tuple[Trigger, ...]:
        """Every trigger the simulation holds, armed or not, from every client."""
        listing = self._call(self._stub.ObserveTriggers, EMPTY)
        return tuple(trigger_translation.trigger_of(view) for view in listing.triggers)

    def reset_firmware(self, cause: str) -> None:
        """Reset the firmware from outside: ``pin``, ``power-on`` or ``brown-out``.

        Raises:
            ValueError: If the word is no cause of a reset at all; nothing is sent.
            SimulationRefusedError: If the server refuses the cause.
        """
        wanted = life_translation.CAUSES.get(cause)
        if wanted is None:
            words = ", ".join(life_translation.CAUSES)
            raise ValueError(f"not a reset cause: {cause}; one of {words}")
        request = contract.ResetRequest(cause=wanted)
        _acknowledged(self._call(self._stub.ResetFirmware, request))

    def read_lives(self) -> Lives:
        """Every life of the run."""
        return life_translation.lives_of(self._call(self._stub.ObserveLives, EMPTY))

    def read_life_dump(self, life: int) -> LifeDump:
        """What a life that ended left behind."""
        view = self._call(self._stub.ReadLifeDump, contract.LifeChoice(life=life))
        return life_translation.dump_of(view)

    def read_retained(self) -> bytes:
        """The whole retained memory."""
        return bytes(self._call(self._stub.ObserveRetained, EMPTY).content)

    def write_retained(self, offset: int, data: bytes) -> None:
        """Write bytes into the retained memory."""
        request = contract.RetainedWrite(offset=offset, data=data)
        _acknowledged(self._call(self._stub.WriteRetained, request))

    def read_flash(self, offset: int, length: int) -> bytes:
        """Bytes of the flash from its beginning; length 0 reads to its end."""
        if length == 0:
            return self.save_flash()[offset:]
        request = contract.FlashRequest(offset=offset, length=length)
        return bytes(self._call(self._stub.ObserveFlash, request).content)

    def flash_partitions(self) -> dict[str, tuple[int, int]]:
        """Every partition: its offset and size, by name."""
        view = self._call(self._stub.ObserveFlash, contract.FlashRequest())
        return {one.name: (one.offset, one.size) for one in view.partitions}

    def write_flash(self, offset: int, data: bytes, raw: bool) -> None:
        """Write bytes into the flash."""
        request = contract.FlashWrite(offset=offset, data=data, raw=raw)
        _acknowledged(self._call(self._stub.WriteFlash, request))

    def erase_flash(self, partition: str = "", sector: int | None = None) -> None:
        """Erase a partition, a sector, or the whole flash."""
        if partition:
            request = contract.FlashErase(partition=partition)
        elif sector is not None:
            request = contract.FlashErase(sector=sector)
        else:
            request = contract.FlashErase(whole=EMPTY)
        _acknowledged(self._call(self._stub.EraseFlash, request))

    def save_flash(self) -> bytes:
        """The whole flash."""
        return bytes(self._call(self._stub.SaveFlash, EMPTY).content)

    def load_flash(self, content: bytes) -> None:
        """Lay a saved flash down."""
        request = contract.FlashContent(content=content)
        _acknowledged(self._call(self._stub.LoadFlash, request))

    def close(self) -> None:
        """Let go of the connection. Closing twice is allowed."""
        self._channel.close()

    @staticmethod
    def _taken(ack: contract.Ack) -> None:
        """Pass a change the server took; refuse one it declined."""
        _acknowledged(ack)

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        """Make one call, turning a failure into the port's two kinds."""
        try:
            return method(request)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.PERMISSION_DENIED:
                raise ProFeatureLockedError(error.details()) from error
            if error.code() in (grpc.StatusCode.FAILED_PRECONDITION, grpc.StatusCode.NOT_FOUND):
                raise SimulationRefusedError(error.details()) from error
            if error.code() == grpc.StatusCode.UNIMPLEMENTED:
                raise ContractNotServedError(error.details() or "method not found") from error
            raise SimulationUnreachableError(error.details() or str(error.code())) from error


def _acknowledged(ack: contract.Ack) -> None:
    """Pass a change the server took; turn one it declined into a refusal."""
    if ack.refusal == contract.REFUSAL_NONE:
        return
    raise SimulationRefusedError(ack.refusal_text or contract.Refusal.Name(ack.refusal))
