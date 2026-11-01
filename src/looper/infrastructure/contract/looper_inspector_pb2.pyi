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

class Refusal(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REFUSAL_NONE: _ClassVar[Refusal]
    REFUSAL_LATE: _ClassVar[Refusal]
    REFUSAL_UNKNOWN_TARGET: _ClassVar[Refusal]
    REFUSAL_NOT_ACCEPTED: _ClassVar[Refusal]
    REFUSAL_QUEUE_FULL: _ClassVar[Refusal]
    REFUSAL_WRONG_EPOCH: _ClassVar[Refusal]
    REFUSAL_INVALID: _ClassVar[Refusal]
    REFUSAL_WRONG_MODE: _ClassVar[Refusal]
    REFUSAL_OTHER: _ClassVar[Refusal]

class Capability(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAPABILITY_UNSPECIFIED: _ClassVar[Capability]
    CAPABILITY_PACED: _ClassVar[Capability]
    CAPABILITY_JOBS: _ClassVar[Capability]
    CAPABILITY_BUS_TIME: _ClassVar[Capability]
    CAPABILITY_REPLY_RULES: _ClassVar[Capability]
    CAPABILITY_DEVICE_ACTIONS: _ClassVar[Capability]
    CAPABILITY_SOURCES: _ClassVar[Capability]
    CAPABILITY_LINE_COUNTS: _ClassVar[Capability]
    CAPABILITY_DEBUGGER: _ClassVar[Capability]
    CAPABILITY_LEVELS: _ClassVar[Capability]
    CAPABILITY_READ_BY_TIME: _ClassVar[Capability]

class ClockMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLOCK_MODE_HELD: _ClassVar[ClockMode]
    CLOCK_MODE_PACED: _ClassVar[ClockMode]
    CLOCK_MODE_MAX: _ClassVar[ClockMode]

class EventKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_KIND_UNSPECIFIED: _ClassVar[EventKind]
    EVENT_KIND_SAMPLE: _ClassVar[EventKind]
    EVENT_KIND_PIN: _ClassVar[EventKind]
    EVENT_KIND_EXCHANGE: _ClassVar[EventKind]
    EVENT_KIND_CALL: _ClassVar[EventKind]
    EVENT_KIND_COMMAND: _ClassVar[EventKind]
    EVENT_KIND_JOB: _ClassVar[EventKind]
    EVENT_KIND_FAULT: _ClassVar[EventKind]
    EVENT_KIND_RUN: _ClassVar[EventKind]

class LossReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOSS_REASON_UNSPECIFIED: _ClassVar[LossReason]
    LOSS_REASON_RING_FULL: _ClassVar[LossReason]
    LOSS_REASON_CLIENT_TOO_SLOW: _ClassVar[LossReason]
    LOSS_REASON_RETENTION: _ClassVar[LossReason]

class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_UNSPECIFIED: _ClassVar[Direction]
    DIRECTION_OUTBOUND: _ClassVar[Direction]
    DIRECTION_INBOUND: _ClassVar[Direction]

class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOURCE_FIRMWARE: _ClassVar[Source]
    SOURCE_CLIENT: _ClassVar[Source]
    SOURCE_JOB: _ClassVar[Source]
    SOURCE_RULE: _ClassVar[Source]
    SOURCE_COMPONENT: _ClassVar[Source]

class ExchangeUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXCHANGE_UNIT_UNSPECIFIED: _ClassVar[ExchangeUnit]
    EXCHANGE_UNIT_BYTE: _ClassVar[ExchangeUnit]
    EXCHANGE_UNIT_WRITE: _ClassVar[ExchangeUnit]
    EXCHANGE_UNIT_LINE: _ClassVar[ExchangeUnit]
    EXCHANGE_UNIT_FRAME: _ClassVar[ExchangeUnit]
    EXCHANGE_UNIT_TRANSACTION: _ClassVar[ExchangeUnit]

class SourceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOURCE_STATE_AS_BUILT: _ClassVar[SourceState]
    SOURCE_STATE_CHANGED: _ClassVar[SourceState]
    SOURCE_STATE_MISSING: _ClassVar[SourceState]
    SOURCE_STATE_UNKEPT: _ClassVar[SourceState]

class SymbolKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SYMBOL_KIND_UNSPECIFIED: _ClassVar[SymbolKind]
    SYMBOL_KIND_FUNCTION: _ClassVar[SymbolKind]
    SYMBOL_KIND_ADAPTER_CALL: _ClassVar[SymbolKind]
    SYMBOL_KIND_GLOBAL_VARIABLE: _ClassVar[SymbolKind]
    SYMBOL_KIND_STATIC_VARIABLE: _ClassVar[SymbolKind]
    SYMBOL_KIND_LOCAL_VARIABLE: _ClassVar[SymbolKind]
    SYMBOL_KIND_PARAMETER: _ClassVar[SymbolKind]
    SYMBOL_KIND_FIELD: _ClassVar[SymbolKind]
    SYMBOL_KIND_MACRO: _ClassVar[SymbolKind]
    SYMBOL_KIND_ENUM_CONSTANT: _ClassVar[SymbolKind]
    SYMBOL_KIND_TYPE: _ClassVar[SymbolKind]

class RestartPhase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESTART_PHASE_RUNNING: _ClassVar[RestartPhase]
    RESTART_PHASE_BUILDING: _ClassVar[RestartPhase]
    RESTART_PHASE_RESTARTING: _ClassVar[RestartPhase]
CONTRACT_VERSION_UNSPECIFIED: ContractVersion
CONTRACT_VERSION_CURRENT: ContractVersion
REFUSAL_NONE: Refusal
REFUSAL_LATE: Refusal
REFUSAL_UNKNOWN_TARGET: Refusal
REFUSAL_NOT_ACCEPTED: Refusal
REFUSAL_QUEUE_FULL: Refusal
REFUSAL_WRONG_EPOCH: Refusal
REFUSAL_INVALID: Refusal
REFUSAL_WRONG_MODE: Refusal
REFUSAL_OTHER: Refusal
CAPABILITY_UNSPECIFIED: Capability
CAPABILITY_PACED: Capability
CAPABILITY_JOBS: Capability
CAPABILITY_BUS_TIME: Capability
CAPABILITY_REPLY_RULES: Capability
CAPABILITY_DEVICE_ACTIONS: Capability
CAPABILITY_SOURCES: Capability
CAPABILITY_LINE_COUNTS: Capability
CAPABILITY_DEBUGGER: Capability
CAPABILITY_LEVELS: Capability
CAPABILITY_READ_BY_TIME: Capability
CLOCK_MODE_HELD: ClockMode
CLOCK_MODE_PACED: ClockMode
CLOCK_MODE_MAX: ClockMode
EVENT_KIND_UNSPECIFIED: EventKind
EVENT_KIND_SAMPLE: EventKind
EVENT_KIND_PIN: EventKind
EVENT_KIND_EXCHANGE: EventKind
EVENT_KIND_CALL: EventKind
EVENT_KIND_COMMAND: EventKind
EVENT_KIND_JOB: EventKind
EVENT_KIND_FAULT: EventKind
EVENT_KIND_RUN: EventKind
LOSS_REASON_UNSPECIFIED: LossReason
LOSS_REASON_RING_FULL: LossReason
LOSS_REASON_CLIENT_TOO_SLOW: LossReason
LOSS_REASON_RETENTION: LossReason
DIRECTION_UNSPECIFIED: Direction
DIRECTION_OUTBOUND: Direction
DIRECTION_INBOUND: Direction
SOURCE_FIRMWARE: Source
SOURCE_CLIENT: Source
SOURCE_JOB: Source
SOURCE_RULE: Source
SOURCE_COMPONENT: Source
EXCHANGE_UNIT_UNSPECIFIED: ExchangeUnit
EXCHANGE_UNIT_BYTE: ExchangeUnit
EXCHANGE_UNIT_WRITE: ExchangeUnit
EXCHANGE_UNIT_LINE: ExchangeUnit
EXCHANGE_UNIT_FRAME: ExchangeUnit
EXCHANGE_UNIT_TRANSACTION: ExchangeUnit
SOURCE_STATE_AS_BUILT: SourceState
SOURCE_STATE_CHANGED: SourceState
SOURCE_STATE_MISSING: SourceState
SOURCE_STATE_UNKEPT: SourceState
SYMBOL_KIND_UNSPECIFIED: SymbolKind
SYMBOL_KIND_FUNCTION: SymbolKind
SYMBOL_KIND_ADAPTER_CALL: SymbolKind
SYMBOL_KIND_GLOBAL_VARIABLE: SymbolKind
SYMBOL_KIND_STATIC_VARIABLE: SymbolKind
SYMBOL_KIND_LOCAL_VARIABLE: SymbolKind
SYMBOL_KIND_PARAMETER: SymbolKind
SYMBOL_KIND_FIELD: SymbolKind
SYMBOL_KIND_MACRO: SymbolKind
SYMBOL_KIND_ENUM_CONSTANT: SymbolKind
SYMBOL_KIND_TYPE: SymbolKind
RESTART_PHASE_RUNNING: RestartPhase
RESTART_PHASE_BUILDING: RestartPhase
RESTART_PHASE_RESTARTING: RestartPhase

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Ack(_message.Message):
    __slots__ = ("command_seq", "applied_at_us", "pending", "epoch", "refusal", "refusal_text", "late_by_us")
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    APPLIED_AT_US_FIELD_NUMBER: _ClassVar[int]
    PENDING_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    REFUSAL_FIELD_NUMBER: _ClassVar[int]
    REFUSAL_TEXT_FIELD_NUMBER: _ClassVar[int]
    LATE_BY_US_FIELD_NUMBER: _ClassVar[int]
    command_seq: int
    applied_at_us: int
    pending: bool
    epoch: int
    refusal: Refusal
    refusal_text: str
    late_by_us: int
    def __init__(self, command_seq: _Optional[int] = ..., applied_at_us: _Optional[int] = ..., pending: _Optional[bool] = ..., epoch: _Optional[int] = ..., refusal: _Optional[_Union[Refusal, str]] = ..., refusal_text: _Optional[str] = ..., late_by_us: _Optional[int] = ...) -> None: ...

class When(_message.Message):
    __slots__ = ("at_us", "after_us", "allow_late")
    AT_US_FIELD_NUMBER: _ClassVar[int]
    AFTER_US_FIELD_NUMBER: _ClassVar[int]
    ALLOW_LATE_FIELD_NUMBER: _ClassVar[int]
    at_us: int
    after_us: int
    allow_late: bool
    def __init__(self, at_us: _Optional[int] = ..., after_us: _Optional[int] = ..., allow_late: _Optional[bool] = ...) -> None: ...

class Description(_message.Message):
    __slots__ = ("contract_version", "firmware_name", "reads_the_build", "definition_path", "capabilities", "retention_us", "max_events_per_batch")
    CONTRACT_VERSION_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_NAME_FIELD_NUMBER: _ClassVar[int]
    READS_THE_BUILD_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_PATH_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    RETENTION_US_FIELD_NUMBER: _ClassVar[int]
    MAX_EVENTS_PER_BATCH_FIELD_NUMBER: _ClassVar[int]
    contract_version: ContractVersion
    firmware_name: str
    reads_the_build: bool
    definition_path: str
    capabilities: _containers.RepeatedScalarFieldContainer[Capability]
    retention_us: int
    max_events_per_batch: int
    def __init__(self, contract_version: _Optional[_Union[ContractVersion, str]] = ..., firmware_name: _Optional[str] = ..., reads_the_build: _Optional[bool] = ..., definition_path: _Optional[str] = ..., capabilities: _Optional[_Iterable[_Union[Capability, str]]] = ..., retention_us: _Optional[int] = ..., max_events_per_batch: _Optional[int] = ...) -> None: ...

class RunControl(_message.Message):
    __slots__ = ("hold", "run_for_us", "run_until_us", "step_pass", "pace_ratio", "max_speed")
    HOLD_FIELD_NUMBER: _ClassVar[int]
    RUN_FOR_US_FIELD_NUMBER: _ClassVar[int]
    RUN_UNTIL_US_FIELD_NUMBER: _ClassVar[int]
    STEP_PASS_FIELD_NUMBER: _ClassVar[int]
    PACE_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    hold: Empty
    run_for_us: int
    run_until_us: int
    step_pass: Empty
    pace_ratio: float
    max_speed: Empty
    def __init__(self, hold: _Optional[_Union[Empty, _Mapping]] = ..., run_for_us: _Optional[int] = ..., run_until_us: _Optional[int] = ..., step_pass: _Optional[_Union[Empty, _Mapping]] = ..., pace_ratio: _Optional[float] = ..., max_speed: _Optional[_Union[Empty, _Mapping]] = ...) -> None: ...

class RunReply(_message.Message):
    __slots__ = ("ack", "state")
    ACK_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    state: RunState
    def __init__(self, ack: _Optional[_Union[Ack, _Mapping]] = ..., state: _Optional[_Union[RunState, _Mapping]] = ...) -> None: ...

class RunState(_message.Message):
    __slots__ = ("now_us", "mode", "pace_ratio", "behind_us", "slipped_us", "epoch", "next_event_seq", "pass_cost_us", "target_us", "queued_commands", "hold_reason")
    NOW_US_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    PACE_RATIO_FIELD_NUMBER: _ClassVar[int]
    BEHIND_US_FIELD_NUMBER: _ClassVar[int]
    SLIPPED_US_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    NEXT_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    PASS_COST_US_FIELD_NUMBER: _ClassVar[int]
    TARGET_US_FIELD_NUMBER: _ClassVar[int]
    QUEUED_COMMANDS_FIELD_NUMBER: _ClassVar[int]
    HOLD_REASON_FIELD_NUMBER: _ClassVar[int]
    now_us: int
    mode: ClockMode
    pace_ratio: float
    behind_us: int
    slipped_us: int
    epoch: int
    next_event_seq: int
    pass_cost_us: int
    target_us: int
    queued_commands: int
    hold_reason: str
    def __init__(self, now_us: _Optional[int] = ..., mode: _Optional[_Union[ClockMode, str]] = ..., pace_ratio: _Optional[float] = ..., behind_us: _Optional[int] = ..., slipped_us: _Optional[int] = ..., epoch: _Optional[int] = ..., next_event_seq: _Optional[int] = ..., pass_cost_us: _Optional[int] = ..., target_us: _Optional[int] = ..., queued_commands: _Optional[int] = ..., hold_reason: _Optional[str] = ...) -> None: ...

class Subscription(_message.Message):
    __slots__ = ("epoch", "from_event_seq", "filter", "with_levels")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    FROM_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    WITH_LEVELS_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    from_event_seq: int
    filter: EventFilter
    with_levels: bool
    def __init__(self, epoch: _Optional[int] = ..., from_event_seq: _Optional[int] = ..., filter: _Optional[_Union[EventFilter, _Mapping]] = ..., with_levels: _Optional[bool] = ...) -> None: ...

class ReadEventsRequest(_message.Message):
    __slots__ = ("epoch", "from_event_seq", "max_events", "filter", "with_levels", "from_us", "to_us")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    FROM_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    MAX_EVENTS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    WITH_LEVELS_FIELD_NUMBER: _ClassVar[int]
    FROM_US_FIELD_NUMBER: _ClassVar[int]
    TO_US_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    from_event_seq: int
    max_events: int
    filter: EventFilter
    with_levels: bool
    from_us: int
    to_us: int
    def __init__(self, epoch: _Optional[int] = ..., from_event_seq: _Optional[int] = ..., max_events: _Optional[int] = ..., filter: _Optional[_Union[EventFilter, _Mapping]] = ..., with_levels: _Optional[bool] = ..., from_us: _Optional[int] = ..., to_us: _Optional[int] = ...) -> None: ...

class EventFilter(_message.Message):
    __slots__ = ("kinds", "channel_ids", "bus_ids", "sample_stride", "pin_ids", "call_functions")
    KINDS_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_IDS_FIELD_NUMBER: _ClassVar[int]
    BUS_IDS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_STRIDE_FIELD_NUMBER: _ClassVar[int]
    PIN_IDS_FIELD_NUMBER: _ClassVar[int]
    CALL_FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    kinds: _containers.RepeatedScalarFieldContainer[EventKind]
    channel_ids: _containers.RepeatedScalarFieldContainer[int]
    bus_ids: _containers.RepeatedScalarFieldContainer[int]
    sample_stride: int
    pin_ids: _containers.RepeatedScalarFieldContainer[int]
    call_functions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, kinds: _Optional[_Iterable[_Union[EventKind, str]]] = ..., channel_ids: _Optional[_Iterable[int]] = ..., bus_ids: _Optional[_Iterable[int]] = ..., sample_stride: _Optional[int] = ..., pin_ids: _Optional[_Iterable[int]] = ..., call_functions: _Optional[_Iterable[str]] = ...) -> None: ...

class EventBatch(_message.Message):
    __slots__ = ("epoch", "events", "lost", "next_event_seq", "sim_now_us", "epoch_changed", "levels")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    LOST_FIELD_NUMBER: _ClassVar[int]
    NEXT_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    SIM_NOW_US_FIELD_NUMBER: _ClassVar[int]
    EPOCH_CHANGED_FIELD_NUMBER: _ClassVar[int]
    LEVELS_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    events: _containers.RepeatedCompositeFieldContainer[Event]
    lost: _containers.RepeatedCompositeFieldContainer[Lost]
    next_event_seq: int
    sim_now_us: int
    epoch_changed: bool
    levels: LevelsBefore
    def __init__(self, epoch: _Optional[int] = ..., events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ..., lost: _Optional[_Iterable[_Union[Lost, _Mapping]]] = ..., next_event_seq: _Optional[int] = ..., sim_now_us: _Optional[int] = ..., epoch_changed: _Optional[bool] = ..., levels: _Optional[_Union[LevelsBefore, _Mapping]] = ...) -> None: ...

class LevelsBefore(_message.Message):
    __slots__ = ("before_event_seq", "pins", "channels")
    BEFORE_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    PINS_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    before_event_seq: int
    pins: _containers.RepeatedCompositeFieldContainer[PinLevelSince]
    channels: _containers.RepeatedCompositeFieldContainer[ChannelValueSince]
    def __init__(self, before_event_seq: _Optional[int] = ..., pins: _Optional[_Iterable[_Union[PinLevelSince, _Mapping]]] = ..., channels: _Optional[_Iterable[_Union[ChannelValueSince, _Mapping]]] = ...) -> None: ...

class PinLevelSince(_message.Message):
    __slots__ = ("pin_id", "high", "since_us")
    PIN_ID_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    SINCE_US_FIELD_NUMBER: _ClassVar[int]
    pin_id: int
    high: bool
    since_us: int
    def __init__(self, pin_id: _Optional[int] = ..., high: _Optional[bool] = ..., since_us: _Optional[int] = ...) -> None: ...

class ChannelValueSince(_message.Message):
    __slots__ = ("channel_id", "value", "since_us")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SINCE_US_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    value: float
    since_us: int
    def __init__(self, channel_id: _Optional[int] = ..., value: _Optional[float] = ..., since_us: _Optional[int] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("event_seq", "sim_us", "sample", "pin", "exchange", "call", "command", "job", "fault", "run")
    EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    CALL_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    FAULT_FIELD_NUMBER: _ClassVar[int]
    RUN_FIELD_NUMBER: _ClassVar[int]
    event_seq: int
    sim_us: int
    sample: Sample
    pin: PinChange
    exchange: Exchange
    call: Call
    command: CommandApplied
    job: JobEvent
    fault: Fault
    run: RunEvent
    def __init__(self, event_seq: _Optional[int] = ..., sim_us: _Optional[int] = ..., sample: _Optional[_Union[Sample, _Mapping]] = ..., pin: _Optional[_Union[PinChange, _Mapping]] = ..., exchange: _Optional[_Union[Exchange, _Mapping]] = ..., call: _Optional[_Union[Call, _Mapping]] = ..., command: _Optional[_Union[CommandApplied, _Mapping]] = ..., job: _Optional[_Union[JobEvent, _Mapping]] = ..., fault: _Optional[_Union[Fault, _Mapping]] = ..., run: _Optional[_Union[RunEvent, _Mapping]] = ...) -> None: ...

class Lost(_message.Message):
    __slots__ = ("from_event_seq", "to_event_seq", "from_us", "to_us", "reason")
    FROM_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    TO_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    FROM_US_FIELD_NUMBER: _ClassVar[int]
    TO_US_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    from_event_seq: int
    to_event_seq: int
    from_us: int
    to_us: int
    reason: LossReason
    def __init__(self, from_event_seq: _Optional[int] = ..., to_event_seq: _Optional[int] = ..., from_us: _Optional[int] = ..., to_us: _Optional[int] = ..., reason: _Optional[_Union[LossReason, str]] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("channel_id", "value")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    value: float
    def __init__(self, channel_id: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class PinChange(_message.Message):
    __slots__ = ("pin_id", "high", "source", "command_seq")
    PIN_ID_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    pin_id: int
    high: bool
    source: Source
    command_seq: int
    def __init__(self, pin_id: _Optional[int] = ..., high: _Optional[bool] = ..., source: _Optional[_Union[Source, str]] = ..., command_seq: _Optional[int] = ...) -> None: ...

class Call(_message.Message):
    __slots__ = ("function", "peripheral")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    PERIPHERAL_FIELD_NUMBER: _ClassVar[int]
    function: str
    peripheral: str
    def __init__(self, function: _Optional[str] = ..., peripheral: _Optional[str] = ...) -> None: ...

class Exchange(_message.Message):
    __slots__ = ("bus_id", "start_us", "end_us", "direction", "address_value", "payload", "response", "payload_length", "response_length", "accepted", "refusal", "source", "source_name", "source_id", "requested_at_us", "command_seq", "can", "uart", "i2c", "spi")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    START_US_FIELD_NUMBER: _ClassVar[int]
    END_US_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_VALUE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_LENGTH_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REFUSAL_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_AT_US_FIELD_NUMBER: _ClassVar[int]
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    CAN_FIELD_NUMBER: _ClassVar[int]
    UART_FIELD_NUMBER: _ClassVar[int]
    I2C_FIELD_NUMBER: _ClassVar[int]
    SPI_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    start_us: int
    end_us: int
    direction: Direction
    address_value: int
    payload: bytes
    response: bytes
    payload_length: int
    response_length: int
    accepted: bool
    refusal: Refusal
    source: Source
    source_name: str
    source_id: int
    requested_at_us: int
    command_seq: int
    can: CanDetail
    uart: UartDetail
    i2c: I2cDetail
    spi: SpiDetail
    def __init__(self, bus_id: _Optional[int] = ..., start_us: _Optional[int] = ..., end_us: _Optional[int] = ..., direction: _Optional[_Union[Direction, str]] = ..., address_value: _Optional[int] = ..., payload: _Optional[bytes] = ..., response: _Optional[bytes] = ..., payload_length: _Optional[int] = ..., response_length: _Optional[int] = ..., accepted: _Optional[bool] = ..., refusal: _Optional[_Union[Refusal, str]] = ..., source: _Optional[_Union[Source, str]] = ..., source_name: _Optional[str] = ..., source_id: _Optional[int] = ..., requested_at_us: _Optional[int] = ..., command_seq: _Optional[int] = ..., can: _Optional[_Union[CanDetail, _Mapping]] = ..., uart: _Optional[_Union[UartDetail, _Mapping]] = ..., i2c: _Optional[_Union[I2cDetail, _Mapping]] = ..., spi: _Optional[_Union[SpiDetail, _Mapping]] = ...) -> None: ...

class CanDetail(_message.Message):
    __slots__ = ("extended", "remote", "dlc", "fd", "brs", "esi", "error_frame")
    EXTENDED_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    DLC_FIELD_NUMBER: _ClassVar[int]
    FD_FIELD_NUMBER: _ClassVar[int]
    BRS_FIELD_NUMBER: _ClassVar[int]
    ESI_FIELD_NUMBER: _ClassVar[int]
    ERROR_FRAME_FIELD_NUMBER: _ClassVar[int]
    extended: bool
    remote: bool
    dlc: int
    fd: bool
    brs: bool
    esi: bool
    error_frame: bool
    def __init__(self, extended: _Optional[bool] = ..., remote: _Optional[bool] = ..., dlc: _Optional[int] = ..., fd: _Optional[bool] = ..., brs: _Optional[bool] = ..., esi: _Optional[bool] = ..., error_frame: _Optional[bool] = ...) -> None: ...

class UartDetail(_message.Message):
    __slots__ = ("error_kind",)
    ERROR_KIND_FIELD_NUMBER: _ClassVar[int]
    error_kind: str
    def __init__(self, error_kind: _Optional[str] = ...) -> None: ...

class I2cDetail(_message.Message):
    __slots__ = ("is_read", "acknowledged", "register", "repeated_start")
    IS_READ_FIELD_NUMBER: _ClassVar[int]
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    REGISTER_FIELD_NUMBER: _ClassVar[int]
    REPEATED_START_FIELD_NUMBER: _ClassVar[int]
    is_read: bool
    acknowledged: bool
    register: int
    repeated_start: bool
    def __init__(self, is_read: _Optional[bool] = ..., acknowledged: _Optional[bool] = ..., register: _Optional[int] = ..., repeated_start: _Optional[bool] = ...) -> None: ...

class SpiDetail(_message.Message):
    __slots__ = ("chip_select",)
    CHIP_SELECT_FIELD_NUMBER: _ClassVar[int]
    chip_select: int
    def __init__(self, chip_select: _Optional[int] = ...) -> None: ...

class CommandApplied(_message.Message):
    __slots__ = ("command_seq", "description", "encoded")
    COMMAND_SEQ_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENCODED_FIELD_NUMBER: _ClassVar[int]
    command_seq: int
    description: str
    encoded: bytes
    def __init__(self, command_seq: _Optional[int] = ..., description: _Optional[str] = ..., encoded: _Optional[bytes] = ...) -> None: ...

class JobEvent(_message.Message):
    __slots__ = ("job_id", "kind", "text")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STARTED: _ClassVar[JobEvent.Kind]
        STOPPED: _ClassVar[JobEvent.Kind]
        FINISHED: _ClassVar[JobEvent.Kind]
        REFUSED: _ClassVar[JobEvent.Kind]
        LATE: _ClassVar[JobEvent.Kind]
    STARTED: JobEvent.Kind
    STOPPED: JobEvent.Kind
    FINISHED: JobEvent.Kind
    REFUSED: JobEvent.Kind
    LATE: JobEvent.Kind
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    kind: JobEvent.Kind
    text: str
    def __init__(self, job_id: _Optional[int] = ..., kind: _Optional[_Union[JobEvent.Kind, str]] = ..., text: _Optional[str] = ...) -> None: ...

class Fault(_message.Message):
    __slots__ = ("source", "text")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    source: str
    text: str
    def __init__(self, source: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class RunEvent(_message.Message):
    __slots__ = ("kind", "amount_us", "mode")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REACHED: _ClassVar[RunEvent.Kind]
        HELD: _ClassVar[RunEvent.Kind]
        SLIPPED: _ClassVar[RunEvent.Kind]
        MODE_CHANGED: _ClassVar[RunEvent.Kind]
    REACHED: RunEvent.Kind
    HELD: RunEvent.Kind
    SLIPPED: RunEvent.Kind
    MODE_CHANGED: RunEvent.Kind
    KIND_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_US_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    kind: RunEvent.Kind
    amount_us: int
    mode: ClockMode
    def __init__(self, kind: _Optional[_Union[RunEvent.Kind, str]] = ..., amount_us: _Optional[int] = ..., mode: _Optional[_Union[ClockMode, str]] = ...) -> None: ...

class ClearRequest(_message.Message):
    __slots__ = ("epoch",)
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    def __init__(self, epoch: _Optional[int] = ...) -> None: ...

class PinDrive(_message.Message):
    __slots__ = ("pin_id", "high", "toggle", "when")
    PIN_ID_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    TOGGLE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    pin_id: int
    high: bool
    toggle: Empty
    when: When
    def __init__(self, pin_id: _Optional[int] = ..., high: _Optional[bool] = ..., toggle: _Optional[_Union[Empty, _Mapping]] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

class PinDriven(_message.Message):
    __slots__ = ("ack", "high")
    ACK_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    high: bool
    def __init__(self, ack: _Optional[_Union[Ack, _Mapping]] = ..., high: _Optional[bool] = ...) -> None: ...

class WatchStarted(_message.Message):
    __slots__ = ("watch", "ack")
    WATCH_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    watch: WatchView
    ack: Ack
    def __init__(self, watch: _Optional[_Union[WatchView, _Mapping]] = ..., ack: _Optional[_Union[Ack, _Mapping]] = ...) -> None: ...

class BusMessage(_message.Message):
    __slots__ = ("bus_id", "address", "payload", "extended", "dlc", "remote", "fd", "brs", "chunk_bytes", "byte_gap_us")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_FIELD_NUMBER: _ClassVar[int]
    DLC_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    FD_FIELD_NUMBER: _ClassVar[int]
    BRS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_BYTES_FIELD_NUMBER: _ClassVar[int]
    BYTE_GAP_US_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    address: int
    payload: bytes
    extended: bool
    dlc: int
    remote: bool
    fd: bool
    brs: bool
    chunk_bytes: int
    byte_gap_us: int
    def __init__(self, bus_id: _Optional[int] = ..., address: _Optional[int] = ..., payload: _Optional[bytes] = ..., extended: _Optional[bool] = ..., dlc: _Optional[int] = ..., remote: _Optional[bool] = ..., fd: _Optional[bool] = ..., brs: _Optional[bool] = ..., chunk_bytes: _Optional[int] = ..., byte_gap_us: _Optional[int] = ...) -> None: ...

class BusMessageRequest(_message.Message):
    __slots__ = ("message", "when")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    message: BusMessage
    when: When
    def __init__(self, message: _Optional[_Union[BusMessage, _Mapping]] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

class BusMessageReply(_message.Message):
    __slots__ = ("ack", "summary")
    ACK_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ack: Ack
    summary: str
    def __init__(self, ack: _Optional[_Union[Ack, _Mapping]] = ..., summary: _Optional[str] = ...) -> None: ...

class SendJob(_message.Message):
    __slots__ = ("name", "steps", "repeat", "start", "random_seed")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    REPEAT_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    RANDOM_SEED_FIELD_NUMBER: _ClassVar[int]
    name: str
    steps: _containers.RepeatedCompositeFieldContainer[SendStep]
    repeat: Repeat
    start: When
    random_seed: int
    def __init__(self, name: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[SendStep, _Mapping]]] = ..., repeat: _Optional[_Union[Repeat, _Mapping]] = ..., start: _Optional[_Union[When, _Mapping]] = ..., random_seed: _Optional[int] = ...) -> None: ...

class SendStep(_message.Message):
    __slots__ = ("after_us", "message", "counters", "checksums", "random_bytes")
    AFTER_US_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COUNTERS_FIELD_NUMBER: _ClassVar[int]
    CHECKSUMS_FIELD_NUMBER: _ClassVar[int]
    RANDOM_BYTES_FIELD_NUMBER: _ClassVar[int]
    after_us: int
    message: BusMessage
    counters: _containers.RepeatedCompositeFieldContainer[CounterField]
    checksums: _containers.RepeatedCompositeFieldContainer[ChecksumField]
    random_bytes: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, after_us: _Optional[int] = ..., message: _Optional[_Union[BusMessage, _Mapping]] = ..., counters: _Optional[_Iterable[_Union[CounterField, _Mapping]]] = ..., checksums: _Optional[_Iterable[_Union[ChecksumField, _Mapping]]] = ..., random_bytes: _Optional[_Iterable[int]] = ...) -> None: ...

class Repeat(_message.Message):
    __slots__ = ("times", "until_stopped", "period_us", "burst")
    TIMES_FIELD_NUMBER: _ClassVar[int]
    UNTIL_STOPPED_FIELD_NUMBER: _ClassVar[int]
    PERIOD_US_FIELD_NUMBER: _ClassVar[int]
    BURST_FIELD_NUMBER: _ClassVar[int]
    times: int
    until_stopped: bool
    period_us: int
    burst: int
    def __init__(self, times: _Optional[int] = ..., until_stopped: _Optional[bool] = ..., period_us: _Optional[int] = ..., burst: _Optional[int] = ...) -> None: ...

class CounterField(_message.Message):
    __slots__ = ("byte_offset", "width_bytes", "big_endian", "start", "step", "wrap")
    BYTE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    WIDTH_BYTES_FIELD_NUMBER: _ClassVar[int]
    BIG_ENDIAN_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    WRAP_FIELD_NUMBER: _ClassVar[int]
    byte_offset: int
    width_bytes: int
    big_endian: bool
    start: int
    step: int
    wrap: bool
    def __init__(self, byte_offset: _Optional[int] = ..., width_bytes: _Optional[int] = ..., big_endian: _Optional[bool] = ..., start: _Optional[int] = ..., step: _Optional[int] = ..., wrap: _Optional[bool] = ...) -> None: ...

class ChecksumField(_message.Message):
    __slots__ = ("byte_offset", "kind", "from_byte", "to_byte", "polynomial")
    BYTE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    FROM_BYTE_FIELD_NUMBER: _ClassVar[int]
    TO_BYTE_FIELD_NUMBER: _ClassVar[int]
    POLYNOMIAL_FIELD_NUMBER: _ClassVar[int]
    byte_offset: int
    kind: str
    from_byte: int
    to_byte: int
    polynomial: int
    def __init__(self, byte_offset: _Optional[int] = ..., kind: _Optional[str] = ..., from_byte: _Optional[int] = ..., to_byte: _Optional[int] = ..., polynomial: _Optional[int] = ...) -> None: ...

class JobChoice(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    def __init__(self, job_id: _Optional[int] = ...) -> None: ...

class JobView(_message.Message):
    __slots__ = ("job_id", "name", "state", "next_due_us", "sent", "late", "last_error", "ack", "started_at_us")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        WAITING: _ClassVar[JobView.State]
        RUNNING: _ClassVar[JobView.State]
        FINISHED: _ClassVar[JobView.State]
        STOPPED: _ClassVar[JobView.State]
        REFUSED: _ClassVar[JobView.State]
    WAITING: JobView.State
    RUNNING: JobView.State
    FINISHED: JobView.State
    STOPPED: JobView.State
    REFUSED: JobView.State
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    NEXT_DUE_US_FIELD_NUMBER: _ClassVar[int]
    SENT_FIELD_NUMBER: _ClassVar[int]
    LATE_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_US_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    name: str
    state: JobView.State
    next_due_us: int
    sent: int
    late: int
    last_error: str
    ack: Ack
    started_at_us: int
    def __init__(self, job_id: _Optional[int] = ..., name: _Optional[str] = ..., state: _Optional[_Union[JobView.State, str]] = ..., next_due_us: _Optional[int] = ..., sent: _Optional[int] = ..., late: _Optional[int] = ..., last_error: _Optional[str] = ..., ack: _Optional[_Union[Ack, _Mapping]] = ..., started_at_us: _Optional[int] = ...) -> None: ...

class JobList(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobView]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobView, _Mapping]]] = ...) -> None: ...

class CurvePoint(_message.Message):
    __slots__ = ("sim_us", "value")
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    sim_us: int
    value: float
    def __init__(self, sim_us: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class GapPoint(_message.Message):
    __slots__ = ("sim_us", "gap_us")
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    GAP_US_FIELD_NUMBER: _ClassVar[int]
    sim_us: int
    gap_us: int
    def __init__(self, sim_us: _Optional[int] = ..., gap_us: _Optional[int] = ...) -> None: ...

class ViewPosition(_message.Message):
    __slots__ = ("epoch", "as_of_event_seq")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    AS_OF_EVENT_SEQ_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    as_of_event_seq: int
    def __init__(self, epoch: _Optional[int] = ..., as_of_event_seq: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("sim_us", "pins")
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    PINS_FIELD_NUMBER: _ClassVar[int]
    sim_us: int
    pins: _containers.RepeatedCompositeFieldContainer[PinView]
    def __init__(self, sim_us: _Optional[int] = ..., pins: _Optional[_Iterable[_Union[PinView, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("channel_id", "name", "unit", "direction", "value", "is_drivable", "signal", "is_silent", "display_value", "is_driven_by_graph")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_DRIVABLE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    IS_SILENT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_DRIVEN_BY_GRAPH_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    name: str
    unit: str
    direction: str
    value: float
    is_drivable: bool
    signal: SignalView
    is_silent: bool
    display_value: str
    is_driven_by_graph: bool
    def __init__(self, channel_id: _Optional[int] = ..., name: _Optional[str] = ..., unit: _Optional[str] = ..., direction: _Optional[str] = ..., value: _Optional[float] = ..., is_drivable: _Optional[bool] = ..., signal: _Optional[_Union[SignalView, _Mapping]] = ..., is_silent: _Optional[bool] = ..., display_value: _Optional[str] = ..., is_driven_by_graph: _Optional[bool] = ...) -> None: ...

class ChannelList(_message.Message):
    __slots__ = ("channels",)
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedCompositeFieldContainer[ChannelView]
    def __init__(self, channels: _Optional[_Iterable[_Union[ChannelView, _Mapping]]] = ...) -> None: ...

class SignalRequest(_message.Message):
    __slots__ = ("channel_id", "signal", "when")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    signal: SignalView
    when: When
    def __init__(self, channel_id: _Optional[int] = ..., signal: _Optional[_Union[SignalView, _Mapping]] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

class WaveformView(_message.Message):
    __slots__ = ("name", "display_name", "is_alternating", "is_periodic")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ALTERNATING_FIELD_NUMBER: _ClassVar[int]
    IS_PERIODIC_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    is_alternating: bool
    is_periodic: bool
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., is_alternating: _Optional[bool] = ..., is_periodic: _Optional[bool] = ...) -> None: ...

class SignalInputRequest(_message.Message):
    __slots__ = ("node", "output")
    NODE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    node: str
    output: int
    def __init__(self, node: _Optional[str] = ..., output: _Optional[int] = ...) -> None: ...

class SignalNodeRequest(_message.Message):
    __slots__ = ("key", "kind", "signal", "source", "inputs", "model", "parameters", "interpreted")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    KEY_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INTERPRETED_FIELD_NUMBER: _ClassVar[int]
    key: str
    kind: str
    signal: SignalView
    source: int
    inputs: _containers.RepeatedCompositeFieldContainer[SignalInputRequest]
    model: str
    parameters: _containers.ScalarMap[str, float]
    interpreted: bool
    def __init__(self, key: _Optional[str] = ..., kind: _Optional[str] = ..., signal: _Optional[_Union[SignalView, _Mapping]] = ..., source: _Optional[int] = ..., inputs: _Optional[_Iterable[_Union[SignalInputRequest, _Mapping]]] = ..., model: _Optional[str] = ..., parameters: _Optional[_Mapping[str, float]] = ..., interpreted: _Optional[bool] = ...) -> None: ...

class ModelParameterView(_message.Message):
    __slots__ = ("name", "default_value", "unit")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    name: str
    default_value: float
    unit: str
    def __init__(self, name: _Optional[str] = ..., default_value: _Optional[float] = ..., unit: _Optional[str] = ...) -> None: ...

class ModelView(_message.Message):
    __slots__ = ("name", "description", "inputs", "outputs", "parameters", "step_us", "source", "problem", "kind", "execution", "execution_label", "execution_reason", "state_names", "origin", "origin_label", "stands_in_for")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STEP_US_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PROBLEM_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_LABEL_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_REASON_FIELD_NUMBER: _ClassVar[int]
    STATE_NAMES_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_LABEL_FIELD_NUMBER: _ClassVar[int]
    STANDS_IN_FOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    inputs: _containers.RepeatedScalarFieldContainer[str]
    outputs: _containers.RepeatedScalarFieldContainer[str]
    parameters: _containers.RepeatedCompositeFieldContainer[ModelParameterView]
    step_us: int
    source: str
    problem: str
    kind: str
    execution: str
    execution_label: str
    execution_reason: str
    state_names: _containers.RepeatedScalarFieldContainer[str]
    origin: str
    origin_label: str
    stands_in_for: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., inputs: _Optional[_Iterable[str]] = ..., outputs: _Optional[_Iterable[str]] = ..., parameters: _Optional[_Iterable[_Union[ModelParameterView, _Mapping]]] = ..., step_us: _Optional[int] = ..., source: _Optional[str] = ..., problem: _Optional[str] = ..., kind: _Optional[str] = ..., execution: _Optional[str] = ..., execution_label: _Optional[str] = ..., execution_reason: _Optional[str] = ..., state_names: _Optional[_Iterable[str]] = ..., origin: _Optional[str] = ..., origin_label: _Optional[str] = ..., stands_in_for: _Optional[str] = ...) -> None: ...

class ModelNodeChoice(_message.Message):
    __slots__ = ("node", "when")
    NODE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    node: str
    when: When
    def __init__(self, node: _Optional[str] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

class ModelStateView(_message.Message):
    __slots__ = ("name", "value", "value_text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: float
    value_text: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[float] = ..., value_text: _Optional[str] = ...) -> None: ...

class ModelNodeView(_message.Message):
    __slots__ = ("node", "execution", "execution_label", "execution_reason", "fault", "state")
    NODE_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_LABEL_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_REASON_FIELD_NUMBER: _ClassVar[int]
    FAULT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    node: str
    execution: str
    execution_label: str
    execution_reason: str
    fault: str
    state: _containers.RepeatedCompositeFieldContainer[ModelStateView]
    def __init__(self, node: _Optional[str] = ..., execution: _Optional[str] = ..., execution_label: _Optional[str] = ..., execution_reason: _Optional[str] = ..., fault: _Optional[str] = ..., state: _Optional[_Iterable[_Union[ModelStateView, _Mapping]]] = ...) -> None: ...

class SignalGraphView(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[ModelNodeView]
    def __init__(self, models: _Optional[_Iterable[_Union[ModelNodeView, _Mapping]]] = ...) -> None: ...

class ModelList(_message.Message):
    __slots__ = ("models", "unavailable_reason")
    MODELS_FIELD_NUMBER: _ClassVar[int]
    UNAVAILABLE_REASON_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[ModelView]
    unavailable_reason: str
    def __init__(self, models: _Optional[_Iterable[_Union[ModelView, _Mapping]]] = ..., unavailable_reason: _Optional[str] = ...) -> None: ...

class SignalTargetRequest(_message.Message):
    __slots__ = ("channel_id", "node", "output")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    node: str
    output: int
    def __init__(self, channel_id: _Optional[int] = ..., node: _Optional[str] = ..., output: _Optional[int] = ...) -> None: ...

class SignalGraphRequest(_message.Message):
    __slots__ = ("nodes", "targets", "when")
    NODES_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[SignalNodeRequest]
    targets: _containers.RepeatedCompositeFieldContainer[SignalTargetRequest]
    when: When
    def __init__(self, nodes: _Optional[_Iterable[_Union[SignalNodeRequest, _Mapping]]] = ..., targets: _Optional[_Iterable[_Union[SignalTargetRequest, _Mapping]]] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

class WaveformList(_message.Message):
    __slots__ = ("waveforms",)
    WAVEFORMS_FIELD_NUMBER: _ClassVar[int]
    waveforms: _containers.RepeatedCompositeFieldContainer[WaveformView]
    def __init__(self, waveforms: _Optional[_Iterable[_Union[WaveformView, _Mapping]]] = ...) -> None: ...

class VariableView(_message.Message):
    __slots__ = ("variable_id", "path", "name", "root", "segments", "encoding", "byte_width", "link_time_address", "runtime_address", "is_writable", "bit_offset", "bit_width", "origin", "is_firmware", "declared_in", "display_type", "display_address", "is_enum", "enumerators")
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
    IS_ENUM_FIELD_NUMBER: _ClassVar[int]
    ENUMERATORS_FIELD_NUMBER: _ClassVar[int]
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
    is_enum: bool
    enumerators: _containers.RepeatedCompositeFieldContainer[Enumerator]
    def __init__(self, variable_id: _Optional[int] = ..., path: _Optional[str] = ..., name: _Optional[str] = ..., root: _Optional[str] = ..., segments: _Optional[_Iterable[str]] = ..., encoding: _Optional[str] = ..., byte_width: _Optional[int] = ..., link_time_address: _Optional[int] = ..., runtime_address: _Optional[int] = ..., is_writable: _Optional[bool] = ..., bit_offset: _Optional[int] = ..., bit_width: _Optional[int] = ..., origin: _Optional[str] = ..., is_firmware: _Optional[bool] = ..., declared_in: _Optional[str] = ..., display_type: _Optional[str] = ..., display_address: _Optional[str] = ..., is_enum: _Optional[bool] = ..., enumerators: _Optional[_Iterable[_Union[Enumerator, _Mapping]]] = ...) -> None: ...

class Enumerator(_message.Message):
    __slots__ = ("value", "name")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    value: int
    name: str
    def __init__(self, value: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class VariableCatalogue(_message.Message):
    __slots__ = ("variables", "unavailable_reason")
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    UNAVAILABLE_REASON_FIELD_NUMBER: _ClassVar[int]
    variables: _containers.RepeatedCompositeFieldContainer[VariableView]
    unavailable_reason: str
    def __init__(self, variables: _Optional[_Iterable[_Union[VariableView, _Mapping]]] = ..., unavailable_reason: _Optional[str] = ...) -> None: ...

class Scaling(_message.Message):
    __slots__ = ("scale", "offset")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    scale: float
    offset: float
    def __init__(self, scale: _Optional[float] = ..., offset: _Optional[float] = ...) -> None: ...

class VariableChoice(_message.Message):
    __slots__ = ("variable_id", "scaling")
    VARIABLE_ID_FIELD_NUMBER: _ClassVar[int]
    SCALING_FIELD_NUMBER: _ClassVar[int]
    variable_id: int
    scaling: Scaling
    def __init__(self, variable_id: _Optional[int] = ..., scaling: _Optional[_Union[Scaling, _Mapping]] = ...) -> None: ...

class WatchView(_message.Message):
    __slots__ = ("channel_id", "path", "name", "encoding", "byte_width", "runtime_address", "is_writable", "value", "bit_offset", "bit_width", "display_value", "range_text", "lowest", "highest", "resolution", "raw_value", "scaling", "read_period_us", "read_period_text", "enumerators")
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
    LOWEST_FIELD_NUMBER: _ClassVar[int]
    HIGHEST_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    RAW_VALUE_FIELD_NUMBER: _ClassVar[int]
    SCALING_FIELD_NUMBER: _ClassVar[int]
    READ_PERIOD_US_FIELD_NUMBER: _ClassVar[int]
    READ_PERIOD_TEXT_FIELD_NUMBER: _ClassVar[int]
    ENUMERATORS_FIELD_NUMBER: _ClassVar[int]
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
    lowest: float
    highest: float
    resolution: float
    raw_value: float
    scaling: Scaling
    read_period_us: int
    read_period_text: str
    enumerators: _containers.RepeatedCompositeFieldContainer[Enumerator]
    def __init__(self, channel_id: _Optional[int] = ..., path: _Optional[str] = ..., name: _Optional[str] = ..., encoding: _Optional[str] = ..., byte_width: _Optional[int] = ..., runtime_address: _Optional[int] = ..., is_writable: _Optional[bool] = ..., value: _Optional[float] = ..., bit_offset: _Optional[int] = ..., bit_width: _Optional[int] = ..., display_value: _Optional[str] = ..., range_text: _Optional[str] = ..., lowest: _Optional[float] = ..., highest: _Optional[float] = ..., resolution: _Optional[float] = ..., raw_value: _Optional[float] = ..., scaling: _Optional[_Union[Scaling, _Mapping]] = ..., read_period_us: _Optional[int] = ..., read_period_text: _Optional[str] = ..., enumerators: _Optional[_Iterable[_Union[Enumerator, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("channel_id", "value", "when")
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    value: float
    when: When
    def __init__(self, channel_id: _Optional[int] = ..., value: _Optional[float] = ..., when: _Optional[_Union[When, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("sim_us", "gap", "column", "is_outbound", "payload", "response", "was_taken")
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    GAP_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    IS_OUTBOUND_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    WAS_TAKEN_FIELD_NUMBER: _ClassVar[int]
    sim_us: int
    gap: str
    column: int
    is_outbound: bool
    payload: str
    response: str
    was_taken: bool
    def __init__(self, sim_us: _Optional[int] = ..., gap: _Optional[str] = ..., column: _Optional[int] = ..., is_outbound: _Optional[bool] = ..., payload: _Optional[str] = ..., response: _Optional[str] = ..., was_taken: _Optional[bool] = ...) -> None: ...

class LadderView(_message.Message):
    __slots__ = ("bus_name", "parties", "steps", "note", "position")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    parties: _containers.RepeatedCompositeFieldContainer[PartyView]
    steps: _containers.RepeatedCompositeFieldContainer[StepView]
    note: str
    position: ViewPosition
    def __init__(self, bus_name: _Optional[str] = ..., parties: _Optional[_Iterable[_Union[PartyView, _Mapping]]] = ..., steps: _Optional[_Iterable[_Union[StepView, _Mapping]]] = ..., note: _Optional[str] = ..., position: _Optional[_Union[ViewPosition, _Mapping]] = ...) -> None: ...

class LadderChoice(_message.Message):
    __slots__ = ("bus_id",)
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    def __init__(self, bus_id: _Optional[int] = ...) -> None: ...

class WindowView(_message.Message):
    __slots__ = ("start_us", "end_us")
    START_US_FIELD_NUMBER: _ClassVar[int]
    END_US_FIELD_NUMBER: _ClassVar[int]
    start_us: int
    end_us: int
    def __init__(self, start_us: _Optional[int] = ..., end_us: _Optional[int] = ...) -> None: ...

class MarkView(_message.Message):
    __slots__ = ("sim_us", "label", "detail", "duration_us", "is_doubtful", "is_high")
    SIM_US_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DURATION_US_FIELD_NUMBER: _ClassVar[int]
    IS_DOUBTFUL_FIELD_NUMBER: _ClassVar[int]
    IS_HIGH_FIELD_NUMBER: _ClassVar[int]
    sim_us: int
    label: str
    detail: str
    duration_us: int
    is_doubtful: bool
    is_high: bool
    def __init__(self, sim_us: _Optional[int] = ..., label: _Optional[str] = ..., detail: _Optional[str] = ..., duration_us: _Optional[int] = ..., is_doubtful: _Optional[bool] = ..., is_high: _Optional[bool] = ...) -> None: ...

class LaneView(_message.Message):
    __slots__ = ("key", "label", "kind", "marks", "count", "gaps", "usual_gap_us", "worst_gap_us", "summary")
    KEY_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    MARKS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    GAPS_FIELD_NUMBER: _ClassVar[int]
    USUAL_GAP_US_FIELD_NUMBER: _ClassVar[int]
    WORST_GAP_US_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    key: str
    label: str
    kind: str
    marks: _containers.RepeatedCompositeFieldContainer[MarkView]
    count: int
    gaps: _containers.RepeatedCompositeFieldContainer[GapPoint]
    usual_gap_us: int
    worst_gap_us: int
    summary: str
    def __init__(self, key: _Optional[str] = ..., label: _Optional[str] = ..., kind: _Optional[str] = ..., marks: _Optional[_Iterable[_Union[MarkView, _Mapping]]] = ..., count: _Optional[int] = ..., gaps: _Optional[_Iterable[_Union[GapPoint, _Mapping]]] = ..., usual_gap_us: _Optional[int] = ..., worst_gap_us: _Optional[int] = ..., summary: _Optional[str] = ...) -> None: ...

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
    points: _containers.RepeatedCompositeFieldContainer[CurvePoint]
    lowest: float
    highest: float
    def __init__(self, key: _Optional[str] = ..., label: _Optional[str] = ..., channel_id: _Optional[int] = ..., points: _Optional[_Iterable[_Union[CurvePoint, _Mapping]]] = ..., lowest: _Optional[float] = ..., highest: _Optional[float] = ...) -> None: ...

class TimelineView(_message.Message):
    __slots__ = ("window", "recorded", "curves", "lanes", "is_empty", "position")
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    RECORDED_FIELD_NUMBER: _ClassVar[int]
    CURVES_FIELD_NUMBER: _ClassVar[int]
    LANES_FIELD_NUMBER: _ClassVar[int]
    IS_EMPTY_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    window: WindowView
    recorded: WindowView
    curves: _containers.RepeatedCompositeFieldContainer[CurveView]
    lanes: _containers.RepeatedCompositeFieldContainer[LaneView]
    is_empty: bool
    position: ViewPosition
    def __init__(self, window: _Optional[_Union[WindowView, _Mapping]] = ..., recorded: _Optional[_Union[WindowView, _Mapping]] = ..., curves: _Optional[_Iterable[_Union[CurveView, _Mapping]]] = ..., lanes: _Optional[_Iterable[_Union[LaneView, _Mapping]]] = ..., is_empty: _Optional[bool] = ..., position: _Optional[_Union[ViewPosition, _Mapping]] = ...) -> None: ...

class Following(_message.Message):
    __slots__ = ("wanted",)
    WANTED_FIELD_NUMBER: _ClassVar[int]
    wanted: bool
    def __init__(self, wanted: _Optional[bool] = ...) -> None: ...

class TimelineRequest(_message.Message):
    __slots__ = ("window_us",)
    WINDOW_US_FIELD_NUMBER: _ClassVar[int]
    window_us: int
    def __init__(self, window_us: _Optional[int] = ...) -> None: ...

class CallTimingView(_message.Message):
    __slots__ = ("function", "calls", "answered_calls", "total_host_ns", "mean", "longest", "is_never_answered", "bands", "shape", "origin")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    ANSWERED_CALLS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_HOST_NS_FIELD_NUMBER: _ClassVar[int]
    MEAN_FIELD_NUMBER: _ClassVar[int]
    LONGEST_FIELD_NUMBER: _ClassVar[int]
    IS_NEVER_ANSWERED_FIELD_NUMBER: _ClassVar[int]
    BANDS_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    function: str
    calls: int
    answered_calls: int
    total_host_ns: int
    mean: str
    longest: str
    is_never_answered: bool
    bands: _containers.RepeatedScalarFieldContainer[int]
    shape: str
    origin: str
    def __init__(self, function: _Optional[str] = ..., calls: _Optional[int] = ..., answered_calls: _Optional[int] = ..., total_host_ns: _Optional[int] = ..., mean: _Optional[str] = ..., longest: _Optional[str] = ..., is_never_answered: _Optional[bool] = ..., bands: _Optional[_Iterable[int]] = ..., shape: _Optional[str] = ..., origin: _Optional[str] = ...) -> None: ...

class TimingReportView(_message.Message):
    __slots__ = ("entries", "heaviest_host_ns")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    HEAVIEST_HOST_NS_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[CallTimingView]
    heaviest_host_ns: int
    def __init__(self, entries: _Optional[_Iterable[_Union[CallTimingView, _Mapping]]] = ..., heaviest_host_ns: _Optional[int] = ...) -> None: ...

class ProfileEntryView(_message.Message):
    __slots__ = ("name", "origin", "directory", "file_name", "calls", "self_nanoseconds", "total_nanoseconds", "self_text", "total_text", "mean_text", "longest_text", "source_path", "line")
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
    SOURCE_PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
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
    source_path: str
    line: int
    def __init__(self, name: _Optional[str] = ..., origin: _Optional[str] = ..., directory: _Optional[str] = ..., file_name: _Optional[str] = ..., calls: _Optional[int] = ..., self_nanoseconds: _Optional[int] = ..., total_nanoseconds: _Optional[int] = ..., self_text: _Optional[str] = ..., total_text: _Optional[str] = ..., mean_text: _Optional[str] = ..., longest_text: _Optional[str] = ..., source_path: _Optional[str] = ..., line: _Optional[int] = ...) -> None: ...

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

class BusView(_message.Message):
    __slots__ = ("bus_id", "kind", "name", "bitrate_bps", "display_bitrate", "accepts_messages", "takes_address", "address_label", "takes_extended", "max_payload_bytes", "max_address", "max_extended_address", "takes_line_ending", "supports_fd", "supports_remote", "exchange_unit", "has_time_model", "controller_latency_us", "queue_depth", "queue_unit")
    BUS_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BITRATE_BPS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_BITRATE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTS_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    TAKES_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_LABEL_FIELD_NUMBER: _ClassVar[int]
    TAKES_EXTENDED_FIELD_NUMBER: _ClassVar[int]
    MAX_PAYLOAD_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MAX_EXTENDED_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TAKES_LINE_ENDING_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_FD_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_REMOTE_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_UNIT_FIELD_NUMBER: _ClassVar[int]
    HAS_TIME_MODEL_FIELD_NUMBER: _ClassVar[int]
    CONTROLLER_LATENCY_US_FIELD_NUMBER: _ClassVar[int]
    QUEUE_DEPTH_FIELD_NUMBER: _ClassVar[int]
    QUEUE_UNIT_FIELD_NUMBER: _ClassVar[int]
    bus_id: int
    kind: str
    name: str
    bitrate_bps: int
    display_bitrate: str
    accepts_messages: bool
    takes_address: bool
    address_label: str
    takes_extended: bool
    max_payload_bytes: int
    max_address: int
    max_extended_address: int
    takes_line_ending: bool
    supports_fd: bool
    supports_remote: bool
    exchange_unit: ExchangeUnit
    has_time_model: bool
    controller_latency_us: int
    queue_depth: int
    queue_unit: ExchangeUnit
    def __init__(self, bus_id: _Optional[int] = ..., kind: _Optional[str] = ..., name: _Optional[str] = ..., bitrate_bps: _Optional[int] = ..., display_bitrate: _Optional[str] = ..., accepts_messages: _Optional[bool] = ..., takes_address: _Optional[bool] = ..., address_label: _Optional[str] = ..., takes_extended: _Optional[bool] = ..., max_payload_bytes: _Optional[int] = ..., max_address: _Optional[int] = ..., max_extended_address: _Optional[int] = ..., takes_line_ending: _Optional[bool] = ..., supports_fd: _Optional[bool] = ..., supports_remote: _Optional[bool] = ..., exchange_unit: _Optional[_Union[ExchangeUnit, str]] = ..., has_time_model: _Optional[bool] = ..., controller_latency_us: _Optional[int] = ..., queue_depth: _Optional[int] = ..., queue_unit: _Optional[_Union[ExchangeUnit, str]] = ...) -> None: ...

class SourceFileView(_message.Message):
    __slots__ = ("path", "display_path", "origin", "is_header", "is_project", "state", "state_text")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PATH_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    IS_HEADER_FIELD_NUMBER: _ClassVar[int]
    IS_PROJECT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    display_path: str
    origin: str
    is_header: bool
    is_project: bool
    state: SourceState
    state_text: str
    def __init__(self, path: _Optional[str] = ..., display_path: _Optional[str] = ..., origin: _Optional[str] = ..., is_header: _Optional[bool] = ..., is_project: _Optional[bool] = ..., state: _Optional[_Union[SourceState, str]] = ..., state_text: _Optional[str] = ...) -> None: ...

class SourceTreeView(_message.Message):
    __slots__ = ("files", "note")
    FILES_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[SourceFileView]
    note: str
    def __init__(self, files: _Optional[_Iterable[_Union[SourceFileView, _Mapping]]] = ..., note: _Optional[str] = ...) -> None: ...

class SourceRequest(_message.Message):
    __slots__ = ("path", "from_disk")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_DISK_FIELD_NUMBER: _ClassVar[int]
    path: str
    from_disk: bool
    def __init__(self, path: _Optional[str] = ..., from_disk: _Optional[bool] = ...) -> None: ...

class SourceText(_message.Message):
    __slots__ = ("path", "as_built", "text", "digest", "state", "state_text", "note")
    PATH_FIELD_NUMBER: _ClassVar[int]
    AS_BUILT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    path: str
    as_built: bool
    text: str
    digest: str
    state: SourceState
    state_text: str
    note: str
    def __init__(self, path: _Optional[str] = ..., as_built: _Optional[bool] = ..., text: _Optional[str] = ..., digest: _Optional[str] = ..., state: _Optional[_Union[SourceState, str]] = ..., state_text: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...

class SemanticSpan(_message.Message):
    __slots__ = ("line", "column", "length", "kind", "kind_text", "name", "caption", "declared_path", "declared_line")
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    KIND_TEXT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    DECLARED_PATH_FIELD_NUMBER: _ClassVar[int]
    DECLARED_LINE_FIELD_NUMBER: _ClassVar[int]
    line: int
    column: int
    length: int
    kind: SymbolKind
    kind_text: str
    name: str
    caption: str
    declared_path: str
    declared_line: int
    def __init__(self, line: _Optional[int] = ..., column: _Optional[int] = ..., length: _Optional[int] = ..., kind: _Optional[_Union[SymbolKind, str]] = ..., kind_text: _Optional[str] = ..., name: _Optional[str] = ..., caption: _Optional[str] = ..., declared_path: _Optional[str] = ..., declared_line: _Optional[int] = ...) -> None: ...

class FunctionExtentView(_message.Message):
    __slots__ = ("name", "signature", "first_line", "last_line")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    FIRST_LINE_FIELD_NUMBER: _ClassVar[int]
    LAST_LINE_FIELD_NUMBER: _ClassVar[int]
    name: str
    signature: str
    first_line: int
    last_line: int
    def __init__(self, name: _Optional[str] = ..., signature: _Optional[str] = ..., first_line: _Optional[int] = ..., last_line: _Optional[int] = ...) -> None: ...

class LineRange(_message.Message):
    __slots__ = ("first_line", "last_line")
    FIRST_LINE_FIELD_NUMBER: _ClassVar[int]
    LAST_LINE_FIELD_NUMBER: _ClassVar[int]
    first_line: int
    last_line: int
    def __init__(self, first_line: _Optional[int] = ..., last_line: _Optional[int] = ...) -> None: ...

class SemanticsView(_message.Message):
    __slots__ = ("path", "digest", "spans", "functions", "inactive", "note")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    SPANS_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    path: str
    digest: str
    spans: _containers.RepeatedCompositeFieldContainer[SemanticSpan]
    functions: _containers.RepeatedCompositeFieldContainer[FunctionExtentView]
    inactive: _containers.RepeatedCompositeFieldContainer[LineRange]
    note: str
    def __init__(self, path: _Optional[str] = ..., digest: _Optional[str] = ..., spans: _Optional[_Iterable[_Union[SemanticSpan, _Mapping]]] = ..., functions: _Optional[_Iterable[_Union[FunctionExtentView, _Mapping]]] = ..., inactive: _Optional[_Iterable[_Union[LineRange, _Mapping]]] = ..., note: _Optional[str] = ...) -> None: ...

class LineCountEntry(_message.Message):
    __slots__ = ("line", "count", "count_text", "heat", "branches", "branches_taken", "partly_run", "recent", "rate_text", "rate_heat", "group_first", "group_last")
    LINE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    COUNT_TEXT_FIELD_NUMBER: _ClassVar[int]
    HEAT_FIELD_NUMBER: _ClassVar[int]
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    BRANCHES_TAKEN_FIELD_NUMBER: _ClassVar[int]
    PARTLY_RUN_FIELD_NUMBER: _ClassVar[int]
    RECENT_FIELD_NUMBER: _ClassVar[int]
    RATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    RATE_HEAT_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIRST_FIELD_NUMBER: _ClassVar[int]
    GROUP_LAST_FIELD_NUMBER: _ClassVar[int]
    line: int
    count: int
    count_text: str
    heat: int
    branches: int
    branches_taken: int
    partly_run: bool
    recent: int
    rate_text: str
    rate_heat: int
    group_first: int
    group_last: int
    def __init__(self, line: _Optional[int] = ..., count: _Optional[int] = ..., count_text: _Optional[str] = ..., heat: _Optional[int] = ..., branches: _Optional[int] = ..., branches_taken: _Optional[int] = ..., partly_run: _Optional[bool] = ..., recent: _Optional[int] = ..., rate_text: _Optional[str] = ..., rate_heat: _Optional[int] = ..., group_first: _Optional[int] = ..., group_last: _Optional[int] = ...) -> None: ...

class FunctionCountView(_message.Message):
    __slots__ = ("name", "path", "first_line", "last_line", "calls", "calls_text", "lines", "lines_run", "has_host_cost", "host_self_text", "host_share_text", "recent_calls", "calls_rate_text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FIRST_LINE_FIELD_NUMBER: _ClassVar[int]
    LAST_LINE_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    CALLS_TEXT_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    LINES_RUN_FIELD_NUMBER: _ClassVar[int]
    HAS_HOST_COST_FIELD_NUMBER: _ClassVar[int]
    HOST_SELF_TEXT_FIELD_NUMBER: _ClassVar[int]
    HOST_SHARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    RECENT_CALLS_FIELD_NUMBER: _ClassVar[int]
    CALLS_RATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    first_line: int
    last_line: int
    calls: int
    calls_text: str
    lines: int
    lines_run: int
    has_host_cost: bool
    host_self_text: str
    host_share_text: str
    recent_calls: int
    calls_rate_text: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., first_line: _Optional[int] = ..., last_line: _Optional[int] = ..., calls: _Optional[int] = ..., calls_text: _Optional[str] = ..., lines: _Optional[int] = ..., lines_run: _Optional[int] = ..., has_host_cost: _Optional[bool] = ..., host_self_text: _Optional[str] = ..., host_share_text: _Optional[str] = ..., recent_calls: _Optional[int] = ..., calls_rate_text: _Optional[str] = ...) -> None: ...

class LineCountView(_message.Message):
    __slots__ = ("path", "counting", "is_counted", "lines", "functions", "since_us", "at_us", "since_text", "summary_text", "note", "window_us", "rate_window_text")
    PATH_FIELD_NUMBER: _ClassVar[int]
    COUNTING_FIELD_NUMBER: _ClassVar[int]
    IS_COUNTED_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    SINCE_US_FIELD_NUMBER: _ClassVar[int]
    AT_US_FIELD_NUMBER: _ClassVar[int]
    SINCE_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_TEXT_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    WINDOW_US_FIELD_NUMBER: _ClassVar[int]
    RATE_WINDOW_TEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    counting: bool
    is_counted: bool
    lines: _containers.RepeatedCompositeFieldContainer[LineCountEntry]
    functions: _containers.RepeatedCompositeFieldContainer[FunctionCountView]
    since_us: int
    at_us: int
    since_text: str
    summary_text: str
    note: str
    window_us: int
    rate_window_text: str
    def __init__(self, path: _Optional[str] = ..., counting: _Optional[bool] = ..., is_counted: _Optional[bool] = ..., lines: _Optional[_Iterable[_Union[LineCountEntry, _Mapping]]] = ..., functions: _Optional[_Iterable[_Union[FunctionCountView, _Mapping]]] = ..., since_us: _Optional[int] = ..., at_us: _Optional[int] = ..., since_text: _Optional[str] = ..., summary_text: _Optional[str] = ..., note: _Optional[str] = ..., window_us: _Optional[int] = ..., rate_window_text: _Optional[str] = ...) -> None: ...

class FileCoverage(_message.Message):
    __slots__ = ("path", "lines", "lines_run", "never_run", "share_text")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    LINES_RUN_FIELD_NUMBER: _ClassVar[int]
    NEVER_RUN_FIELD_NUMBER: _ClassVar[int]
    SHARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    lines: int
    lines_run: int
    never_run: int
    share_text: str
    def __init__(self, path: _Optional[str] = ..., lines: _Optional[int] = ..., lines_run: _Optional[int] = ..., never_run: _Optional[int] = ..., share_text: _Optional[str] = ...) -> None: ...

class CoverageView(_message.Message):
    __slots__ = ("counting", "files", "never_called", "lines", "lines_run", "share_text", "since_us", "at_us", "since_text", "summary_text", "note")
    COUNTING_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    NEVER_CALLED_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    LINES_RUN_FIELD_NUMBER: _ClassVar[int]
    SHARE_TEXT_FIELD_NUMBER: _ClassVar[int]
    SINCE_US_FIELD_NUMBER: _ClassVar[int]
    AT_US_FIELD_NUMBER: _ClassVar[int]
    SINCE_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_TEXT_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    counting: bool
    files: _containers.RepeatedCompositeFieldContainer[FileCoverage]
    never_called: _containers.RepeatedCompositeFieldContainer[FunctionCountView]
    lines: int
    lines_run: int
    share_text: str
    since_us: int
    at_us: int
    since_text: str
    summary_text: str
    note: str
    def __init__(self, counting: _Optional[bool] = ..., files: _Optional[_Iterable[_Union[FileCoverage, _Mapping]]] = ..., never_called: _Optional[_Iterable[_Union[FunctionCountView, _Mapping]]] = ..., lines: _Optional[int] = ..., lines_run: _Optional[int] = ..., share_text: _Optional[str] = ..., since_us: _Optional[int] = ..., at_us: _Optional[int] = ..., since_text: _Optional[str] = ..., summary_text: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...

class HotLine(_message.Message):
    __slots__ = ("path", "line", "count", "count_text", "function", "recent", "rate_text")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    COUNT_TEXT_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    RECENT_FIELD_NUMBER: _ClassVar[int]
    RATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    line: int
    count: int
    count_text: str
    function: str
    recent: int
    rate_text: str
    def __init__(self, path: _Optional[str] = ..., line: _Optional[int] = ..., count: _Optional[int] = ..., count_text: _Optional[str] = ..., function: _Optional[str] = ..., recent: _Optional[int] = ..., rate_text: _Optional[str] = ...) -> None: ...

class HotspotsView(_message.Message):
    __slots__ = ("counting", "lines", "functions", "costly", "since_text", "note", "lines_by_rate", "functions_by_rate", "rate_window_text")
    COUNTING_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    COSTLY_FIELD_NUMBER: _ClassVar[int]
    SINCE_TEXT_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    LINES_BY_RATE_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONS_BY_RATE_FIELD_NUMBER: _ClassVar[int]
    RATE_WINDOW_TEXT_FIELD_NUMBER: _ClassVar[int]
    counting: bool
    lines: _containers.RepeatedCompositeFieldContainer[HotLine]
    functions: _containers.RepeatedCompositeFieldContainer[FunctionCountView]
    costly: _containers.RepeatedCompositeFieldContainer[FunctionCountView]
    since_text: str
    note: str
    lines_by_rate: _containers.RepeatedCompositeFieldContainer[HotLine]
    functions_by_rate: _containers.RepeatedCompositeFieldContainer[FunctionCountView]
    rate_window_text: str
    def __init__(self, counting: _Optional[bool] = ..., lines: _Optional[_Iterable[_Union[HotLine, _Mapping]]] = ..., functions: _Optional[_Iterable[_Union[FunctionCountView, _Mapping]]] = ..., costly: _Optional[_Iterable[_Union[FunctionCountView, _Mapping]]] = ..., since_text: _Optional[str] = ..., note: _Optional[str] = ..., lines_by_rate: _Optional[_Iterable[_Union[HotLine, _Mapping]]] = ..., functions_by_rate: _Optional[_Iterable[_Union[FunctionCountView, _Mapping]]] = ..., rate_window_text: _Optional[str] = ...) -> None: ...

class BreakpointPlace(_message.Message):
    __slots__ = ("path", "line")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    path: str
    line: int
    def __init__(self, path: _Optional[str] = ..., line: _Optional[int] = ...) -> None: ...

class DebugControl(_message.Message):
    __slots__ = ("attach", "detach", "resume", "step_over", "step_into", "step_out", "add_breakpoint", "remove_breakpoint")
    ATTACH_FIELD_NUMBER: _ClassVar[int]
    DETACH_FIELD_NUMBER: _ClassVar[int]
    RESUME_FIELD_NUMBER: _ClassVar[int]
    STEP_OVER_FIELD_NUMBER: _ClassVar[int]
    STEP_INTO_FIELD_NUMBER: _ClassVar[int]
    STEP_OUT_FIELD_NUMBER: _ClassVar[int]
    ADD_BREAKPOINT_FIELD_NUMBER: _ClassVar[int]
    REMOVE_BREAKPOINT_FIELD_NUMBER: _ClassVar[int]
    attach: Empty
    detach: Empty
    resume: Empty
    step_over: Empty
    step_into: Empty
    step_out: Empty
    add_breakpoint: BreakpointPlace
    remove_breakpoint: int
    def __init__(self, attach: _Optional[_Union[Empty, _Mapping]] = ..., detach: _Optional[_Union[Empty, _Mapping]] = ..., resume: _Optional[_Union[Empty, _Mapping]] = ..., step_over: _Optional[_Union[Empty, _Mapping]] = ..., step_into: _Optional[_Union[Empty, _Mapping]] = ..., step_out: _Optional[_Union[Empty, _Mapping]] = ..., add_breakpoint: _Optional[_Union[BreakpointPlace, _Mapping]] = ..., remove_breakpoint: _Optional[int] = ...) -> None: ...

class DebugFrame(_message.Message):
    __slots__ = ("level", "function", "path", "line", "place_text")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    PLACE_TEXT_FIELD_NUMBER: _ClassVar[int]
    level: int
    function: str
    path: str
    line: int
    place_text: str
    def __init__(self, level: _Optional[int] = ..., function: _Optional[str] = ..., path: _Optional[str] = ..., line: _Optional[int] = ..., place_text: _Optional[str] = ...) -> None: ...

class BreakpointView(_message.Message):
    __slots__ = ("number", "path", "line", "resolved", "hits")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_FIELD_NUMBER: _ClassVar[int]
    HITS_FIELD_NUMBER: _ClassVar[int]
    number: int
    path: str
    line: int
    resolved: bool
    hits: int
    def __init__(self, number: _Optional[int] = ..., path: _Optional[str] = ..., line: _Optional[int] = ..., resolved: _Optional[bool] = ..., hits: _Optional[int] = ...) -> None: ...

class DebugVariable(_message.Message):
    __slots__ = ("name", "value", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    type: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class DebugView(_message.Message):
    __slots__ = ("available", "attached", "stopped", "status_text", "stopped_at", "breakpoints", "frames", "variables", "note")
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    ATTACHED_FIELD_NUMBER: _ClassVar[int]
    STOPPED_FIELD_NUMBER: _ClassVar[int]
    STATUS_TEXT_FIELD_NUMBER: _ClassVar[int]
    STOPPED_AT_FIELD_NUMBER: _ClassVar[int]
    BREAKPOINTS_FIELD_NUMBER: _ClassVar[int]
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    available: bool
    attached: bool
    stopped: bool
    status_text: str
    stopped_at: DebugFrame
    breakpoints: _containers.RepeatedCompositeFieldContainer[BreakpointView]
    frames: _containers.RepeatedCompositeFieldContainer[DebugFrame]
    variables: _containers.RepeatedCompositeFieldContainer[DebugVariable]
    note: str
    def __init__(self, available: _Optional[bool] = ..., attached: _Optional[bool] = ..., stopped: _Optional[bool] = ..., status_text: _Optional[str] = ..., stopped_at: _Optional[_Union[DebugFrame, _Mapping]] = ..., breakpoints: _Optional[_Iterable[_Union[BreakpointView, _Mapping]]] = ..., frames: _Optional[_Iterable[_Union[DebugFrame, _Mapping]]] = ..., variables: _Optional[_Iterable[_Union[DebugVariable, _Mapping]]] = ..., note: _Optional[str] = ...) -> None: ...

class RestartRequest(_message.Message):
    __slots__ = ("rebuild",)
    REBUILD_FIELD_NUMBER: _ClassVar[int]
    rebuild: bool
    def __init__(self, rebuild: _Optional[bool] = ...) -> None: ...

class BuildDiagnostic(_message.Message):
    __slots__ = ("path", "line", "column", "severity", "message")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    path: str
    line: int
    column: int
    severity: str
    message: str
    def __init__(self, path: _Optional[str] = ..., line: _Optional[int] = ..., column: _Optional[int] = ..., severity: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class BuildResult(_message.Message):
    __slots__ = ("failed", "title_text", "summary_text", "diagnostics", "output")
    FAILED_FIELD_NUMBER: _ClassVar[int]
    TITLE_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_TEXT_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSTICS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    failed: bool
    title_text: str
    summary_text: str
    diagnostics: _containers.RepeatedCompositeFieldContainer[BuildDiagnostic]
    output: str
    def __init__(self, failed: _Optional[bool] = ..., title_text: _Optional[str] = ..., summary_text: _Optional[str] = ..., diagnostics: _Optional[_Iterable[_Union[BuildDiagnostic, _Mapping]]] = ..., output: _Optional[str] = ...) -> None: ...

class RestartView(_message.Message):
    __slots__ = ("phase", "can_restart", "restart_unavailable", "can_rebuild", "rebuild_unavailable", "last_build", "generation", "done_text")
    PHASE_FIELD_NUMBER: _ClassVar[int]
    CAN_RESTART_FIELD_NUMBER: _ClassVar[int]
    RESTART_UNAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CAN_REBUILD_FIELD_NUMBER: _ClassVar[int]
    REBUILD_UNAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    LAST_BUILD_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    DONE_TEXT_FIELD_NUMBER: _ClassVar[int]
    phase: RestartPhase
    can_restart: bool
    restart_unavailable: str
    can_rebuild: bool
    rebuild_unavailable: str
    last_build: BuildResult
    generation: int
    done_text: str
    def __init__(self, phase: _Optional[_Union[RestartPhase, str]] = ..., can_restart: _Optional[bool] = ..., restart_unavailable: _Optional[str] = ..., can_rebuild: _Optional[bool] = ..., rebuild_unavailable: _Optional[str] = ..., last_build: _Optional[_Union[BuildResult, _Mapping]] = ..., generation: _Optional[int] = ..., done_text: _Optional[str] = ...) -> None: ...
