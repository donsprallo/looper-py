# What does the firmware do right after an event?

**The question.** When the LED changes, what is the state of the world a
moment later? Or: how often did this pin change during a scenario?

**Why it is worth a test.** An expectation looks at a window of time you
choose. A trigger lets the *simulation* find the moment -- the instant the
condition became true -- and gives you its exact time to measure from.

## How

1. Arm a condition on a pin or a watched variable.
2. `advance` past where it should fire.
3. Read the trigger, and disarm it in a `finally`.

## Example: the LED changes, and the simulation holds just after

A SINGLE trigger fires once and holds the simulation `post_us` later. The
clock stands there, so a window attached to the same simulation shows the
instant too.

```python
import looper


def test_a_single_trigger_holds_the_run_just_after_the_led_changes(simulation):
    led = simulation.pin("LED_STATUS")
    trigger = simulation.triggers.arm(looper.Edge(led.pin_id), post_us=1_000)
    try:
        simulation.advance(2.0)
        fired = simulation.triggers.current(trigger)
        held_at_us = round(simulation.simulated_seconds * 1_000_000)
    finally:
        simulation.triggers.disarm_own()

    assert fired.state is looper.TriggerState.HELD
    assert fired.fires == 1
    assert held_at_us == fired.last_fired_at_us + 1_000
```

`advance(2.0)` returns early, at the hold point, so the simulated time is
read afterwards rather than assumed.

## Example: counting rising edges

A NORMAL trigger never holds, so the whole span runs and `fires` is the count:

```python
def test_the_led_rises_at_least_twice_in_two_seconds(simulation):
    led = simulation.pin("LED_STATUS")
    rising = looper.Edge(led.pin_id, looper.Polarity.RISE)
    trigger = simulation.triggers.arm(rising, mode=looper.TriggerMode.NORMAL)
    try:
        simulation.advance(2.0)
        counted = simulation.triggers.current(trigger)
    finally:
        simulation.triggers.disarm_own()

    assert counted.fires >= 2
    assert counted.state is looper.TriggerState.ARMED
```

## When it fails

`fired.fires` is 0
: The condition did not become true in the time given. The pin is the wrong
  one, the polarity is not what happens, or the span is too short.

`state` is `ARMED` where `HELD` was expected
: A SINGLE trigger that has not fired; the same causes.

`looper.SimulationRefusedError` at `arm`
: The simulation cannot watch for that condition; the message is its own
  sentence. See [Triggers](../guides/triggers.md).

## Variations

- **React to the button.** `Edge(button.pin_id, Polarity.FALL)` fires when
  the button is pressed (it is active low); arm it, then toggle the pin.
- **Measure from the fire.** `fired.last_fired_at_us` is the exact start for
  a calculation of your own, in simulated microseconds.
