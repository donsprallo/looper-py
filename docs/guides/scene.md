# Setting the scene

Before you expect something of the firmware, you usually make something
happen: press a button, apply a current, put a message on a bus, or simply
let it run for a while. This page shows every way to do that.

## Looking around first

The firmware registers its pins, analog channels and buses when it starts.
Ask the simulation what there is:

```python
with looper.run("looper.toml", virtual=True) as simulation:
    for pin in simulation.pins():
        print(pin.pin_id, pin.name, pin.level, "drivable" if pin.is_drivable else "")
    for channel in simulation.channels():
        print(channel.channel_id, channel.name, channel.direction, channel.display_value)
    for bus in simulation.buses():
        print(bus.bus_id, bus.kind, bus.name, "takes messages" if bus.accepts_messages else "")
```

```text
17 LED_STATUS low
4 BUTTON_MODE high drivable
0 SHUNT_CURRENT input no data
1 FILTERED output no data
```

In a test, prefer names to numbers. `pin(name)`, `channel(name)` and
`bus(name)` look one up, and refuse with the names there are when it does not
exist -- so a typo explains itself:

```python
button = simulation.pin("BUTTON_MODE")
shunt = simulation.channel("SHUNT_CURRENT")
```

```text
looper.SimulationRefusedError: the firmware registered no channel named 'SHUNT'; it has FILTERED, SHUNT_CURRENT
```

The values are read when you ask: `simulation.pin("LED_STATUS").level` is the
level now, not when the test started.

## Letting time pass

```python
simulation.advance(1.0)        # one second of simulated time
simulation.simulated_seconds   # 1.0

simulation.advance_microseconds(8_681)   # a bit period, said exactly
```

Seconds go through a float and are rounded to whole microseconds; a test
that already knows the microseconds -- a bit period, a sampling interval, a
timeout the firmware counts in microseconds -- says them with
`advance_microseconds` instead.

On a held clock nothing happens between your calls -- the firmware is
held. `advance` is refused when the clock is not held (`paced` or `max`):
the server says so in its own words, `SimulationRefusedError: the clock runs
in real time and cannot be advanced`. Let it run where it matters: after start-up, after changing an input,
before a check that should not see a transient. `evaluate` lets its own
window pass, so you do not advance for the window itself.

When something outside the simulation has to keep talking to the firmware while
time passes, hand the clock over and take it back: `simulation.pace(10.0)` runs
it at ten times real time, `simulation.run_at_max()` as fast as the computer
allows, and `simulation.hold()` stops it so that `advance` works again.
`simulation.run_state()` says how a paced clock is doing: `pace_ratio`,
`behind_us` (what it owes) and `slipped_us` (what it gave up after a stall, so
that a measurement can tell whether the pace held). How far the clock moves
between two passes of the firmware's loop is the *time model*'s to say; see
[How it works](../concepts.md) and the recipe
[Time models](../recipes/time-models.md).

## Pins

`toggle_pin(pin_id)` drives the opposite of the level a pin is at and returns
the level it drove:

```python
button = simulation.pin("BUTTON_MODE")
button.level                             # 'high' -- released, it is active low
simulation.toggle_pin(button.pin_id)     # 'low'  -- pressed
simulation.toggle_pin(button.pin_id)     # 'high' -- released again
```

Only inputs can be driven -- the firmware drives its own outputs:

```text
looper.SimulationRefusedError: unknown pin, or the pin is an output
```

A pin the signal graph drives is the graph's; `toggle_pin` is refused while it
drives it (see [Comparators and input pins](#comparators-and-input-pins)).

A level stays until something changes it, also across tests that share a
simulation. Release what you pressed at the end of a test, or use a fresh
simulation (see [Tests in pytest](pytest.md#keeping-tests-independent)).

## Analog inputs

An analog input is driven by a *signal*: a definition that the simulation
evaluates every time the firmware reads the channel, against simulated time.
A firmware sampling at 1 kHz therefore sees a clean 1 kHz signal, however
rarely your test looks.

```{figure} ../images/waveforms.svg
:alt: Constant, sine, square, triangle and sawtooth waveforms, with offset, amplitude, frequency and phase.

The waveforms a signal can have.
```

```python
from looper import Signal

shunt = simulation.channel("SHUNT_CURRENT")

# a constant: 5 A from now on
simulation.apply_signal(shunt.channel_id, Signal(offset=5.0))

# 2 A with a 1 A ripple at 5 Hz
simulation.apply_signal(
    shunt.channel_id,
    Signal(waveform="sine", offset=2.0, amplitude=1.0, frequency_hz=5.0),
)

# a 0 .. 4 A square wave at 1 Hz, starting high
simulation.apply_signal(
    shunt.channel_id,
    Signal(waveform="square", offset=2.0, amplitude=2.0, frequency_hz=1.0, phase_degrees=0.0),
)

# back to nothing
simulation.apply_signal(shunt.channel_id, Signal())
```

| `Signal` field | Default | Meaning |
| --- | --- | --- |
| `waveform` | `"constant"` | `constant`, `sine`, `square`, `triangle`, `sawtooth`, `noise`, `pulse`, `rectified_sine`, `sweep` or `table` |
| `offset` | `0.0` | the level it swings around; the whole value of a constant |
| `amplitude` | `0.0` | how far it swings either way; a rectified sine's peak; a table's scale |
| `frequency_hz` | `0.0` | how often it repeats |
| `phase_degrees` | `0.0` | where in its period it starts |
| `duty` | `None` | square and pulse: the share of a period that is high, 0 to 1; `None` is a half |
| `low`, `high` | `None` | pulse: its two levels; `None` takes them from offset and amplitude |
| `rectification` | `""` | rectified sine: `full` (two humps a period) or `half` |
| `sweep_from_hz`, `sweep_to_hz`, `sweep_seconds` | `0.0` | sweep: a sine from one frequency to the other over a time |
| `sweep_spacing`, `sweep_end` | `""` | sweep: `linear` or `logarithmic`; `repeat`, `hold` or `stop` at the end |
| `table_times`, `table_values` | `()` | table: its points, the times in seconds from 0 on and rising |
| `table_between`, `table_end`, `table_time_scale` | `""`, `""`, `0.0` | table: `linear` or `steps`; `repeat` or `hold`; how much slower it plays (0 is 1) |

A field belongs to the waveforms that read it; the others ignore it, and a
choice left empty is the waveform's first option. Two constructors spell the
newer waveforms the way a bench does:

```python
# a gate: 0 .. 3.3 V, 100 Hz, high a quarter of each period
Signal.pulse(0.0, 3.3, 100.0, duty=0.25)

# a supply that dips, from points (seconds, value): 12 V, 7 V for 50 ms, back, and stays
Signal.table([(0.0, 12.0), (0.1, 7.0), (0.15, 12.0), (1.0, 12.0)], between="steps", end="hold")
```

A table plays `offset + amplitude * value`, so `Signal.table` starts at
`amplitude=1.0`. A recording in a CSV or PWL file is read **by the server**,
as the window reads it -- the time first, a value column, commas, semicolons
with a decimal comma, tabs or spaces, a header and a unit row skipped -- and a
long one is simplified so that no point moves further than `max_error`:

```python
signal = Signal.from_csv("mains_dip.csv", simulation, value_column=0, max_error=0.5)

table = simulation.read_table("mains_dip.csv")     # the same, with what the server says
table.summary_text      # '1 024 points · 0 to 2 s · −325 to 325'
table.simplified_text   # '120 000 → 2 310 points, max error 0.4' -- empty when every point is kept
signal = table.signal(amplitude=1.0, offset=0.0, end="hold")
```

`Signal.from_csv` needs a simulation at hand: reading and simplifying stay in
the server, so a test plays exactly the points the window would. The path is
on the server's disk; one that exists where the test runs is sent as a whole
path. A file that cannot be played raises `ValueError` with the server's
sentence, its file and line: `mains_dip.csv, line 14: "abc" is not a number.`
Without a simulation, read the points yourself and pass them to
`Signal.table`.

Whatever cannot be -- a duty outside 0 to 1, a pulse's high below its low, a
sweep of no time, times that do not rise, more than 16 384 points -- is refused
with the server's sentence. The newer waveforms and `duty` need a server whose
runtime moves generators: `"moving_generators" in simulation.description.capabilities`.

A signal on an output channel is refused -- outputs are what the firmware
publishes:

```text
looper.SimulationRefusedError: unknown channel, or the channel is an output
```

The current value of every channel, inputs and outputs, is in
`simulation.channels()`:

```python
simulation.apply_signal(shunt.channel_id, Signal(offset=5.0))
simulation.advance(0.5)
simulation.channel("FILTERED").display_value   # '4.967 A' -- almost there
```

## A graph of signals

`apply_signal` puts one waveform on one input. A **graph** combines them:
generators, what the firmware itself published, a pin, a watched variable, the
operations, comparators and **models** -- a motor, a filter, a room -- that the
simulation steps on its own clock. A model fed from an output channel and driving
an input closes the loop around the firmware, which is how a test puts a plant in
front of a controller.

A `SignalGraph` is a value built step by step; every method returns a new graph:

```python
import looper


def test_the_room_closes_the_loop(simulation):
    duty = simulation.channel("FAN_DUTY")          # what the firmware publishes
    sensor = simulation.channel("TEMP_SENSOR")     # what the firmware reads

    graph = (
        looper.SignalGraph()
        .generator("heat", looper.Signal(offset=40.0))          # a constant 40 W
        .channel("duty", duty.channel_id)                       # the firmware's own output
        .model("room", "Room", inputs=("heat", "duty"))         # a model of the project
        .drive(sensor.channel_id, "room")                       # the input it feeds
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(40.0)                                    # the room warms up
```

| Method | Adds |
| --- | --- |
| `generator(key, signal)` | a node that produces a `Signal` |
| `channel(key, channel_id)` | a node that reads an analog channel; an output closes a loop |
| `pin(key, pin_id)` | a node that reads a pin as 0 or 1 |
| `watch(key, channel_id)` | a node that reads a watched variable, by its watch channel |
| `operation(key, kind, first, second)` | `looper.SignalNodeKind.ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `MIN` or `MAX` of two other nodes; `ABS` of `first` alone |
| `compare(key, reads, level=0.0, hysteresis=0.0, below=False, threshold=None, check_us=0)` | a comparator: 1 while `reads` is above `level` (or below it), else 0; see [Comparators and input pins](#comparators-and-input-pins) |
| `value(key, value)` | a node that gives a number a test sets later with `simulation.set_graph_value`; to an input or to a model's parameter |
| `model(key, name, inputs, parameters=None, parameter_sources=None)` | a model the simulation steps; `inputs` in the order the model declares them, `parameters` by name, `parameter_sources` the parameters a value node gives, by name |
| `drive(channel_id, node, output=0)` | the analog **input** that reads one output of a node |
| `drive_pin(pin_id, node, output=0)` | the digital **input pin** that reads one output of a node: high from 0.5, low below |
| `probe(name, node, output=0, sample_us=0)` | records an output as a trace of its own, every `sample_us` (0: the server's Auto), without driving anything |

A bare key stands for the first output of a node; `looper.NodeOutput(node,
output)` names another one. Applying a graph **replaces** whatever graph ran
before, for every client -- the window included -- and an input the new graph no
longer drives goes back to its own signal. `SignalGraph()` applied on its own
removes the graph. Whether the graph holds together is the simulation's to say:

```text
looper.SimulationRefusedError: ...
```

comes back for an unknown model, inputs that do not fit it, or a target that is
not an input. The message is the server's sentence, word for word.

`simulation.models()` lists the models the project offers, read afresh from its
files, and `simulation.model("Room")` gets one by name -- with its `inputs`,
`outputs`, `parameters` (each with a `default_value`, a `unit` and, where the model
declares them, `lowest` and `highest`), its `kind`
(`linear` or `state`), its `origin` (`project` or `built_in`) and, when it cannot
be used, a `problem`. `model.output("temperature")` is the position of an output,
for `drive(..., output=...)`:

```python
room = simulation.model("Room")
room.inputs                          # ('heat', 'duty')
room.output("temperature")           # 0
[(one.name, one.default_value) for one in room.parameters]
```

How to write a model is described in {learn}`Models of your own
<manual/signals.html#models-of-your-own>`; the window builds the same graph in its
{rs}`signal editor <gui/signals.html>`.

(a-value-that-moves-a-parameter)=
### A value that moves a parameter

A parameter is a constant the model is made with, so a graph that wants to
change one while the simulation runs gives it a **value node**: a number the
test sets, wired to the parameter by name.

```python
def test_a_warmer_room_needs_more_cooling(simulation):
    graph = (
        looper.SignalGraph()
        .generator("heat", looper.Signal(offset=40.0))
        .channel("duty", simulation.channel("FAN_DUTY").channel_id)
        .value("ambient", 20.0)                                 # what the room's surroundings are
        .model("room", "Room", inputs=("heat", "duty"),
               parameter_sources={"ambient": "ambient"})        # parameter "ambient" <- node "ambient"
        .drive(simulation.channel("TEMP_SENSOR").channel_id, "room")
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(90.0)

    simulation.set_graph_value("ambient", 30.0)                 # no graph sent again
    simulation.advance(90.0)
```

`simulation.set_graph_value(node, value)` changes the number without applying
the graph again. The model it feeds is made again with the value and **keeps its
state**, so a motor does not stop and a filter does not jump. It raises
`SimulationRefusedError` if the applied graph has no value node of that key, or
if the value lies outside the `lowest` and `highest` the model declares for a
parameter it feeds; the graph then runs on as it was. Only a value node can be
set; a constant generator that feeds a parameter is read when the graph is
applied. `parameter_sources` overrides the same name in `parameters`.

The window does the same when a slider on a {rs}`panel <gui/panel.html#a-panel-value>`
moves a panel value; see {rs}`Panel values <gui/signals.html#panel-values>`. Setting the value
replaces the graph in the runtime, so a loop that sets one many times a second
costs more than a test needs: set it when the test needs it, and let the
simulation run in between.

## Comparators and input pins

A comparator turns a signal into a level: 1 while its input is above a
threshold, 0 otherwise, or the other way round with `below=True`. With a
`hysteresis` it goes back only once the input has gone that far past the
threshold the other way -- the rule of the chain Threshold. `drive_pin` puts
that level on a digital **input pin**, and the firmware sees its edges as it
would a real pin's, its EXTI included. A mains zero-cross detector, the way an
opto-coupler on a dimmer gives it:

```python
def test_the_zero_cross_pin_pulses_once_a_half_cycle(simulation):
    zc = simulation.pin("ZC")

    graph = (
        looper.SignalGraph()
        .generator("mains", looper.Signal("sine", amplitude=325.0, frequency_hz=50.0))
        .operation("mains_abs", looper.SignalNodeKind.ABS, "mains")
        .compare("zc", "mains_abs", level=15.0, hysteresis=2.0, below=True)
        .drive_pin(zc.pin_id, "zc")
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(0.05)

    check = simulation.expect()
    check.pin("ZC").frequency_between(99.0, 101.0)                 # one pulse a half cycle
    check.pin("ZC").pulse_width_between(305, 325, unit="us")       # |v| < 15 V .. > 17 V
    assert check.evaluate(for_seconds=0.2)
```

`threshold=` names a node to compare with instead of the constant `level`, as
`threshold=looper.NodeOutput("reference", 1)`. `ABS` takes one input; `MIN` and
`MAX` two.

**How exact the edges are** is the server's to say. Behind generators, Abs, Min
and Max the runtime plans each edge ahead to the microsecond. Behind a model
the signal changes only at the model's steps, so the edges fall on them; behind
noise or a divide there is no slope to plan with, and the comparator is checked
every `check_us` (0: Auto, every 10 µs). `simulation.signal_graph()` reads the
applied graph back, and its `pin_target(pin_id)` says how this one does:

```python
target = simulation.signal_graph().pin_target(zc.pin_id)
target.resolution_text      # 'exact to 1 µs', or 'at model steps of 100 µs'
target.edges                # the edges it gave the pin since it was applied
target.fault_text           # why it does not drive the pin now; empty while it does
```

**The graph comes first** on a pin it drives. `simulation.pin("ZC")` says so
with `is_driven_by_graph` and `set_by_text` (`'signal graph'`), and a
`toggle_pin` is refused with the server's sentence instead of doing nothing
quietly:

```text
looper.SimulationRefusedError: ZC is driven by the signal graph, which comes first: this drive does nothing while the graph drives it.
```

When the graph lets go -- a new graph without the pin, or `SignalGraph()` --
the pin keeps its last level; release what the graph left pressed. Only an
input pin can be a target; an output is refused:

```text
looper.SimulationRefusedError: GATE is an output of this firmware; the graph cannot drive it. Choose an input pin.
```

The comparator, Abs, Min, Max and input pins need a server whose runtime plans
the graph's edges: `"graph_edges" in simulation.description.capabilities`.

### Probes on their own clock

A probe records a node's output as a trace of its own, even where nothing the
firmware reads depends on it. `sample_us` says how often; 0 lets the server
choose from what feeds it -- a model's step, else a hundredth of the fastest
generator's period -- and a comparator is recorded at its edges.
`simulation.probe(name)` finds the probe's trace channel, which an expectation
on a channel takes like any other:

```python
graph = graph.probe("LOAD_RMS", "rms", sample_us=1_000)
simulation.apply_signal_graph(graph)

rms = simulation.probe("LOAD_RMS")
check = simulation.expect()
check.channel(rms.channel_id, rms.name).stays_between(158.0, 166.0)
```

A name the applied graph has no probe for is refused with the names it has.

`simulation.model(name)` also says where a library lists a model (`group`, such
as `'Power switches'`), the words that find it (`keywords`) and, for each
parameter, what it does (`description`).

## Generators that move and signal logic

### Linked fields

A generator can take a field from another node instead of from its `Signal`:
`frequency=`, `amplitude=`, `offset=` and `duty=` on `generator` name the node,
as the server's pytest export writes them. A linked frequency is the signal in
Hz, integrated into the phase so that the wave never jumps -- FM; a linked
amplitude is AM. Which fields a waveform lets be linked is the server's to say
(phase never); one it does not is refused with its sentence.

```python
graph = (
    looper.SignalGraph()
    .value("rate", 200.0)
    .generator("gate", looper.Signal.pulse(0.0, 1.0, 1.0), frequency="rate")
    .drive_pin(simulation.pin("TACHO").pin_id, "gate")
)
simulation.apply_signal_graph(graph)
simulation.set_graph_value("rate", 50.0)      # the pulses slow down without a jump
```

### Select and Sample & Hold

`select(key, select, when_1, when_0)` passes `when_1` while `select` gives 0.5
or more, else `when_0`; it switches at the microsecond `select` crosses, without
hysteresis -- a fault injected by a level, a mains that drops out.
`sample_hold(key, reads, trigger, mode=SampleMode.RISING, initial=0.0)` holds
`reads` as it was when `trigger` rose (`FALLING`: fell), or follows it while the
trigger is high and holds it from the falling edge on (`TRACK`); it gives
`initial` until its first sample.

```python
graph = (
    looper.SignalGraph()
    .generator("mains", looper.Signal("sine", 325.0, frequency_hz=50.0))
    .pin("zc", simulation.pin("ZC").pin_id)
    .sample_hold("peak", "mains", "zc", mode=looper.SampleMode.FALLING)
    .value("healthy", 1.0)
    .value("dropped", 0.0)
    .select("supply", "healthy", "mains", "dropped")
)
```

`simulation.signal_graph().node(key)` says what each gives now:

```python
state = simulation.signal_graph()
state.node("supply").passing_port      # 'when 1'
state.node("peak").value               # 312.4 -- None for a node that reports no value
state.node("peak").samples             # samples since the graph was applied
state.node("peak").hover_lines         # ('holds 312.4, sampled at 1.250000 s', ...)
```

### Pins that hold pulses

A model reads a pin at its own steps, so a gate pulse shorter than the step can
fall between two of them. `pin(key, pin_id, hold_pulses=True)` gives a model 1
at its step when the pin was high at any instant since the step before; a
comparator, an input pin or a probe still read the level as it is.

```python
graph = graph.pin("gate", simulation.pin("GATE").pin_id, hold_pulses=True)
graph = graph.model("triac", "Triac", inputs=["mains", "gate"])
```

Select, Sample & Hold and `hold_pulses` need a server whose runtime selects and
samples: `"signal_logic" in simulation.description.capabilities`.

### The delay between two pins

`expect.pin("GATE").after("ZC").between(lo, hi, unit=...)` expects each rising
edge of ZC to be answered by GATE's first rising edge at or after it, within the
range. The server measures it from the pins' recorded edges; the report shows
its sentence:

```python
check = simulation.expect()
check.pin("GATE").after("ZC").between(4.9, 5.1, unit="ms")
report = check.evaluate(for_seconds=0.2)
report.outcomes[0].observed     # 'ZC↑ → GATE↑ 5.00 ms (4.98 ms – 5.02 ms, 20 delays)'
```

`after(reference, reference_edge=Polarity.RISE, edge=Polarity.RISE)` takes
falling or any edges as well. A ZC that GATE did not answer before the next ZC
fails the check, even when every measured delay is within range: a gate that
stays away is not in time. It needs a server that measures delays
(`"pin_delay"` among the capabilities); one that does not refuses the window.

### Starters

`simulation.starters()` lists the small graphs looper-models defines to begin
with -- *Mains with zero-cross*, *Frequency sweep*, *Phase-angle dimmer* --
each with what it needs and whether this firmware has it:

```python
starters = simulation.starters()
starters.names                                   # ('mains_zero_cross', 'frequency_sweep', 'phase_angle_dimmer')
dimmer = starters.named("phase_angle_dimmer")
dimmer.needs_text        # 'an input pin, an output pin and the models Triac and HalfCycleRms'
dimmer.is_available, dimmer.unavailable_text
dimmer.graph_text        # the window's clipboard document, to paste in the editor
```

## Bus messages

On a bus that takes messages -- CAN and UART; on SPI and I2C the firmware is
the master -- a test can put a message on the bus as if another node had sent
it:

```python
from looper import BusMessage

can = simulation.bus("CAN2")
assert can.accepts_messages

simulation.send_bus_message(BusMessage(bus_id=can.bus_id, address=0x701, payload=b"\x01\x02"))

# a 29 bit identifier
simulation.send_bus_message(
    BusMessage(bus_id=can.bus_id, address=0x18FF50E5, payload=bytes(8), extended=True)
)
```

A message carries at most as many bytes as the bus says. On a UART that is 64:
the runtime keeps a bus payload in 64 bytes, and a longer message would arrive
cut short. `send_bus_message` therefore refuses a longer payload instead of
sending it -- send it as several, ten commands of six bytes to a message, say.
`bus.max_payload_bytes` says the limit of a bus.

```text
looper.SimulationRefusedError: UART1 carries at most 64 bytes in one message, and this one has 65; send it as several
```

A bus the simulation does not model, or one that takes no messages, is
refused:

```text
looper.SimulationRefusedError: that bus is not one the simulation models
```

## Reading the traffic back

What crossed the buses is recorded, and a test can walk it rather than only
expect things of it. `exchanges()` yields every recorded exchange, oldest
first, reading on until it has caught up with the recording:

```python
simulation.advance(0.2)

for exchange in simulation.exchanges():
    print(exchange.sim_us, exchange.display_address, exchange.payload.hex())
```

Each exchange carries its `event_seq`, its place in the stream. Keep the last
one and ask again from one beyond it to go on where the reading left off --
between two phases of a test, say:

```python
seen = 0
simulation.advance(0.1)
for exchange in simulation.exchanges():
    seen = exchange.event_seq + 1

simulation.toggle_pin(button.pin_id)
simulation.advance(0.1)
after_the_press = list(simulation.exchanges(since=seen))
```

`read_events(since)` is the same stream a page at a time, for a test that
wants the samples too or wants to stop early: the page carries `samples`,
`exchanges`, how many events were lost, and `next_event_seq`, where the next
page begins. That number, not the length of the page, says where to go on --
a page can be empty while more events follow.

A recording another client cleared while it was being read is refused:

```text
looper.SimulationRefusedError: the recording was cleared while it was being read
```

## Between two phases

A test with two phases does not want the first one in what it reads of the
second. `clear_recordings()` throws the recorded events away and begins the
next recording; `clear_measurements()` does the same for the call counts, the
profile and the heap figures:

```python
simulation.advance(0.5)        # let the firmware settle
simulation.clear_recordings()
simulation.clear_measurements()

simulation.toggle_pin(button.pin_id)
simulation.advance(0.1)
after_the_press = list(simulation.exchanges())
```

Both reach every client of the simulation, a window included: there is one
simulation and one recording. `expect().evaluate(for_seconds=...)` clears the
same way at the start of its window, so a test that only expects things needs
neither call.

Event numbers keep counting across a clear, so one held from before it still
says where to go on.

## What the simulation stands at

`run_state()` reads the run in one go: `now_us` and `clock_mode`, the
recording `epoch`, `next_event_seq` -- a starting point for
`exchanges(since=...)` -- and `hold_reason`, why the firmware answers nothing
right now, such as a debugger stopped at a line.

```python
start = simulation.run_state().next_event_seq
simulation.advance(0.1)
fresh = list(simulation.exchanges(since=start))
```

`timings()` says how often each adapter function was called and how often it
was answered, and `memory()` gives the heap and the deepest the stack went --
both as they stand, rather than over a window the way an expectation sees
them. A build that is not watching its memory refuses `memory()`.

## Putting it together

A typical scene: let the firmware start, change an input, let it react, and
then check the steady state.

```python
def test_an_over_current_makes_the_led_blink_fast(simulation):
    simulation.advance(1.0)                                   # start-up
    shunt = simulation.channel("SHUNT_CURRENT")
    simulation.apply_signal(shunt.channel_id, Signal(offset=5.0))
    simulation.advance(1.0)                                   # let the filter settle

    check = simulation.expect()
    check.channel(simulation.channel("FILTERED").channel_id, "FILTERED").stays_between(4.9, 5.1)
    check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)

    report = check.evaluate(for_seconds=2.0)
    simulation.apply_signal(shunt.channel_id, Signal())       # leave it as it was
    assert report, report.summary
```
