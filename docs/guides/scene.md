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
```

On a virtual clock nothing happens between your calls -- the firmware is
held. Let it run where it matters: after start-up, after changing an input,
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

A bus the simulation does not model, or one that takes no messages, is
refused:

```text
looper.SimulationRefusedError: that bus is not one the simulation models
```

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
