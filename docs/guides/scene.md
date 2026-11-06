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
| `waveform` | `"constant"` | `constant`, `sine`, `square`, `triangle` or `sawtooth` |
| `offset` | `0.0` | the level it swings around; the whole value of a constant |
| `amplitude` | `0.0` | how far it swings either way |
| `frequency_hz` | `0.0` | how often it repeats |
| `phase_degrees` | `0.0` | where in its period it starts |

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
four operations and **models** -- a motor, a filter, a room -- that the
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
| `operation(key, kind, first, second)` | `looper.SignalNodeKind.ADD`, `SUBTRACT`, `MULTIPLY` or `DIVIDE` of two other nodes |
| `value(key, value)` | a node that gives a number a test sets later with `simulation.set_graph_value`; to an input or to a model's parameter |
| `model(key, name, inputs, parameters=None, parameter_sources=None)` | a model the simulation steps; `inputs` in the order the model declares them, `parameters` by name, `parameter_sources` the parameters a value node gives, by name |
| `drive(channel_id, node, output=0)` | the analog **input** that reads one output of a node |
| `probe(name, node, output=0)` | records an output as a trace of its own, without driving anything |

A bare key stands for the first output of a node; `looper.NodeOutput(node,
output)` names another one. Applying a graph **replaces** whatever graph ran
before, for every client -- the window included -- and an input the new graph no
longer drives goes back to its own signal. `SignalGraph()` applied on its own
removes the graph. Whether the graph holds together is the simulation's to say:

```text
looper.SimulationRefusedError: ...
```

comes back for an unknown model, inputs that do not fit it, or a target that is
not an input.

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

How to write a model is described in {core}`Models of your own
<signals.html#models-of-your-own>`; the window builds the same graph in its
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
