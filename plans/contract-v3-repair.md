# looper-py on contract version 3 – repair plan

Status: 2026-11-01, **ready for implementation** – all open questions are
decided (section 5), nothing implemented yet. Author: architect agent.
Goal (the user's words): looper-py works again **soon**, with the **same
feature set as today**; what `looper-core` removed disappears here too.
Nothing new is added.

Inputs read: looper-py (`CLAUDE.md`, `README.md`, `docs/`, `src/`, `tests/`,
`scripts/`, `pyproject.toml`), looper-core (schema, `servicer.py`,
`run_control.py`, `event_drain.py`, `cli/build_command.py`, history),
looper-rt (`looper_app.c`, `looper_commands_pace.c`), looper-rs
(`plans/contract-v3.md`, `docs/development/contract.md`,
`tests/contract_in_step.rs`, `src/inspector/grpc_inspector.rs`), plus two
probes run against a live `looper-cli run --no-build` of `examples/blinky`
with core's own v3 bindings (scripts kept outside the repository).

---

## 1. Diagnosis

### 1.1 What the checks say today

| Check | Result |
| --- | --- |
| `uv run ruff check src tests` | clean |
| `uv run mypy` | clean (24 files) – the old bindings are internally consistent |
| `uv run pytest` | **1 failed, 94 passed, 4 errors** |
| – `tests/test_contract_in_step.py` | FAIL: our `looper_inspector.proto` differs from core's |
| – `tests/integration/test_blinky.py` (4 tests) | ERROR in the fixture: `LooperCliError: looper-cli stopped before it served (exit 1)`. Cause on this machine: the build's link step failed with `ld.exe: cannot open output file ...\examples\blinky\build\blinky.exe: Permission denied` – a blinky executable was running (most likely the GUI's). This hides the real breakage. |
| Old library against the live v3 server (`build=False`) | `looper.run(...)` fails in `describe()` with `SimulationUnreachableError: Method not found!` |

So the library cannot attach at all. The reason is not a field: the gRPC
**package** changed from `looper.inspector.v1` to `looper.inspector.v3`, so
every method path (`/looper.inspector.v1.Inspector/Describe`) is unknown to
the server (`UNIMPLEMENTED`). Because of that, the version comparison in
`starting._attached` – which should raise `ContractMismatchError` – is never
reached; the user gets a misleading "unreachable".

### 1.2 Where the copy stands

Our copy is byte-identical to core's schema at **`54dd875`** (2026-10-29,
"add model listing functionality"), contract version 2, package
`looper.inspector.v1`, 721 lines. Core today (`7d34c89`) is version 3,
package `looper.inspector.v3`, 1454 lines; `git diff 54dd875 HEAD` on the
schema is +929/-196. Every change that matters to looper-py arrived in one
commit: **`9d1c3c0` "introduce AppliedChange model and enhance event handling
in simulation"** (version 3: `sim_us`, `Ack`, event stream, `ControlRun`).
The later commits (`3396c53`, `a6024cf`, `3a389b1`, `74ebf40`, `c1b3992`,
`7d34c89`) only add RPCs and fields looper-py does not use (sources, line
counts, hotspots, debugger, restart, pace fields), and `6acd749` added
scaling to watches (new fields only).

### 1.3 What changed, for the calls looper-py makes

| looper-py uses (v2) | v3 | Effect on looper-py |
| --- | --- | --- |
| package `looper.inspector.v1` | `looper.inspector.v3` | every call fails until the bindings are regenerated |
| `CONTRACT_VERSION_CURRENT = 2` | `= 3` | `CONTRACT_VERSION` follows the bindings automatically |
| `Describe` → `Description.time_mode` ("real_time"/"virtual") | field 3 **reserved "time_mode"**; new `capabilities`, `retention_us`, `max_events_per_batch` | `Description.time_mode`, `Simulation.time_mode`, `TimeMode` lose their source |
| `ObserveSimulation.microseconds`, `.time_mode` | `SimulationView.sim_us`; `time_mode` reserved | rename; the clock is better read from `ObserveRun.now_us` |
| `AdvanceTime(TimeStep{microseconds})` → `Empty`, refused by FAILED_PRECONDITION on a host clock | **removed**; `ControlRun(RunControl{run_for_us})` → `RunReply{ack, state}`, refused in the Ack (`REFUSAL_WRONG_MODE` / `REFUSAL_INVALID` "the clock runs in real time and cannot be advanced") | `advance` re-implemented on `ControlRun` |
| – | `ObserveRun` → `RunState{now_us, mode HELD/PACED/MAX, epoch, next_event_seq, target_us, hold_reason, ...}` | the source of "where is the clock, how does it run, where does the stream stand" |
| `ReadRecordings(RecordingPositions{after_sample, after_exchange})` → two rings, per-ring `sequence` | **removed**; `ReadEvents(ReadEventsRequest{epoch, from_event_seq, max_events, filter})` → `EventBatch{epoch, events, lost, next_event_seq, sim_now_us, epoch_changed}`; also `Subscribe` (stream) | reading the window is rewritten |
| `SampleView{channel_id, seconds: double, value, sequence}` | `Event{event_seq, sim_us}` + `Sample{channel_id, value}` | time is `uint64 sim_us`; one `event_seq` for all kinds |
| `ExchangeView{bus_id, kind, seconds, direction "outbound", address "0x123" (text), length, payload (hex text), response (hex text), accepted, sequence}` | `Event.sim_us` (= end) + `Exchange{bus_id, start_us, end_us, direction enum, address_value uint32, payload bytes, response bytes, payload_length, response_length, accepted, refusal, source, ...}`; no `kind` | translation rewritten; the address is a number "a client formats" (schema comment) |
| loss: only inferable from sequence gaps | `EventBatch.lost: Lost{from/to_event_seq, from/to_us, reason}` – **no event kind** | lost samples and lost exchanges can no longer be told apart |
| `ClearTrace`, `ClearBusTrace` (also `ClearTimeline`) | **removed**; `ClearRecordings(ClearRequest{epoch})` → `Ack`; clears everything, bumps the epoch, `event_seq` continues | one call; must name the epoch it saw |
| `TogglePin(PinToggle{pin_id, current_level})` → `PinLevel{level}` | **removed**; `DrivePin(PinDrive{pin_id, toggle})` → `PinDriven{ack, high: bool}`; the server toggles | no client-side level reading needed |
| `ApplySignal` → `Empty` | → `Ack` (request gains `when`) | check the Ack |
| `SendBusMessage(BusMessageRequest{bus_id, address, payload, extended})` → `Empty` | `BusMessageRequest{message: BusMessage{...}, when}` → `BusMessageReply{ack, summary}` | nested message; check the Ack |
| `WatchVariable` → `WatchView` | → `WatchStarted{watch, ack}` | unwrap, check the Ack |
| `WriteVariable`, `RemoveWatch` → `Empty` | → `Ack` | check the Ack |
| refusals: gRPC `FAILED_PRECONDITION` | changes: **in the `Ack`** (`refusal`, `refusal_text`); FAILED_PRECONDITION remains for reads (e.g. memory of an unreadable build) and for everything while a debugger holds the firmware | two refusal paths, both become `SimulationRefusedError` |
| `CallTimingView.total_seconds` | `total_host_ns` | not read by looper-py; no effect |
| `ObserveTimings`, `ObserveMemory`, `ObserveChannels`, `ObserveBuses`, `ObserveWatches`, `ListVariables`, `ClearMeasurements` | unchanged for every field looper-py reads | regenerate only |

### 1.4 Facts measured against the live server (blinky, `--no-build`)

- With `--virtual`: `ObserveRun.mode = CLOCK_MODE_HELD`, `now_us = 0`.
  `ControlRun{run_for_us: 500000}` returns after ~3 ms with `state.now_us =
  500000`, `target_us = 0` – **today it blocks until the run is done**,
  although the schema says "returns at once" and `target_us` exists for a
  run still under way. The client must handle both.
- **Without `--virtual` (real time)**: `ObserveRun.mode` also reports
  **`CLOCK_MODE_HELD`** while `now_us` runs with the host clock (1.05 s
  after 1 s); `run_for` is refused (`REFUSAL_INVALID`, "the clock runs in
  real time and cannot be advanced"), `hold` is refused (`REFUSAL_INVALID`).
  Only `Description.capabilities` differs (`CAPABILITY_PACED` present).
  **Root cause (verified by the coordinator):** the `blinky.exe` in
  `examples/blinky/build/` was built 2026-11-01 11:33, before looper-rt
  gained pace reporting (14:12, "implement pace control";
  `looper_report_pace` fills `pace_mode` on every response). The old
  firmware leaves `pace_mode` at 0 (`PACE_MODE_UNSPECIFIED`), and
  looper-core's `translation.to_pace`
  (`src/looper_core/infrastructure/ipc/translation.py:114-122`) maps "not
  reported" to `PaceMode.HELD` – wrong for a runtime started on the host
  clock. A freshly built firmware should report PACED ×1.0 (not re-verified:
  the exe was locked). Fixed in step 0; Q1 is decided.
- The control protocol version (`LOOPER_PROTOCOL_VERSION 2u` in looper-rt,
  `PROTOCOL_VERSION = 2` in core's `protobuf_session.py`, checked on
  `COMMAND_HELLO`) was last raised on 2026-10-29 (`c34e08b`); the event log,
  run control and pace reporting were added after it without a bump, so a
  stale firmware is not recognised as stale.
- The event log is filled by a **drain thread every 50 ms of host time**
  (`event_drain.py`). Right after a `run_for`, `ReadEvents` may still answer
  an empty batch with `sim_now_us` behind `now_us`; in the probe it took
  ~20 polls / 0.27 s host time to read 1 s of blinky (6 593 samples,
  9 exchanges). A reader must wait until `sim_now_us` reaches the window's
  end.
- `ReadEvents` applies the `filter` **after** cutting the page
  (`max_events_per_batch = 2000`): a filtered page can be empty while more
  events follow. Progress must be judged by `next_event_seq`, never by "the
  page was empty".
- After `ClearRecordings`, `ObserveRun.next_event_seq` is the first number
  of the new epoch. Reading the new epoch from `from_event_seq = 0` answers
  a `Lost(RETENTION)` for the discarded range – not a real loss.
- `ClearRecordings{epoch: 0}` skips the epoch check (implementation, not
  stated in the schema).
- `DrivePin` toggle on an input: `ack` with `applied_at_us`; on an output:
  `REFUSAL_INVALID` "unknown pin, or the pin is an output".
- `ListVariables` for blinky is ~10 MB – `MAX_MESSAGE_BYTES = 64 MB` stays
  necessary.

---

## 2. Inventory of the public API

Legend: **Keep** – unchanged; **Adapt** – same name and meaning, new
implementation on v3 (how); **Remove** – core dropped the feature (where).
"Public" = exported from `looper`, reachable on those objects, or used by
user tests as an extension point (`Inspector`, domain values).

### 2.1 `looper` (top level)

| Name | Verdict | How / why |
| --- | --- | --- |
| `run(definition, *, virtual, build, looper_cli)` | Keep | `looper-cli run` still takes `--virtual`, `--no-build`, `--listen`, `--stop-on-stdin-close`, `--quiet` (checked with `run --help`). |
| `connect(address)` | Adapt | Same signature. `UNIMPLEMENTED` on `Describe` becomes `ContractMismatchError` ("the server does not speak contract version 3") instead of "unreachable" – restores the existing error, no new feature. |
| `Simulation`, `Expectations` | Adapt | see 2.2, 2.3 |
| `ExpectationReport`, `Outcome` | Keep | |
| `Pin`, `Channel`, `Bus`, `Variable`, `Watch` | Keep | every field still comes from the contract unchanged (`PinView.level` is still "low"/"high"). New v3 fields (watch scaling, bus form facts) are **not** added. |
| `BusMessage` | Keep | translated into the nested `BusMessage` of `BusMessageRequest`. |
| `Signal` | Keep | |
| `TimeMode` | **Remove** (replaced, see Q2) | `Description.time_mode` was removed in core `9d1c3c0` (field 3 reserved). Recommended replacement: `ClockMode` with `HELD`, `PACED`, `MAX` (the contract's `ClockMode`), read live. |
| `SimulationRefusedError` | Adapt | now also raised for an `Ack` with `refusal != REFUSAL_NONE`; message = `refusal_text`, else the refusal's name. |
| `SimulationUnreachableError` | Keep | every status other than FAILED_PRECONDITION (and UNIMPLEMENTED on attach). |
| `ContractMismatchError` | Adapt | see `connect`. |
| `LooperCliError` | Keep | |
| `__version__` | Adapt | `0.1.0` → `0.2.0` (the API changes in a breaking way: `time_mode`). |

### 2.2 `Simulation`

| Member | Verdict | How / why |
| --- | --- | --- |
| `description` | Adapt | `Description` without `time_mode` (see 2.4). |
| `firmware_name`, `definition_path` | Keep | |
| `time_mode` | **Remove** → `clock_mode` (Q2) | read from `ObserveRun.mode` on each access, because in v3 the mode can be switched by any client while the simulation runs. |
| `simulated_seconds` | Adapt | `ObserveRun.now_us / 1e6`. Still a float in seconds for users. |
| `advance(seconds)` | Adapt | `ControlRun{run_for_us: round(seconds * 1e6)}`; refusal in the Ack → `SimulationRefusedError` (same as the old FAILED_PRECONDITION). If the reply's `state.target_us != 0` (run still under way – allowed by the schema, not done by today's server), poll `ObserveRun` until `target_us == 0`. `round` instead of `int`: `0.57 * 1e6` is `569999.99…`. |
| `expect()` | Keep | |
| `pins()`, `channels()`, `buses()`, `pin(name)`, `channel(name)`, `bus(name)` | Keep | |
| `toggle_pin(pin_id) -> str` | Adapt | `DrivePin{pin_id, toggle}`; returns `"high"`/`"low"` from `PinDriven.high`. The client no longer reads the pins first; an unknown or output pin is the server's refusal ("unknown pin, or the pin is an output") instead of the client's "the firmware registered no pin N". |
| `apply_signal(channel_id, signal)` | Adapt | `SignalRequest` as before, without `when`; check the Ack. |
| `send_bus_message(message)` | Adapt | nested `BusMessage`; check `BusMessageReply.ack`. `summary` is ignored. |
| `variables()` | Keep | `unavailable_reason` → refusal, as now. |
| `watch_variable(variable_id) -> Watch` | Adapt | unwrap `WatchStarted.watch`, check `.ack`. No scaling is sent (new feature, not added). |
| `write_variable(channel_id, value)`, `remove_watch(channel_id)` | Adapt | check the Ack. |
| `watches()` | Keep | |
| `close()`, context manager | Keep | |

### 2.3 `Expectations` and the subjects

| Member | Verdict | How / why |
| --- | --- | --- |
| `add`, `channel`, `bus`, `call`, `memory`, `stack`, `firmware_is_alive` | Keep | |
| every subject method (`stays_between`, `reaches`, `nothing_refused`, `carried_at_least`, `happened_at_least`, `was_answered`, `happened_at`, `never_allocates`, `peak_below`, `nothing_leaked`, `stays_below`, `no_deeper_than`) | Keep | signatures and report texts unchanged, `within_seconds` stays seconds |
| `evaluate(for_seconds=1.0)` | Adapt | new sequence, section 3 step 4: `ObserveRun` → `ClearRecordings{epoch}` → `ClearMeasurements` → `ObserveRun` (window start: epoch, `next_event_seq`, `now_us`) → let time pass by the mode read at that moment (`HELD`: `run_for`; `PACED`/`MAX`: host sleep; see Q1 for a run another client holds, and for `hold_reason`) → `ObserveRun` (window end `now_us`) → `ObserveTimings` → read `ReadEvents` pages filtered to SAMPLE + EXCHANGE until `next_event_seq` stops moving **and** `sim_now_us >= end`; keep events with `sim_us <= end` → `ObserveMemory`. `MAXIMUM_PAGES` goes: the `sim_us <= end` cut makes chasing impossible; a host-time deadline (e.g. 10 s) for the drain to catch up raises `SimulationUnreachableError`. `epoch_changed` during the read (another client cleared) raises `SimulationRefusedError("the recording was cleared during the window")`. |

### 2.4 Domain values (`looper.domain.model`, not top level but reachable)

| Value | Verdict | How / why |
| --- | --- | --- |
| `Description` | Adapt | drop `time_mode`; keep `contract_version`, `firmware_name`, `definition_path`, `reads_the_build`. |
| `TimeMode` | Remove → `ClockMode` (Q2) | |
| `Sample(channel_id, seconds, value, sequence)` | Adapt | `Sample(channel_id, sim_us: int, value, event_seq: int)`. Contract v3 has no `double seconds` for simulated time; the domain follows it. |
| `Exchange(..., seconds, address, display_address, direction, payload, response, length, accepted, sequence)` | Adapt | `seconds` → `sim_us` (end of the exchange), `sequence` → `event_seq`, `length` ← `payload_length`, `direction` enum → `"outbound"`/`"inbound"` (unchanged strings), `payload`/`response` straight bytes, `address` ← `address_value`, `display_address` formatted here as `0x{address:X}` (the schema assigns formatting to the client; it is report text only, CLAUDE.md §2 "Darstellung"). `was_refused` stays. |
| `Recordings` (two positions) | Remove → `EventPage` | internal page value: `samples`, `exchanges`, `next_event_seq`, `sim_now_us`, `lost_events`, `epoch_changed`. Nothing replaces "two positions" because core has one stream. |
| `CallTiming`, `HeapUsage`, `MemoryUsage`, `Pin`, `Channel`, `Bus`, `Variable`, `Watch`, `BusMessage`, `Signal`, `Outcome`, `ExpectationReport` | Keep | |
| `Observation(samples, exchanges, timings, elapsed_seconds, lost_samples, lost_exchanges, memory)` | Adapt | `elapsed_seconds` stays (a rate is per second); `lost_samples` + `lost_exchanges` → one `lost_events` (Q3); `sample_loss_note` and `exchange_loss_note` both say "and N events the recording could not keep". |
| checks (`ChannelReaches`, `ChannelStaysBetween`, `BusNothingRefused`, `BusCarriedAtLeast`, `CallHappened`, `CallWasAnswered`, `CallRate`, `FirmwareIsAlive`, memory checks) | Keep / Adapt | `ChannelReaches` computes "took" from `sim_us` (integer µs, divided by 1e6 for the text). `BusCarriedAtLeast` stops adding lost events to the count (Q3). Report texts otherwise identical. |

### 2.5 Port and infrastructure (extension points)

| Item | Verdict | How |
| --- | --- | --- |
| `Inspector.describe`, `read_timings`, `read_memory`, `read_pins`, `read_channels`, `read_buses`, `clear_measurements`, `apply_signal`, `send_bus_message`, `list_variables`, `watch_variable`, `write_variable`, `remove_watch`, `read_watches`, `close` | Keep (signature) | adapters change, the port does not |
| `Inspector.simulated_microseconds()`, `advance(microseconds)` | Adapt | → `run_state() -> RunStatus(now_us, clock_mode, epoch, next_event_seq, target_us)` and `run_for(microseconds) -> RunStatus` |
| `Inspector.clear_recordings()` | Adapt | → `clear_recordings(epoch: int) -> None` |
| `Inspector.read_recordings(after_sample, after_exchange)` | Remove → `read_events(epoch, from_event_seq) -> EventPage` | core `9d1c3c0` removed `ReadRecordings` |
| `Inspector.toggle_pin(pin_id, current_level)` | Adapt | → `toggle_pin(pin_id) -> str`; core removed `TogglePin` (`9d1c3c0`), the server toggles |
| `GrpcInspector`, `CONTRACT_VERSION`, `MAX_MESSAGE_BYTES` | Adapt | new calls; one `_acknowledged(ack)` helper turns a refusal into `SimulationRefusedError` |
| `translation.*` | Adapt | one function per v3 message; `recordings_of` → `event_page_of` |
| `LooperCliRun`, `RunCommand`, `program_of`, `address_in`, `LooperCliError` | Keep | |

Nothing that looper-py offers was dropped by core *without* a replacement;
the only feature that disappears in its old shape is the **time mode**
(`TimeMode`, `Description.time_mode`, `Simulation.time_mode`), and with it
the separation of lost samples from lost exchanges.

---

## 3. Steps

Each step ends with `uv run ruff check src tests && uv run mypy && uv run
pytest` unless stated. Per the user's global rule, **nobody commits**; the
user commits each step if they want. Sizes: S < 1 h, M = half a day.

### Step 0 – truthful run mode in looper-core (S, looper-core)

Part of this repair, at the user's request, and first because the server
owns the truth (CLAUDE.md §2). No schema change, so no new copy.

**Fallback to the start mode.** When the runtime does not
report a pace (`pace_mode == PACE_MODE_UNSPECIFIED`), core uses the mode
the session was started in, exactly like the default
`SimulationSession.read_pace` (`domain/ports/simulation_session.py:388-394`):
`TimeMode.REAL_TIME` → `Pace.paced(1.0)`, `TimeMode.VIRTUAL` →
`Pace.held()`. Shape: `translation.to_pace` returns `None` (or takes the
fallback `Pace` as an argument) for "not reported" instead of inventing
`HELD`; `ProtobufSession.read_pace` and `set_pace` fill in the session's
start mode. Files: `src/looper_core/infrastructure/ipc/translation.py`,
`src/looper_core/infrastructure/ipc/protobuf_session.py`.
Tests (core): `tests/infrastructure/ipc/` – an unreported pace on a
real-time session reads as PACED ×1.0, on a virtual one as HELD; a
reported pace is taken as reported. Check end to end with the stale
`blinky.exe` still in place: `ObserveRun.mode` is `CLOCK_MODE_PACED`
without `--virtual`, `CLOCK_MODE_HELD` with it.

The control protocol version stays as it is (user decision 2026-11-01):
no bump in looper-rt or looper-core, no staleness warning. A stale
firmware is therefore not detected; `--no-build` runs whatever firmware is
in the build folder, and it must be rebuilt after looper-rt changes (step 6).

Verify (core): `uv run pytest`, `uv run ruff check`, `uv run mypy` there.

### Step 1 – take over the schema (S)

- Copy `looper-core/src/looper_core/presentation/inspector/schema/looper_inspector.proto`
  to `src/looper/infrastructure/contract/looper_inspector.proto`.
- `uv run python scripts/generate_contract.py` (regenerates `_pb2.py`,
  `_pb2.pyi`, `_pb2_grpc.py`; protoc 7.35.1 / grpc 1.85.0 like core's).
- Verify: `uv run pytest tests/test_contract_in_step.py` green;
  `python -c "from looper.infrastructure.contract import looper_inspector_pb2 as c; print(c.CONTRACT_VERSION_CURRENT)"` prints 3.
- Expected and accepted: mypy and the infrastructure tests are red until
  step 4 (they name removed messages). Steps 1–4 are one sitting.

### Step 2 – domain on `sim_us` and one stream (S)

Files: `domain/model/readings.py` (`Sample`, `Exchange`, `EventPage`
instead of `Recordings`, `ClockMode` instead of `TimeMode`, `Description`
without `time_mode`), `domain/model/observation.py` (`lost_events`, notes),
`domain/model/__init__.py`, `domain/checks/channel_checks.py` (`sim_us`),
`domain/checks/bus_checks.py` (Q3).
Tests: `tests/domain/` – add `test_checks.py` cases for `ChannelReaches`
on µs (took 0.25 s from 250 000 µs), loss note wording, `BusCarriedAtLeast`
without lost events. Verify: `uv run pytest tests/domain`.

### Step 3 – port and use cases (M)

Files: `application/ports.py` (2.5), `application/expectations.py` (the
`evaluate` sequence of 2.3, `_read_window` replacing `_read_all`/`_joined`/
`_after`, `round` for µs), `application/simulation.py` (`clock_mode`,
`simulated_seconds`, `advance` with the wait on `target_us`, `toggle_pin`
without the pin pre-read), `src/looper/__init__.py` (exports,
`__version__`).
Tests: `tests/doubles.py` – `ScriptedInspector` speaks the new port (a
scripted `RunStatus`, pages of `EventPage`, a configurable lag of
`sim_now_us`, scripted refusals). `tests/application/test_expectations.py`:
- adapt: every page read; cleared before the window and clock moved (now
  asserts the epoch passed to `clear_recordings` is the one just observed);
  host clock waited out (mode `PACED`); rate from elapsed time; growing
  recording read only up to the window end (by `sim_us`, replaces
  `GrowingInspector`).
- add: an empty filtered page with `next_event_seq` moving does not end the
  read; a log behind the window end is waited for and a stuck one raises
  `SimulationUnreachableError`; `epoch_changed` raises
  `SimulationRefusedError`; lost events show in the note; the mode is read
  per window (HELD → `run_for`, PACED/MAX → host wait, never a mode
  switch); a `hold_reason` is refused before anything is cleared.
`tests/application/test_simulation.py`: adapt `test_time_is_advanced_in_seconds`
(µs rounding, waits while `target_us` set), `test_toggling_a_pin...`
(server toggles), `test_a_pin_the_firmware_never_registered_is_refused`
(refusal comes from the port now), description test without time mode.
Verify: `uv run pytest tests/domain tests/application`.

### Step 4 – gRPC adapter and translation (M)

Files: `infrastructure/grpc_inspector.py` (new calls per 1.3, `_acknowledged`,
`run_for` loop on `target_us`, `read_events` with
`EventFilter(kinds=[EVENT_KIND_SAMPLE, EVENT_KIND_EXCHANGE])`, `max_events`
left 0 = server maximum), `infrastructure/translation.py`
(`description_of`, `run_status_of`, `event_page_of` with `_sample_of` /
`_exchange_of` from `Event`, `lost` summed as `to - from + 1`,
`bus_message_request_of` nested, `watch_of(WatchStarted.watch)`).
Tests: `tests/infrastructure/test_grpc_inspector.py` – the
`ScriptedServicer` answers `ObserveRun`, `ControlRun`, `ReadEvents`,
`ClearRecordings`, `DrivePin` instead of `AdvanceTime`/`ReadRecordings`/
`TogglePin`; adapt the exchange tests (number address formatted as
`0x…`, bytes payload; the "plain number" address test is removed – the
contract no longer sends text); add: an Ack refusal becomes
`SimulationRefusedError` with its text; a refusal without text names the
refusal; FAILED_PRECONDITION still is a refusal; a run still under way is
waited for; `Lost` becomes `lost_events`.
Verify: full `ruff`, `mypy`, `pytest` green except the integration tests.

### Step 5 – composition root (S)

File: `starting.py`: on attach, a `SimulationUnreachableError` that came
from `UNIMPLEMENTED` on `Describe` becomes `ContractMismatchError` (the
adapter maps `UNIMPLEMENTED` to a distinct internal signal, or `starting`
checks it). Test: in `tests/infrastructure/test_grpc_inspector.py` a server
without the v3 service → `ContractMismatchError`.

### Step 6 – integration and end-to-end (S)

File: `tests/integration/test_blinky.py`: `time_mode is TimeMode.VIRTUAL`
→ `clock_mode is ClockMode.HELD`; everything else should pass unchanged
(that is the point). Run:

```console
# looper-py, against a neighbouring looper-core (builds blinky; no blinky.exe may be running)
$ uv run pytest tests/integration -v
```

Manual end-to-end without a build, as the user asked for, against a server
in a terminal (fixed port so a script can find it):

```console
# terminal 1, in looper-core
$ uv run looper-cli run --no-build --virtual --listen 127.0.0.1:50051 examples/blinky/looper.toml
# terminal 2, in looper-py
$ uv run python -c "import looper; s = looper.connect('127.0.0.1:50051'); \
  print(s.firmware_name, s.clock_mode, s.simulated_seconds); \
  c = s.expect(); c.firmware_is_alive(); c.call('adapter_blinky_gpio_set').happened_at_least(2); \
  c.stack().no_deeper_than(64); r = c.evaluate(1.0); print(r.summary)"
```

And through `run` with the module form the integration test uses:
`looper.run(".../examples/blinky/looper.toml", virtual=True, build=False,
looper_cli=("uv","run","--no-sync","--project",CORE,"python","-m","looper_core.presentation.cli.main"))`.
Also once without `--virtual` (real time): `evaluate(1.0)` must wait about
one host second and pass `firmware_is_alive` – this is the check for Q1.
With `--stop-on-stdin-close` (the user's command) the server stops as soon
as its stdin closes, so it suits `looper.run`, not a second terminal.

**`--no-build` starts whatever firmware is in `examples/blinky/build/`.**
After any looper-rt change it must be rebuilt once –
`uv run looper-cli build examples/blinky/looper.toml` or a `run` without
`--no-build` – with no blinky running (the GUI locks `blinky.exe`).
Otherwise the end-to-end check measures an old runtime: that is exactly how
the false `CLOCK_MODE_HELD` of 1.4 arose.

### Step 7 – repository notes (S)

`README.md` tables and `CLAUDE.md` §1/§4 wording that names removed calls
(see section 4) – content only where code names changed; prose is the docs
agent's. `pyproject.toml` version `0.2.0`.

### Keeping the copy in step (the workflow, unchanged in shape)

1. A change starts in looper-core: schema, bindings there
   (`uv run python scripts/generate_inspector_contract.py`), server, tests.
2. Copy the file here (same path as step 1), then
   `uv run python scripts/generate_contract.py`.
3. `tests/test_contract_in_step.py` compares byte-for-byte (line endings
   normalised) with `../looper-core` or `$LOOPER_CORE`, and skips without a
   checkout – the same rule as looper-rs `tests/contract_in_step.rs`.
4. `CONTRACT_VERSION` comes from the bindings; a version bump in core makes
   `connect` refuse an old server and vice versa – after step 5 also when
   the package name changed.

Recommendation: run looper-py's `test_contract_in_step.py` whenever the
schema in core changes, as looper-rs does; the two clients went out of step
here because only one of them was updated.

---

## 4. Documentation to change (list only, for the docs agent)

- `README.md`: example and tables (`time_mode` → `clock_mode`;
  `advance` refused unless the clock is held; refusals now come with the
  server's text; "Method not found" no longer appears); the paragraph on
  `evaluate` (one clear for every client, a new epoch).
- `docs/concepts.md` §3 "A virtual clock…": held / paced / max instead of
  virtual / real time; `advance` = run for a span on a held clock; the
  refusal text; §"Errors" list.
- `docs/getting-started/first-test.md`: `simulation.time_mode.value` and
  the printed `blinky virtual`; the toggle refusal message.
- `docs/guides/expectations.md`: the window (`sim_us`, exactness on a held
  clock, how loss is reported now – one count of events), `reaches`
  measured in whole microseconds.
- `docs/guides/pytest.md`: fixture text "virtual clock" wording.
- `docs/guides/variables.md`: watch/write/remove now acknowledged; refusals.
- `docs/troubleshooting.md`: `ContractMismatchError` example (version 3 vs
  2, and the "does not speak contract version 3" case); refusal messages
  (`unknown pin, or the pin is an output`, `the clock runs in real time and
  cannot be advanced` / `hold the simulation first…`); the build failing
  because a running blinky.exe locks the file (seen in this diagnosis):
  wait for that run or stop its server, then build again;
  `build=False` running a stale firmware (rebuild after looper-rt
  changes; nothing detects it); `evaluate` on a
  clock another client holds or paces, and while a debugger holds the
  firmware.
- `docs/reference/api.md` and `docs/reference/expectations.md`: `ClockMode`
  instead of `TimeMode`, `Description` fields, `Sample`/`Exchange` fields.
- `docs/recipes/bus.md`, `memory.md`, `sweeps.md`, `input-reaction.md`,
  `measurement-path.md`, `periodic-task.md`, `stack.md`,
  `hollow-adapter.md`: check each for `seconds`, `time_mode`, refusal
  texts, loss notes.
- `docs/draw_figures.py`: `lockstep.svg` and `window-edges.svg` describe the
  virtual clock and the window edges; relabel to held clock and `sim_us`.
- `CLAUDE.md`: §1 infrastructure line unchanged; mention that the contract
  is version 3 and that changes are acknowledged (one line).
- `docs/_build/` is a stale build output in the tree; regenerate or delete
  (user's choice).

---

## 5. Risks and open questions

**Q1 – How does `evaluate` know the clock runs by itself?** **Decided.**
The false `CLOCK_MODE_HELD` came from a stale firmware plus core's
"unreported = HELD" default (1.4); step 0 fixes core, so looper-py trusts
`RunState.mode` and nothing else. No workaround from capabilities, no
"try `run_for`, sleep on refusal".

The run state is **shared between clients**: the GUI (or another test) may
hold a simulation started in real time, pace one started held, or a
debugger may stop the firmware (`hold_reason`). `evaluate` therefore reads
the mode at the start of every window, never once at attach, and
recommended behaviour is:
- `HELD` (on purpose by anyone, or `--virtual`): the window is a
  `run_for` of exactly `for_seconds` – the test lets time pass itself, as it
  did on a virtual clock. It does **not** switch the mode back, and does not
  wait for someone else to release it (a held clock never moves by itself,
  so waiting would hang).
- `PACED` / `MAX`: wait out `for_seconds` on the host, cut the window by
  `sim_us`, and compute rates from the simulated time that passed (as
  before on the real clock).
- `hold_reason` not empty (debugger): `SimulationRefusedError` with that
  reason, before clearing anything.
- The mode changes during the window (another client switches it): the
  window's elapsed time is still `now_us` after minus before, so rates stay
  right; a `run_for` refused with `REFUSAL_WRONG_MODE` becomes
  `SimulationRefusedError`. Not retried.
- `Simulation.advance` keeps its meaning: only on a held clock, refused
  otherwise.

**Q2 – What replaces `TimeMode` / `Simulation.time_mode`?** **Decided: (a).**
Core removed `Description.time_mode` in `9d1c3c0`; the concept is now the
run mode, which any client can switch while the simulation runs.
Options: (a) remove `TimeMode` and `time_mode`, add `ClockMode` (HELD,
PACED, MAX) and `Simulation.clock_mode`, read live; (b) keep the names as a
shim mapping HELD → VIRTUAL, PACED/MAX → REAL_TIME; (c) remove without a
replacement. **Decision (user): (a)**, no shim: the library is 0.1.0, its
users are the user's own tests, and VIRTUAL/REAL_TIME would mislabel MAX.
It is a rename of an existing feature, not a new one. The `run(virtual=…)`
argument stays because `looper-cli run --virtual` stays.

**Q3 – Lost events have no kind.** **Decided as recommended.** `Lost` names ranges of `event_seq` and
`sim_us`, not whether samples or exchanges were lost, so `lost_samples` /
`lost_exchanges` cannot be kept. Today `BusCarriedAtLeast` counts lost
exchanges in the test's favour. **Recommendation:** one `lost_events`
count, shown in the note of channel and bus checks; `BusCarriedAtLeast` no
longer adds it (a lost sample must not make a bus check pass). On a held
clock the server is lossless (schema), so this only matters in real time.
Alternative: fail every check of a window with losses – stricter, but a
behaviour change; not recommended now.

**Q4 – `ReadEvents` with a short host poll, or `Subscribe`?** **Decided as recommended.** The log is
filled every 50 ms of host time, so the reader waits for `sim_now_us` to
reach the window end. **Recommendation:** `ReadEvents` (the schema calls it
"for tools and tests") with a 20 ms poll and a 10 s deadline – host time for
transport only, never for content (the window is cut by `sim_us`).
`Subscribe` would avoid the poll but brings stream cancellation and a
subscriber slot (`MAXIMUM_SUBSCRIBERS`) into a library that does not need
it.

**Q5 – `ClearRecordings` epoch.** **Decided as recommended:** pass the epoch read by
`ObserveRun` just before; a `REFUSAL_WRONG_EPOCH` (another client cleared in
between) becomes `SimulationRefusedError`. Do not rely on epoch 0 skipping
the check – it is not stated in the schema.

**Q6 – `ControlRun` blocks today, the schema says it returns at once.** **Decided as recommended.**
Implement the wait on `target_us` (poll `ObserveRun`) so looper-py keeps
working when core makes it asynchronous. Risk: low; covered by a unit test.

**Q7 – The integration test builds blinky.** A running blinky (e.g. the
GUI) locks `blinky.exe` and the build fails with a misleading
`LooperCliError` (seen today). **Decision (user):** no switch to skip the
build; the test stays as it is. If a blinky is running, wait for it or stop
that server first; the troubleshooting page says so. Separately,
`--no-build` / `build=False` uses whatever firmware lies in the build
folder, and it must be rebuilt after every looper-rt change; a stale one is
what produced the false `HELD` of 1.4, and nothing detects it (the protocol
version stays as it is).

**Risks.**
- Window start in real time: events drained between `ClearRecordings` and
  the following `ObserveRun` are missed (at most one drain, ≤ 50 ms of host
  time). On a held clock nothing runs in between, so it is exact. Accept.
- Event volume: 1 s of blinky is ~6 600 events (4 pages); a 60 s window of
  a busy firmware can be several hundred thousand events and seconds of
  protobuf decoding in Python. Accept for now; filtering by channel/bus ids
  of the declared checks is a later optimisation, not part of this repair.
- The address text in a bus report changes from the server's format
  (`0x701`) to `0x{:X}` for every bus kind (e.g. `0x50` for I2C, `5` would
  have been plain for UART/SPI before). Visible only in failure texts.
- `toggle_pin` on an unknown pin now says the server's text instead of
  "the firmware registered no pin N". Accept (same exception type).
- Further core changes during the repair would require another copy; the
  contract test will say so.
