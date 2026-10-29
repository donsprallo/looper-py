"""The port answered by a server speaking the inspector contract over gRPC.

The contract has two answers to a failure, and they become the port's two:
`FAILED_PRECONDITION` is a refusal with its reason, anything else means the
simulation can no longer be read.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import grpc

from looper.application.ports import (
    Inspector,
    SimulationRefusedError,
    SimulationUnreachableError,
)
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    Description,
    MemoryUsage,
    Pin,
    Recordings,
    Signal,
    Variable,
    Watch,
)
from looper.infrastructure import translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

#: How long reaching a server may take before it counts as absent.
CONNECT_TIMEOUT_SECONDS = 5.0

#: The version of the contract this library was built against.
CONTRACT_VERSION = contract.CONTRACT_VERSION_CURRENT

#: The largest answer the channel takes. The catalogue of a firmware of
#: ordinary size is some 12 MB, three times gRPC's default.
MAX_MESSAGE_BYTES = 64 * 1024 * 1024

EMPTY = contract.Empty()


class GrpcInspector(Inspector):
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
        return translation.description_of(self._call(self._stub.Describe, EMPTY))

    def read_recordings(self, after_sample: int, after_exchange: int) -> Recordings:
        """Samples and exchanges recorded since the given positions."""
        positions = contract.RecordingPositions(
            after_sample=after_sample, after_exchange=after_exchange
        )
        return translation.recordings_of(self._call(self._stub.ReadRecordings, positions))

    def read_timings(self) -> tuple[CallTiming, ...]:
        """How often each adapter function was called since the last reset."""
        return translation.timings_of(self._call(self._stub.ObserveTimings, EMPTY))

    def read_memory(self) -> MemoryUsage:
        """The heap and the stack."""
        return translation.memory_of(self._call(self._stub.ObserveMemory, EMPTY))

    def read_pins(self) -> tuple[Pin, ...]:
        """Every pin the firmware registered, with its level."""
        return translation.pins_of(self._call(self._stub.ObserveSimulation, EMPTY))

    def read_channels(self) -> tuple[Channel, ...]:
        """Every analog channel the firmware registered, with its value."""
        return translation.channels_of(self._call(self._stub.ObserveChannels, EMPTY))

    def read_buses(self) -> tuple[Bus, ...]:
        """Every bus the simulation models."""
        return translation.buses_of(self._call(self._stub.ObserveBuses, EMPTY))

    def simulated_microseconds(self) -> int:
        """How much simulated time has passed."""
        return int(self._call(self._stub.ObserveSimulation, EMPTY).microseconds)

    def advance(self, microseconds: int) -> None:
        """Let time pass on a virtual clock."""
        self._call(self._stub.AdvanceTime, contract.TimeStep(microseconds=microseconds))

    def clear_recordings(self) -> None:
        """Discard the recorded samples and exchanges, for every client."""
        self._call(self._stub.ClearTrace, EMPTY)
        self._call(self._stub.ClearBusTrace, EMPTY)

    def clear_measurements(self) -> None:
        """Begin the call counts, the profile and the heap again."""
        self._call(self._stub.ClearMeasurements, EMPTY)

    def toggle_pin(self, pin_id: int, current_level: str) -> str:
        """Drive the opposite of the level a pin was seen at, and say which."""
        toggle = contract.PinToggle(pin_id=pin_id, current_level=current_level)
        return str(self._call(self._stub.TogglePin, toggle).level)

    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        """Install a generated signal on an analog input."""
        request = translation.signal_request_of(channel_id, signal)
        self._call(self._stub.ApplySignal, request)

    def send_bus_message(self, message: BusMessage) -> None:
        """Put one message on a bus."""
        request = translation.bus_message_request_of(message)
        self._call(self._stub.SendBusMessage, request)

    def list_variables(self) -> tuple[Variable, ...]:
        """The catalogue of the firmware's variables, read out of the build."""
        catalogue = self._call(self._stub.ListVariables, EMPTY)
        if catalogue.unavailable_reason:
            raise SimulationRefusedError(catalogue.unavailable_reason)
        return translation.variables_of(catalogue)

    def watch_variable(self, variable_id: int) -> Watch:
        """Begin sampling a variable from the catalogue."""
        choice = contract.VariableChoice(variable_id=variable_id)
        return translation.watch_of(self._call(self._stub.WatchVariable, choice))

    def write_variable(self, channel_id: int, value: float) -> None:
        """Store a value in a watched variable."""
        write = contract.VariableWrite(channel_id=channel_id, value=value)
        self._call(self._stub.WriteVariable, write)

    def remove_watch(self, channel_id: int) -> None:
        """Stop sampling a watched variable."""
        self._call(self._stub.RemoveWatch, contract.WatchChoice(channel_id=channel_id))

    def read_watches(self) -> tuple[Watch, ...]:
        """Every variable being sampled, with its value now."""
        return translation.watches_of(self._call(self._stub.ObserveWatches, EMPTY))

    def close(self) -> None:
        """Let go of the connection. Closing twice is allowed."""
        self._channel.close()

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        """Make one call, turning a failure into the port's two kinds."""
        try:
            return method(request)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.FAILED_PRECONDITION:
                raise SimulationRefusedError(error.details()) from error
            raise SimulationUnreachableError(error.details() or str(error.code())) from error
