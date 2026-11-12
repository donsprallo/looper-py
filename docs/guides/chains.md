# Chains from a test

A [trigger](triggers.md) tells you *when* something happened. A **chain** also
*does* something at that instant: it answers a frame, presses a button, makes a
sensor stick, cuts the power -- inside the simulation, in the same simulated
microsecond, with no poll between. This guide is the Python side of chains: the
builders on `looper.SignalGraph`, reading what a chain did, switching a chain,
the `Sequence` that lets a chain judge a run, and `export_chain`. What a block
means, what is free and what is Pro is told once, in the {learn}`manual
<manual/chains.html>`; for a walk-through on a small firmware see {learn}`Test a chain
on the CAN bus <guides/test-a-chain.html>`.

```{admonition} What is free and what is Pro
:class: important
Building and running chains is **free**, with these exceptions, which are
**looper Pro**: `reply` (every reply), the `fields` of `BusSend` and `BusReply`,
`sequence`, `inject_fault`, `export_chain`, and a `send` placed behind a
`BusReceived`. Without a licence the server **keeps** such a chain and does not
run it; `simulation.chains()` says why in `ChainBlockState.problem`. Switching a
group that holds a Pro part **on** raises `looper.ProFeatureLockedError`.
Switching it off is always allowed.
```

## A chain is a part of a signal graph

Chains are built with the same `SignalGraph` that drives analog inputs, and sent
with the same call:

```python
import looper

STATUS, ORDER = 0x100, 0x101


def status_watch(bus_id: int) -> looper.SignalGraph:
    """Mark every status frame, and every gap of more than a second."""
    frame = looper.BusReceived(bus_id, STATUS, direction=looper.Crossing.FROM_FIRMWARE)
    gap = looper.BusTimeout(bus_id, STATUS, duration_us=1_000_000, after_first_message=True)
    return (
        looper.SignalGraph()
        .when("status", frame, group="watch")
        .mark("seen", "status", after="status", group="watch")
        .when("silent", gap, group="watch")
        .mark("missing", "no status", after="silent", group="watch")
        .group("watch", "Status watch")
    )


bus_id = simulation.bus("CAN1").bus_id
simulation.apply_signal_graph(status_watch(bus_id))
simulation.advance(2.0)
```

Each builder takes a **key** that names the block, an optional `after=` key (the
block whose `fires` output is linked to this block's first input) and an optional
`group=` key. Keys are what a test calls a block and what `simulation.chains()`
reports it by. A `.group(key, name, enabled=True)` names a chain and gives it a
switch.

`apply_signal_graph` checks the chains as a whole. A chain that has a problem is
**kept and not run**, and the rest of the graph is applied; read the problem with
`simulation.chains()`.

## The builders

Conditions:

| Builder | Block |
| --- | --- |
| `.when(key, condition, group="", min_gap_us=0)` | any condition: `Edge`, `Pattern`, `Width`, `Quiet`, `Value`, `BusReceived`, `BusTimeout`, `Clock`, `Start`, `Interrupt`, `ResetSeen` |
| `.threshold(key, looper.Threshold(signal, level, hysteresis, direction, check_us))` | fires when the signal node `signal` crosses a level, with hysteresis; `check_us` 0 leaves the check time to the server |

`Edge`, `Pattern`, `Width`, `Quiet` and `Value` are those of the [triggers
guide](triggers.md#conditions). The others:

```python
looper.BusReceived(bus_id, address, address_mask=0, direction=looper.Crossing.EITHER, pattern=b"")
looper.BusTimeout(bus_id, address, duration_us=100_000, after_first_message=False)
looper.Clock(period_us=100_000, phase_us=0)       # at the phase, then every period
looper.Start(first_life_only=False)               # at 0 s and after every reset
looper.Interrupt(source_id, on_entry=False)       # pending; with on_entry: the handler entered
looper.ResetSeen(cause=0)                         # a life begins after this reset cause; 0 any
```

`Crossing` is `FROM_FIRMWARE`, `TO_FIRMWARE` or `EITHER`. `cause` is the
contract's number: 1 power-on, 4 pin, 5 brown-out (and the others the server
knows).

Logic:

| Builder | Block |
| --- | --- |
| `.delay(key, delay_us, after="", group="", while_waiting=WhileWaiting.QUEUED)` | each event goes on later; `QUEUED`, `RESTART` or `DROPPED` for one that comes meanwhile |
| `.counter(key, n, after="", group="", only_nth=False)` | every n-th event, or only the n-th. Counts from 0 |
| `.once(key, after="", group="")` | the first event, no more until switched on again |
| `.any_of(key, *sources, group="")` | **Or**: an event from any of the sources |
| `.all_of(key, *holding, group="")` | **And** of the states (`holds`) of the blocks it names; fires when all begin to hold |
| `.gate(key, after, open_while, group="")` | events of `after` go on only while the state of `open_while` holds |
| `.logic(key, kind, after="", group="")` | `once`, `and`, `or` or `gate` by name, without the shortcuts' links |
| `.sequence(key, Sequence(...), after="", group="")` | looper Pro; see [below](#a-chain-that-judges-the-run) |

Actions:

| Builder | Block |
| --- | --- |
| `.send(key, looper.BusSend(bus_id, address, payload, extended=False, text="", fields=(), length=0), after=...)` | a message on CAN, or text on UART |
| `.reply(key, looper.BusReply(bus_id, address, payload, answer_after_us=0, fields=(), length=0), after=...)` | looper Pro. Answers the message a `BusReceived` fired on |
| `.set_pin(key, looper.SetPin(pin_id, looper.PinDo.PRESS, press_us=50_000), after=...)` | `PinDo.HIGH`, `LOW` or `PRESS` (the pressing level for `press_us`) |
| `.mark(key, text, after=...)` | a marker on Logic's ruler |
| `.hold(key, after_us=0, after=...)` | holds the simulation |
| `.switch_signal(key, looper.SwitchSignal(node=, channel_id=, do=, to=, over_us=), after=...)` | start, stop, step or ramp a generator, set a value, hold an input |
| `.inject_fault(key, looper.Fault(kind, ...), after=...)` | looper Pro |
| `.raise_interrupt(key, source_id, after=...)` | makes a source pending |
| `.reset_firmware(key, cause=4, after=...)` | resets as the reset pin (4), a power-on (1) or a brown-out (5) |

`.link(from_node, to_node, from_port=0, to_port=0)` joins ports directly. The
shortcuts `after=`, `any_of`, `all_of` and `gate` link for you. Ports are
numbered from 0 in the order the block lists them; `holds` is output 1 of a
condition or an **And**.

### Answering a frame (Pro)

```python
def status_answer(bus_id: int) -> looper.SignalGraph:
    """Answer every status frame with an order for expander pin 3, 5 ms later."""
    frame = looper.BusReceived(bus_id, STATUS, direction=looper.Crossing.FROM_FIRMWARE)
    answer = looper.BusReply(bus_id, ORDER, bytes([3, 1]), answer_after_us=5_000)
    return (
        looper.SignalGraph()
        .when("status", frame, group="answer")
        .reply("order", answer, after="status", group="answer")
        .group("answer", "Status answer")
    )
```

A `BusReply` without a `BusReceived` before it is refused (*Bus reply answers a
received message. Link a Bus received to when.*). A `send` behind a `BusReceived`
is looper Pro too -- anything that answers what it saw is -- so the free way to
put a message on a bus is a `send` that a clock, a pin edge or a threshold
fires.

### Message fields (Pro)

A message can be built from fields instead of fixed bytes:

```python
fields = (
    looper.Field("rpm", start_bit=0, length=16, signal="speed", scale=0.25),
    looper.Field("counter", start_bit=56, length=4, count=True),
    looper.Field("echo", start_bit=8, length=8, request_bit=8),   # reply only
    looper.Field("mode", start_bit=16, length=8, constant=2),
)
looper.BusSend(bus_id, 0x321, fields=fields, length=8)
```

`signal=` names a signal node of the same graph (its value is scaled:
`raw = round((value - offset) / scale)` and **clamped** to the field's range);
`count=True` is a counter that starts at 0 and adds 1 per message; `request_bit=`
quotes the received message at that bit; otherwise the field is `constant`.
`big_endian` and `is_signed` set the order and the sign. Bits are numbered as a
DBC does. Fields that overlap or reach past `length` are refused.

## Reading what a chain did

```python
for block in simulation.chains():
    print(block.key, block.installed, block.fires, block.state_text, block.problem)
```

`simulation.chains()` returns one `ChainBlockState` per block, in the server's
words: whether it runs (`installed`), how often it fired or acted (`fires`),
when (`last_fired_at_us`), its chip (`state_text`, such as `✶ fired 3× · last
1.500000 s`), what it watches for or does (`summary_text`) and **why it does not
run** (`problem`), which is empty when it does. The blocks of the Logic triggers
are in the list too, keyed `logic:<trigger_id>:condition`.

```python
states = {state.key: state for state in simulation.chains()}
assert states["seen"].fires == states["status"].fires
assert states["silent"].fires == 0
```

```{note}
A block counts when it fires. With a *Delay* or a reply time the action lands
later than its condition; `advance` past it before you read.
```

## Switching a chain

```python
simulation.switch_chain("answer", on=False)
simulation.advance(1.0)
simulation.switch_chain("answer", on=True)    # installs it afresh: counts from 0, a Once fires again
```

`group` is the group's key or its name. Switching on a group that holds a Pro part
without a licence raises `looper.ProFeatureLockedError` with the server's
sentence; so does a group that does not fit in the runtime's table (*Too many
blocks for the runtime* ... as a `SimulationRefusedError`). A fault a group
injected ends when the group is switched off.

## A chain that judges the run

A `Sequence` (Pro) is a chain whose steps are the test: it does something,
waits, waits *for* a thing, expects *no* thing, and ends in *done* or *failed*.
`run_until_chain` lets the simulation run until it has ended:

```python
button = simulation.pin("BUTTON_MODE")
led = simulation.pin("LED_STATUS")

steps = looper.Sequence(
    (
        looper.Step(looper.StepKind.DO, "press"),
        looper.Step(looper.StepKind.WAIT_FOR, "lit", 1_000_000),
    )
)
graph = (
    looper.SignalGraph()
    .group("press", "Press until lit")
    .when("tick", looper.Clock(period_us=100_000), group="press")
    .sequence("test", steps, after="tick", group="press")
    .set_pin("push", looper.SetPin(button.pin_id, looper.PinDo.PRESS, 50_000), group="press")
    .when("rises", looper.Edge(led.pin_id, looper.Polarity.RISE), group="press")
    .link("test", "push", from_port=looper.step_port(steps, 0))
    .link("rises", "test", to_port=looper.step_port(steps, 1))
)
simulation.apply_signal_graph(graph)

result = simulation.run_until_chain("Press until lit", timeout_s=2.0)
assert result, result.failure_text
```

A `Step` is `Step(kind, label, duration_us)`. `StepKind.DO` passes an event on
from an output of its own; `WAIT` waits `duration_us`; `WAIT_FOR` waits for an
event at an input of its own and fails when `duration_us` (the limit, 0 none)
runs out; `EXPECT_NONE` fails if an event comes within `duration_us`.

The ports follow the steps in order: input 0 is `start`; outputs 0 and 1 are
`done` and `failed`; every `DO` adds an output from 2 and every `WAIT_FOR` and
`EXPECT_NONE` an input from 1. `looper.step_port(sequence, step_index)` gives the
number of a step's port, so that you do not count: above, step 0 (the `DO`) is
output 2 and step 1 (the `WAIT_FOR`) is input 1. A `WAIT` has no port and
`step_port` raises `IndexError` for it.

```{figure} ../images/chain-run-until.svg
:alt: A time axis in slices of 10 ms of simulated time. After each slice the Sequence is read. It ends inside the fourth slice, and run_until_chain returns at the end of that slice.

`run_until_chain` runs in slices and reads the Sequence after each.
```

`run_until_chain(name, timeout_s=10.0)` takes the group's **name or key** and
returns a `ChainRun` with `passed`, `failure_text` and the final `sequence` state
(`step`, `step_count`, `step_text`). `bool(result)` is `passed`. It runs the
simulation in slices of **10 ms of simulated time**, reading the Sequence after
each, so it stops up to 10 ms after the Sequence ended -- not at the exact
microsecond; the times in the server's `failure_text` are exact. When time runs
out, `passed` is false and the text says the chain *neither passed nor failed
within … s*. `ValueError` says there is no Sequence of that name.

## Doing things to the signals

```python
graph = (
    looper.SignalGraph()
    .generator("heat", looper.Signal(waveform="sine", offset=40.0, amplitude=5.0, frequency_hz=1.0))
    .when("hot", looper.Clock(period_us=2_000_000, phase_us=2_000_000), group="fault")
    .switch_signal("stop", looper.SwitchSignal(node="heat", do=looper.SignalDo.STOP), after="hot", group="fault")
    .group("fault", "Heater off")
)
```

`SwitchSignal(node=…, channel_id=…, do=…, to=…, over_us=…)` with `SignalDo`
`START`, `STOP`, `STEP`, `RAMP`, `SET` or `HOLD_AT`: `node` names a generator or a
value of this graph; `HOLD_AT` takes `channel_id` instead and holds an analog
input at `to`. A value that feeds a **model parameter** is refused (*X feeds a
model parameter – a chain cannot set it.*): the model would have to be made
again. A value a chain set **survives** the next `apply_signal_graph` when the
node is drawn as before; one you changed with `set_graph_value` begins anew.

`simulation.set_graph_value("setpoint", 3.0)` on a value that feeds no
parameter takes about 0.3 ms, because it sets the number in the runtime without
sending the graph.

Faults (Pro):

```python
looper.Fault(looper.FaultKind.STICK, channel_id=shunt.channel_id, for_us=2_000_000)
looper.Fault(looper.FaultKind.NOISE_ON, channel_id=shunt.channel_id, amplitude=0.2)
looper.Fault(looper.FaultKind.DROP, bus_id=can.bus_id, address=0x123, next=3)
looper.Fault(looper.FaultKind.FLIP, bus_id=can.bus_id, address=0x123, byte_index=0, bit=3)
looper.Fault(looper.FaultKind.ERROR_FRAME, bus_id=can.bus_id)
looper.Fault(looper.FaultKind.POWER_CUT, for_us=10_000)    # also needs the bootloader licence
```

`for_us` of a `STICK` is how long (0: until the group is switched off); of a
`POWER_CUT` it is the time the board stays off. `DROP`, `FLIP` and `ERROR_FRAME`
are for CAN.

Interrupts and resets:

```python
.when("pending", looper.Interrupt(source_id=1))
.raise_interrupt("fake", source_id=1, after="tick")
.when("after_wd", looper.ResetSeen(cause=0))
.reset_firmware("kill", cause=4, after="tick")
```

A chain goes over a reset **with its state** (clock, delay, counter, a running
Sequence, a fault); `Start` fires in every life. See
{learn}`Chains and resets <manual/chains.html#chains-and-resets>`. A chain that resets
the firmware at every start is found as a [reset loop](resets-and-memories.md),
which is reported and does not hold the run unless the project says
`hold_on_loop = true`.

## Export as a test (Pro)

```python
written = simulation.export_chain("press")            # a group's key or name
print(written.file_name)                              # test_press_until_lit.py
print(written.warnings)                               # what could not be carried over
Path(written.file_name).write_text(written.text)
```

`export_chain(group, run_for_s=0.0)` returns a `ChainExport`: the file name, the
text of a pytest that builds the group with exactly the builders above, and the
server's warnings. A chain with a `Sequence` ends in `run_until_chain(...)` and
`assert result.passed, result.failure_text`; one without runs `run_for_s`
(0: 10 s) and checks that no chain has a problem. The file needs a `simulation`
fixture in your `conftest.py`, as [every test of the library does](pytest.md).
Operations and models of the signal graph are **left out** and the warnings say
so; a value is exported with its current value. Without a licence the call
raises `looper.ProFeatureLockedError`.

### Fields from a DBC file

`simulation.read_dbc(path)` has the server read a DBC file – the path is on the
server's disk – and gives its CAN messages with their signals. Reading is free.
The library does not fill a block by itself; take what you need from the
message:

```python
engine = simulation.read_dbc("can/engine.dbc").message("EngineData")
rpm = next(signal for signal in engine.signals if signal.name == "rpm")
fields = (
    looper.Field(rpm.name, start_bit=rpm.start_bit, length=rpm.length,
                 big_endian=rpm.big_endian, is_signed=rpm.is_signed,
                 scale=rpm.scale, offset=rpm.offset, signal="speed"),
)
looper.BusSend(bus_id, engine.identifier, fields=fields, length=engine.length)
```

A `DbcFile` has the `path`, the `messages` in the file's order and a `problem`:
a file that cannot be read is not refused, it comes back with the server's
sentence and no messages. A `DbcMessage` has its `name`, `identifier`,
`extended` (29 bit), `length` in bytes, `cycle_us` (0 when the file does not
say) and `signals`; a `DbcSignal` its `name`, `start_bit`, `length`,
`big_endian`, `is_signed`, `scale`, `offset`, `unit`, and `minimum` and
`maximum` when the file gives them.

## What the chains do not see

A chain acts on what the simulation knows: pins, values, signals, interrupts,
and what is recorded on a bus. What the **firmware** does with a frame is not
a fact; wait for the pin, the variable or the reply it leaves. See the
{learn}`limits <manual/chains.html#limits>`.
