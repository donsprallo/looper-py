from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContractVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTRACT_VERSION_UNSPECIFIED: _ClassVar[ContractVersion]
    CONTRACT_VERSION_CURRENT: _ClassVar[ContractVersion]
CONTRACT_VERSION_UNSPECIFIED: ContractVersion
CONTRACT_VERSION_CURRENT: ContractVersion

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Description(_message.Message):
    __slots__ = ("contract_version", "firmware_name", "time_mode", "reads_the_build", "definition_path")
    CONTRACT_VERSION_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIME_MODE_FIELD_NUMBER: _ClassVar[int]
    READS_THE_BUILD_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_PATH_FIELD_NUMBER: _ClassVar[int]
    contract_version: ContractVersion
    firmware_name: str
    time_mode: str
    reads_the_build: bool
    definition_path: str
    def __init__(self, contract_version: _Optional[_Union[ContractVersion, str]] = ..., firmware_name: _Optional[str] = ..., time_mode: _Optional[str] = ..., reads_the_build: _Optional[bool] = ..., definition_path: _Optional[str] = ...) -> None: ...

class PinView(_message.Message):
    __slots__ = ("pin_id", "name", "direction", "level", "is_active", "is_drivable")
    PIN_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_DRIVABLE_FIELD_NUMBER: _ClassVar[int]
    pin_id: int
    name: str
    direction: str
    level: str
    is_active: bool
    is_drivable: bool
    def __init__(self, pin_id: _Optional[int] = ..., name: _Optional[str] = ..., direction: _Optional[str] = ..., level: _Optional[str] = ..., is_active: _Optional[bool] = ..., is_drivable: _Optional[bool] = ...) -> None: ...

class SimulationView(_message.Message):
    __slots__ = ("microseconds", "time_mode", "pins")
    MICROSECONDS_FIELD_NUMBER: _ClassVar[int]
    TIME_MODE_FIELD_NUMBER: _ClassVar[int]
    PINS_FIELD_NUMBER: _ClassVar[int]
    microseconds: int
    time_mode: str
    pins: _containers.RepeatedCompositeFieldContainer[PinView]
    def __init__(self, microseconds: _Optional[int] = ..., time_mode: _Optional[str] = ..., pins: _Optional[_Iterable[_Union[PinView, _Mapping]]] = ...) -> None: ...

class PinToggle(_message.Message):
    __slots__ = ("pin_id", "current_level")
    PIN_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LEVEL_FIELD_NUMBER: _ClassVar[int]
    pin_id: int
    current_level: str
    def __init__(self, pin_id: _Optional[int] = ..., current_level: _Optional[str] = ...) -> None: ...

class PinLevel(_message.Message):
    __slots__ = ("level",)
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    level: str
    def __init__(self, level: _Optional[str] = ...) -> None: ...

class SignalView(_message.Message):
    __slots__ = ("waveform", "amplitude", "offset", "frequency_hz", "phase_degrees")
    WAVEFORM_FIELD_NUMBER: _ClassVar[int]
    AMPLITUDE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_HZ_FIELD_NUMBER: _ClassVar[int]
    PHASE_DEGREES_FIELD_NUMBER: _ClassVar[int]
    waveform: str
    amplitude: float
    offset: float
    frequency_hz: float
    phase_degrees: float
    def __init__(self, waveform: _Optional[str] = ..., amplitude: _Optional[float] = ..., offset: _Optional[float] = ..., frequency_hz: _Optional[float] = ..., phase_degrees: _Optional[float] = ...) -> None: ...

class ChannelView(_message.Message):
    __slots__ = ("channel_id", "name", "unit", "direction", "value", "is_drivable", "signal", "is_silent", "display_value")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_DRIVABLE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    IS_SILENT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_VALUE_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    name: str
    unit: str
    direction: str
    value: float
    is_drivable: bool
    signal: SignalView
    is_silent: bool
    display_value: str
    def __init__(self, channel_id: _Optional[int] = ..., name: _Optional[str] = ..., unit: _Optional[str] = ..., direction: _Optional[str] = ..., value: _Optional[float] = ..., is_drivable: _Optional[bool] = ..., signal: _Optional[_Union[SignalView, _Mapping]] = ..., is_silent: _Optional[bool] = ..., display_value: _Optional[str] = ...) -> None: ...

class ChannelList(_message.Message):
    __slots__ = ("channels",)
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedCompositeFieldContainer[ChannelView]
    def __init__(self, channels: _Optional[_Iterable[_Union[ChannelView, _Mapping]]] = ...) -> None: ...

class SignalRequest(_message.Message):
    __slots__ = ("channel_id", "signal")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    signal: SignalView
    def __init__(self, channel_id: _Optional[int] = ..., signal: _Optional[_Union[SignalView, _Mapping]] = ...) -> None: ...

class WaveformView(_message.Message):
    __slots__ = ("name", "display_name", "is_alternating")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ALTERNATING_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    is_alternating: bool
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., is_alternating: _Optional[bool] = ...) -> None: ...

class WaveformList(_message.Message):
    __slots__ = ("waveforms",)
    WAVEFORMS_FIELD_NUMBER: _ClassVar[int]
    waveforms: _containers.RepeatedCompositeFieldContainer[WaveformView]
    def __init__(self, waveforms: _Optional[_Iterable[_Union[WaveformView, _Mapping]]] = ...) -> None: ...

class SampleView(_message.Message):
    __slots__ = ("channel_id", "seconds", "value", "sequence")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    seconds: float
    value: float
    sequence: int
    def __init__(self, channel_id: _Optional[int] = ..., seconds: _Optional[float] = ..., value: _Optional[float] = ..., sequence: _Optional[int] = ...) -> None: ...

class TraceView(_message.Message):
    __slots__ = ("samples", "next_sequence")
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    NEXT_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[SampleView]
    next_sequence: int
    def __init__(self, samples: _Optional[_Iterable[_Union[SampleView, _Mapping]]] = ..., next_sequence: _Optional[int] = ...) -> None: ...

class ExchangeView(_message.Message):
    __slots__ = ("bus_id", "kind", "seconds", "direction", "address", "length", "payload", "response", "accepted", "sequence")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    kind: str
    seconds: float
    direction: str
    address: str
    length: int
    payload: str
    response: str
    accepted: bool
    sequence: int
    def __init__(self, bus_id: _Optional[int] = ..., kind: _Optional[str] = ..., seconds: _Optional[float] = ..., direction: _Optional[str] = ..., address: _Optional[str] = ..., length: _Optional[int] = ..., payload: _Optional[str] = ..., response: _Optional[str] = ..., accepted: _Optional[bool] = ..., sequence: _Optional[int] = ...) -> None: ...

class BusTraceView(_message.Message):
    __slots__ = ("exchanges", "next_sequence")
    EXCHANGES_FIELD_NUMBER: _ClassVar[int]
    NEXT_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    exchanges: _containers.RepeatedCompositeFieldContainer[ExchangeView]
    next_sequence: int
    def __init__(self, exchanges: _Optional[_Iterable[_Union[ExchangeView, _Mapping]]] = ..., next_sequence: _Optional[int] = ...) -> None: ...

class RecordingPositions(_message.Message):
    __slots__ = ("after_sample", "after_exchange")
    AFTER_SAMPLE_FIELD_NUMBER: _ClassVar[int]
    AFTER_EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    after_sample: int
    after_exchange: int
    def __init__(self, after_sample: _Optional[int] = ..., after_exchange: _Optional[int] = ...) -> None: ...

class Recordings(_message.Message):
    __slots__ = ("trace", "bus_trace")
    TRACE_FIELD_NUMBER: _ClassVar[int]
    BUS_TRACE_FIELD_NUMBER: _ClassVar[int]
    trace: TraceView
    bus_trace: BusTraceView
    def __init__(self, trace: _Optional[_Union[TraceView, _Mapping]] = ..., bus_trace: _Optional[_Union[BusTraceView, _Mapping]] = ...) -> None: ...

class VariableView(_message.Message):
    __slots__ = ("variable_id", "path", "name", "root", "segments", "encoding", "byte_width", "link_time_address", "runtime_address", "is_writable", "bit_offset", "bit_width", "origin", "is_firmware", "declared_in", "display_type", "display_address")
    VARIABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    BYTE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    LINK_TIME_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IS_WRITABLE_FIELD_NUMBER: _ClassVar[int]
    BIT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    BIT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    IS_FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    DECLARED_IN_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    variable_id: int
    path: str
    name: str
    root: str
    segments: _containers.RepeatedScalarFieldContainer[str]
    encoding: str
    byte_width: int
    link_time_address: int
    runtime_address: int
    is_writable: bool
    bit_offset: int
    bit_width: int
    origin: str
    is_firmware: bool
    declared_in: str
    display_type: str
    display_address: str
    def __init__(self, variable_id: _Optional[int] = ..., path: _Optional[str] = ..., name: _Optional[str] = ..., root: _Optional[str] = ..., segments: _Optional[_Iterable[str]] = ..., encoding: _Optional[str] = ..., byte_width: _Optional[int] = ..., link_time_address: _Optional[int] = ..., runtime_address: _Optional[int] = ..., is_writable: _Optional[bool] = ..., bit_offset: _Optional[int] = ..., bit_width: _Optional[int] = ..., origin: _Optional[str] = ..., is_firmware: _Optional[bool] = ..., declared_in: _Optional[str] = ..., display_type: _Optional[str] = ..., display_address: _Optional[str] = ...) -> None: ...

class VariableCatalogue(_message.Message):
    __slots__ = ("variables", "unavailable_reason")
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    UNAVAILABLE_REASON_FIELD_NUMBER: _ClassVar[int]
    variables: _containers.RepeatedCompositeFieldContainer[VariableView]
    unavailable_reason: str
    def __init__(self, variables: _Optional[_Iterable[_Union[VariableView, _Mapping]]] = ..., unavailable_reason: _Optional[str] = ...) -> None: ...

class VariableChoice(_message.Message):
    __slots__ = ("variable_id",)
    VARIABLE_ID_FIELD_NUMBER: _ClassVar[int]
    variable_id: int
    def __init__(self, variable_id: _Optional[int] = ...) -> None: ...

class WatchView(_message.Message):
    __slots__ = ("channel_id", "path", "name", "encoding", "byte_width", "runtime_address", "is_writable", "value", "bit_offset", "bit_width", "display_value", "range_text", "unit")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    BYTE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IS_WRITABLE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    BIT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    BIT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_VALUE_FIELD_NUMBER: _ClassVar[int]
    RANGE_TEXT_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    path: str
    name: str
    encoding: str
    byte_width: int
    runtime_address: int
    is_writable: bool
    value: float
    bit_offset: int
    bit_width: int
    display_value: str
    range_text: str
    unit: str
    def __init__(self, channel_id: _Optional[int] = ..., path: _Optional[str] = ..., name: _Optional[str] = ..., encoding: _Optional[str] = ..., byte_width: _Optional[int] = ..., runtime_address: _Optional[int] = ..., is_writable: _Optional[bool] = ..., value: _Optional[float] = ..., bit_offset: _Optional[int] = ..., bit_width: _Optional[int] = ..., display_value: _Optional[str] = ..., range_text: _Optional[str] = ..., unit: _Optional[str] = ...) -> None: ...

class WatchList(_message.Message):
    __slots__ = ("watches",)
    WATCHES_FIELD_NUMBER: _ClassVar[int]
    watches: _containers.RepeatedCompositeFieldContainer[WatchView]
    def __init__(self, watches: _Optional[_Iterable[_Union[WatchView, _Mapping]]] = ...) -> None: ...

class WatchChoice(_message.Message):
    __slots__ = ("channel_id",)
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    def __init__(self, channel_id: _Optional[int] = ...) -> None: ...

class VariableWrite(_message.Message):
    __slots__ = ("channel_id", "value")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    value: float
    def __init__(self, channel_id: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class BusView(_message.Message):
    __slots__ = ("bus_id", "kind", "name", "bitrate_bps", "display_bitrate", "accepts_messages")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BITRATE_BPS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_BITRATE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTS_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    kind: str
    name: str
    bitrate_bps: int
    display_bitrate: str
    accepts_messages: bool
    def __init__(self, bus_id: _Optional[int] = ..., kind: _Optional[str] = ..., name: _Optional[str] = ..., bitrate_bps: _Optional[int] = ..., display_bitrate: _Optional[str] = ..., accepts_messages: _Optional[bool] = ...) -> None: ...

class BusList(_message.Message):
    __slots__ = ("buses",)
    BUSES_FIELD_NUMBER: _ClassVar[int]
    buses: _containers.RepeatedCompositeFieldContainer[BusView]
    def __init__(self, buses: _Optional[_Iterable[_Union[BusView, _Mapping]]] = ...) -> None: ...

class ComponentView(_message.Message):
    __slots__ = ("bus_id", "address", "name", "model", "properties")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    address: str
    name: str
    model: str
    properties: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bus_id: _Optional[int] = ..., address: _Optional[str] = ..., name: _Optional[str] = ..., model: _Optional[str] = ..., properties: _Optional[_Iterable[int]] = ...) -> None: ...

class ComponentList(_message.Message):
    __slots__ = ("components",)
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    components: _containers.RepeatedCompositeFieldContainer[ComponentView]
    def __init__(self, components: _Optional[_Iterable[_Union[ComponentView, _Mapping]]] = ...) -> None: ...

class BusMessageRequest(_message.Message):
    __slots__ = ("bus_id", "address", "payload", "extended")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    address: int
    payload: bytes
    extended: bool
    def __init__(self, bus_id: _Optional[int] = ..., address: _Optional[int] = ..., payload: _Optional[bytes] = ..., extended: _Optional[bool] = ...) -> None: ...

class PartyView(_message.Message):
    __slots__ = ("address", "name", "is_silent")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_SILENT_FIELD_NUMBER: _ClassVar[int]
    address: str
    name: str
    is_silent: bool
    def __init__(self, address: _Optional[str] = ..., name: _Optional[str] = ..., is_silent: _Optional[bool] = ...) -> None: ...

class StepView(_message.Message):
    __slots__ = ("seconds", "gap", "column", "is_outbound", "payload", "response", "was_taken")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    GAP_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    IS_OUTBOUND_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    WAS_TAKEN_FIELD_NUMBER: _ClassVar[int]
    seconds: float
    gap: str
    column: int
    is_outbound: bool
    payload: str
    response: str
    was_taken: bool
    def __init__(self, seconds: _Optional[float] = ..., gap: _Optional[str] = ..., column: _Optional[int] = ..., is_outbound: _Optional[bool] = ..., payload: _Optional[str] = ..., response: _Optional[str] = ..., was_taken: _Optional[bool] = ...) -> None: ...

class LadderView(_message.Message):
    __slots__ = ("bus_name", "parties", "steps", "note")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    parties: _containers.RepeatedCompositeFieldContainer[PartyView]
    steps: _containers.RepeatedCompositeFieldContainer[StepView]
    note: str
    def __init__(self, bus_name: _Optional[str] = ..., parties: _Optional[_Iterable[_Union[PartyView, _Mapping]]] = ..., steps: _Optional[_Iterable[_Union[StepView, _Mapping]]] = ..., note: _Optional[str] = ...) -> None: ...

class LadderChoice(_message.Message):
    __slots__ = ("bus_id",)
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    def __init__(self, bus_id: _Optional[int] = ...) -> None: ...

class WindowView(_message.Message):
    __slots__ = ("start_seconds", "end_seconds")
    START_SECONDS_FIELD_NUMBER: _ClassVar[int]
    END_SECONDS_FIELD_NUMBER: _ClassVar[int]
    start_seconds: float
    end_seconds: float
    def __init__(self, start_seconds: _Optional[float] = ..., end_seconds: _Optional[float] = ...) -> None: ...

class MarkView(_message.Message):
    __slots__ = ("seconds", "label", "detail", "duration_seconds", "is_doubtful", "is_high")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    IS_DOUBTFUL_FIELD_NUMBER: _ClassVar[int]
    IS_HIGH_FIELD_NUMBER: _ClassVar[int]
    seconds: float
    label: str
    detail: str
    duration_seconds: float
    is_doubtful: bool
    is_high: bool
    def __init__(self, seconds: _Optional[float] = ..., label: _Optional[str] = ..., detail: _Optional[str] = ..., duration_seconds: _Optional[float] = ..., is_doubtful: _Optional[bool] = ..., is_high: _Optional[bool] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("seconds", "value")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    seconds: float
    value: float
    def __init__(self, seconds: _Optional[float] = ..., value: _Optional[float] = ...) -> None: ...

class LaneView(_message.Message):
    __slots__ = ("key", "label", "kind", "marks", "count", "gaps", "usual_gap_seconds", "worst_gap_seconds", "summary")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    MARKS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    GAPS_FIELD_NUMBER: _ClassVar[int]
    USUAL_GAP_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WORST_GAP_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    key: str
    label: str
    kind: str
    marks: _containers.RepeatedCompositeFieldContainer[MarkView]
    count: int
    gaps: _containers.RepeatedCompositeFieldContainer[Point]
    usual_gap_seconds: float
    worst_gap_seconds: float
    summary: str
    def __init__(self, key: _Optional[str] = ..., label: _Optional[str] = ..., kind: _Optional[str] = ..., marks: _Optional[_Iterable[_Union[MarkView, _Mapping]]] = ..., count: _Optional[int] = ..., gaps: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., usual_gap_seconds: _Optional[float] = ..., worst_gap_seconds: _Optional[float] = ..., summary: _Optional[str] = ...) -> None: ...

class CurveView(_message.Message):
    __slots__ = ("key", "label", "channel_id", "points", "lowest", "highest")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    LOWEST_FIELD_NUMBER: _ClassVar[int]
    HIGHEST_FIELD_NUMBER: _ClassVar[int]
    key: str
    label: str
    channel_id: int
    points: _containers.RepeatedCompositeFieldContainer[Point]
    lowest: float
    highest: float
    def __init__(self, key: _Optional[str] = ..., label: _Optional[str] = ..., channel_id: _Optional[int] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., lowest: _Optional[float] = ..., highest: _Optional[float] = ...) -> None: ...

class TimelineView(_message.Message):
    __slots__ = ("window", "recorded", "curves", "lanes", "is_empty")
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    RECORDED_FIELD_NUMBER: _ClassVar[int]
    CURVES_FIELD_NUMBER: _ClassVar[int]
    LANES_FIELD_NUMBER: _ClassVar[int]
    IS_EMPTY_FIELD_NUMBER: _ClassVar[int]
    window: WindowView
    recorded: WindowView
    curves: _containers.RepeatedCompositeFieldContainer[CurveView]
    lanes: _containers.RepeatedCompositeFieldContainer[LaneView]
    is_empty: bool
    def __init__(self, window: _Optional[_Union[WindowView, _Mapping]] = ..., recorded: _Optional[_Union[WindowView, _Mapping]] = ..., curves: _Optional[_Iterable[_Union[CurveView, _Mapping]]] = ..., lanes: _Optional[_Iterable[_Union[LaneView, _Mapping]]] = ..., is_empty: _Optional[bool] = ...) -> None: ...

class Following(_message.Message):
    __slots__ = ("wanted",)
    WANTED_FIELD_NUMBER: _ClassVar[int]
    wanted: bool
    def __init__(self, wanted: _Optional[bool] = ...) -> None: ...

class TimeStep(_message.Message):
    __slots__ = ("microseconds",)
    MICROSECONDS_FIELD_NUMBER: _ClassVar[int]
    microseconds: int
    def __init__(self, microseconds: _Optional[int] = ...) -> None: ...

class TimelineRequest(_message.Message):
    __slots__ = ("window_seconds",)
    WINDOW_SECONDS_FIELD_NUMBER: _ClassVar[int]
    window_seconds: float
    def __init__(self, window_seconds: _Optional[float] = ...) -> None: ...

class CallTimingView(_message.Message):
    __slots__ = ("function", "calls", "answered_calls", "total_seconds", "mean", "longest", "is_never_answered", "bands", "shape", "origin")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    ANSWERED_CALLS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MEAN_FIELD_NUMBER: _ClassVar[int]
    LONGEST_FIELD_NUMBER: _ClassVar[int]
    IS_NEVER_ANSWERED_FIELD_NUMBER: _ClassVar[int]
    BANDS_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    function: str
    calls: int
    answered_calls: int
    total_seconds: float
    mean: str
    longest: str
    is_never_answered: bool
    bands: _containers.RepeatedScalarFieldContainer[int]
    shape: str
    origin: str
    def __init__(self, function: _Optional[str] = ..., calls: _Optional[int] = ..., answered_calls: _Optional[int] = ..., total_seconds: _Optional[float] = ..., mean: _Optional[str] = ..., longest: _Optional[str] = ..., is_never_answered: _Optional[bool] = ..., bands: _Optional[_Iterable[int]] = ..., shape: _Optional[str] = ..., origin: _Optional[str] = ...) -> None: ...

class TimingReportView(_message.Message):
    __slots__ = ("entries", "heaviest_seconds")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    HEAVIEST_SECONDS_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[CallTimingView]
    heaviest_seconds: float
    def __init__(self, entries: _Optional[_Iterable[_Union[CallTimingView, _Mapping]]] = ..., heaviest_seconds: _Optional[float] = ...) -> None: ...

class ProfileEntryView(_message.Message):
    __slots__ = ("name", "origin", "directory", "file_name", "calls", "self_nanoseconds", "total_nanoseconds", "self_text", "total_text", "mean_text", "longest_text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    SELF_NANOSECONDS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NANOSECONDS_FIELD_NUMBER: _ClassVar[int]
    SELF_TEXT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TEXT_FIELD_NUMBER: _ClassVar[int]
    MEAN_TEXT_FIELD_NUMBER: _ClassVar[int]
    LONGEST_TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    origin: str
    directory: str
    file_name: str
    calls: int
    self_nanoseconds: int
    total_nanoseconds: int
    self_text: str
    total_text: str
    mean_text: str
    longest_text: str
    def __init__(self, name: _Optional[str] = ..., origin: _Optional[str] = ..., directory: _Optional[str] = ..., file_name: _Optional[str] = ..., calls: _Optional[int] = ..., self_nanoseconds: _Optional[int] = ..., total_nanoseconds: _Optional[int] = ..., self_text: _Optional[str] = ..., total_text: _Optional[str] = ..., mean_text: _Optional[str] = ..., longest_text: _Optional[str] = ...) -> None: ...

class ProfileGroupView(_message.Message):
    __slots__ = ("label", "calls", "self_nanoseconds", "self_text", "share", "share_text", "children", "entry")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    SELF_NANOSECONDS_FIELD_NUMBER: _ClassVar[int]
    SELF_TEXT_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    SHARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    label: str
    calls: int
    self_nanoseconds: int
    self_text: str
    share: float
    share_text: str
    children: _containers.RepeatedCompositeFieldContainer[ProfileGroupView]
    entry: ProfileEntryView
    def __init__(self, label: _Optional[str] = ..., calls: _Optional[int] = ..., self_nanoseconds: _Optional[int] = ..., self_text: _Optional[str] = ..., share: _Optional[float] = ..., share_text: _Optional[str] = ..., children: _Optional[_Iterable[_Union[ProfileGroupView, _Mapping]]] = ..., entry: _Optional[_Union[ProfileEntryView, _Mapping]] = ...) -> None: ...

class ProfileView(_message.Message):
    __slots__ = ("groups", "heaviest", "measured_nanoseconds", "measured_text", "lost_functions", "is_profiling", "note")
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    HEAVIEST_FIELD_NUMBER: _ClassVar[int]
    MEASURED_NANOSECONDS_FIELD_NUMBER: _ClassVar[int]
    MEASURED_TEXT_FIELD_NUMBER: _ClassVar[int]
    LOST_FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    IS_PROFILING_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[ProfileGroupView]
    heaviest: _containers.RepeatedCompositeFieldContainer[ProfileEntryView]
    measured_nanoseconds: int
    measured_text: str
    lost_functions: int
    is_profiling: bool
    note: str
    def __init__(self, groups: _Optional[_Iterable[_Union[ProfileGroupView, _Mapping]]] = ..., heaviest: _Optional[_Iterable[_Union[ProfileEntryView, _Mapping]]] = ..., measured_nanoseconds: _Optional[int] = ..., measured_text: _Optional[str] = ..., lost_functions: _Optional[int] = ..., is_profiling: _Optional[bool] = ..., note: _Optional[str] = ...) -> None: ...

class FrameView(_message.Message):
    __slots__ = ("name", "origin", "depth", "start", "width", "calls", "total", "own", "share", "caption")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    OWN_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    origin: str
    depth: int
    start: float
    width: float
    calls: int
    total: str
    own: str
    share: float
    caption: str
    def __init__(self, name: _Optional[str] = ..., origin: _Optional[str] = ..., depth: _Optional[int] = ..., start: _Optional[float] = ..., width: _Optional[float] = ..., calls: _Optional[int] = ..., total: _Optional[str] = ..., own: _Optional[str] = ..., share: _Optional[float] = ..., caption: _Optional[str] = ...) -> None: ...

class FlameView(_message.Message):
    __slots__ = ("frames", "depth", "total", "note", "is_watched")
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    IS_WATCHED_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[FrameView]
    depth: int
    total: str
    note: str
    is_watched: bool
    def __init__(self, frames: _Optional[_Iterable[_Union[FrameView, _Mapping]]] = ..., depth: _Optional[int] = ..., total: _Optional[str] = ..., note: _Optional[str] = ..., is_watched: _Optional[bool] = ...) -> None: ...

class StaticObjectView(_message.Message):
    __slots__ = ("name", "origin", "directory", "file_name", "bytes_used", "size_text", "is_constant")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    BYTES_USED_FIELD_NUMBER: _ClassVar[int]
    SIZE_TEXT_FIELD_NUMBER: _ClassVar[int]
    IS_CONSTANT_FIELD_NUMBER: _ClassVar[int]
    name: str
    origin: str
    directory: str
    file_name: str
    bytes_used: int
    size_text: str
    is_constant: bool
    def __init__(self, name: _Optional[str] = ..., origin: _Optional[str] = ..., directory: _Optional[str] = ..., file_name: _Optional[str] = ..., bytes_used: _Optional[int] = ..., size_text: _Optional[str] = ..., is_constant: _Optional[bool] = ...) -> None: ...

class DirectoryShare(_message.Message):
    __slots__ = ("directory", "size_text")
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    SIZE_TEXT_FIELD_NUMBER: _ClassVar[int]
    directory: str
    size_text: str
    def __init__(self, directory: _Optional[str] = ..., size_text: _Optional[str] = ...) -> None: ...

class StaticMemoryView(_message.Message):
    __slots__ = ("biggest", "by_directory", "object_count", "total_bytes", "writable_bytes", "firmware_bytes", "budget_bytes", "is_within_budget", "total_text", "writable_text", "firmware_text", "summary")
    BIGGEST_FIELD_NUMBER: _ClassVar[int]
    BY_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    OBJECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    WRITABLE_BYTES_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_BYTES_FIELD_NUMBER: _ClassVar[int]
    BUDGET_BYTES_FIELD_NUMBER: _ClassVar[int]
    IS_WITHIN_BUDGET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TEXT_FIELD_NUMBER: _ClassVar[int]
    WRITABLE_TEXT_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    biggest: _containers.RepeatedCompositeFieldContainer[StaticObjectView]
    by_directory: _containers.RepeatedCompositeFieldContainer[DirectoryShare]
    object_count: int
    total_bytes: int
    writable_bytes: int
    firmware_bytes: int
    budget_bytes: int
    is_within_budget: bool
    total_text: str
    writable_text: str
    firmware_text: str
    summary: str
    def __init__(self, biggest: _Optional[_Iterable[_Union[StaticObjectView, _Mapping]]] = ..., by_directory: _Optional[_Iterable[_Union[DirectoryShare, _Mapping]]] = ..., object_count: _Optional[int] = ..., total_bytes: _Optional[int] = ..., writable_bytes: _Optional[int] = ..., firmware_bytes: _Optional[int] = ..., budget_bytes: _Optional[int] = ..., is_within_budget: _Optional[bool] = ..., total_text: _Optional[str] = ..., writable_text: _Optional[str] = ..., firmware_text: _Optional[str] = ..., summary: _Optional[str] = ...) -> None: ...

class StackFrameView(_message.Message):
    __slots__ = ("function", "origin", "file_name", "bytes_used", "size_text")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    BYTES_USED_FIELD_NUMBER: _ClassVar[int]
    SIZE_TEXT_FIELD_NUMBER: _ClassVar[int]
    function: str
    origin: str
    file_name: str
    bytes_used: int
    size_text: str
    def __init__(self, function: _Optional[str] = ..., origin: _Optional[str] = ..., file_name: _Optional[str] = ..., bytes_used: _Optional[int] = ..., size_text: _Optional[str] = ...) -> None: ...

class StackUsageView(_message.Message):
    __slots__ = ("path", "largest", "deepest_bytes", "deepest_depth", "deepest_text", "path_is_complete", "is_measured", "summary")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LARGEST_FIELD_NUMBER: _ClassVar[int]
    DEEPEST_BYTES_FIELD_NUMBER: _ClassVar[int]
    DEEPEST_DEPTH_FIELD_NUMBER: _ClassVar[int]
    DEEPEST_TEXT_FIELD_NUMBER: _ClassVar[int]
    PATH_IS_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    IS_MEASURED_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    path: _containers.RepeatedCompositeFieldContainer[StackFrameView]
    largest: _containers.RepeatedCompositeFieldContainer[StackFrameView]
    deepest_bytes: int
    deepest_depth: int
    deepest_text: str
    path_is_complete: bool
    is_measured: bool
    summary: str
    def __init__(self, path: _Optional[_Iterable[_Union[StackFrameView, _Mapping]]] = ..., largest: _Optional[_Iterable[_Union[StackFrameView, _Mapping]]] = ..., deepest_bytes: _Optional[int] = ..., deepest_depth: _Optional[int] = ..., deepest_text: _Optional[str] = ..., path_is_complete: _Optional[bool] = ..., is_measured: _Optional[bool] = ..., summary: _Optional[str] = ...) -> None: ...

class AllocationSiteView(_message.Message):
    __slots__ = ("function", "origin", "file_name", "blocks", "bytes_used", "size_text")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    BLOCKS_FIELD_NUMBER: _ClassVar[int]
    BYTES_USED_FIELD_NUMBER: _ClassVar[int]
    SIZE_TEXT_FIELD_NUMBER: _ClassVar[int]
    function: str
    origin: str
    file_name: str
    blocks: int
    bytes_used: int
    size_text: str
    def __init__(self, function: _Optional[str] = ..., origin: _Optional[str] = ..., file_name: _Optional[str] = ..., blocks: _Optional[int] = ..., bytes_used: _Optional[int] = ..., size_text: _Optional[str] = ...) -> None: ...

class HeapUsageView(_message.Message):
    __slots__ = ("outstanding", "allocations", "frees", "failures", "live_text", "peak_text", "firmware_text", "untracked_blocks", "never_allocated", "is_watched", "summary", "live_bytes", "peak_bytes")
    OUTSTANDING_FIELD_NUMBER: _ClassVar[int]
    ALLOCATIONS_FIELD_NUMBER: _ClassVar[int]
    FREES_FIELD_NUMBER: _ClassVar[int]
    FAILURES_FIELD_NUMBER: _ClassVar[int]
    LIVE_TEXT_FIELD_NUMBER: _ClassVar[int]
    PEAK_TEXT_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    UNTRACKED_BLOCKS_FIELD_NUMBER: _ClassVar[int]
    NEVER_ALLOCATED_FIELD_NUMBER: _ClassVar[int]
    IS_WATCHED_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    LIVE_BYTES_FIELD_NUMBER: _ClassVar[int]
    PEAK_BYTES_FIELD_NUMBER: _ClassVar[int]
    outstanding: _containers.RepeatedCompositeFieldContainer[AllocationSiteView]
    allocations: int
    frees: int
    failures: int
    live_text: str
    peak_text: str
    firmware_text: str
    untracked_blocks: int
    never_allocated: bool
    is_watched: bool
    summary: str
    live_bytes: int
    peak_bytes: int
    def __init__(self, outstanding: _Optional[_Iterable[_Union[AllocationSiteView, _Mapping]]] = ..., allocations: _Optional[int] = ..., frees: _Optional[int] = ..., failures: _Optional[int] = ..., live_text: _Optional[str] = ..., peak_text: _Optional[str] = ..., firmware_text: _Optional[str] = ..., untracked_blocks: _Optional[int] = ..., never_allocated: _Optional[bool] = ..., is_watched: _Optional[bool] = ..., summary: _Optional[str] = ..., live_bytes: _Optional[int] = ..., peak_bytes: _Optional[int] = ...) -> None: ...

class MemoryView(_message.Message):
    __slots__ = ("static_memory", "stack", "heap")
    STATIC_MEMORY_FIELD_NUMBER: _ClassVar[int]
    STACK_FIELD_NUMBER: _ClassVar[int]
    HEAP_FIELD_NUMBER: _ClassVar[int]
    static_memory: StaticMemoryView
    stack: StackUsageView
    heap: HeapUsageView
    def __init__(self, static_memory: _Optional[_Union[StaticMemoryView, _Mapping]] = ..., stack: _Optional[_Union[StackUsageView, _Mapping]] = ..., heap: _Optional[_Union[HeapUsageView, _Mapping]] = ...) -> None: ...
