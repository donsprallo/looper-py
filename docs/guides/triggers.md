# Triggers

Sometimes the question is not "what happened in this window" but "what
happens *after* the LED changes" or "how often does this pin fall". A
trigger is a condition you hand to the simulation. The simulation watches for
it and fires at the exact simulated instant it became true -- your test does
not have to catch the moment, it only reads afterwards when and how often it
happened.

```python
led = simulation.pin("LED_STATUS")
trigger = simulation.triggers.arm(looper.Edge(led.pin_id), post_us=1_000)
try:
    simulation.advance(2.0)
    fired = simulation.triggers.current(trigger)
finally:
    simulation.triggers.disarm_own()

print(fired.state, fired.fires, fired.last_fired_at_us)
```

```text
TriggerState.HELD 1 <the simulated microsecond the LED changed at>
```

## The three steps

1. **Arm.** `simulation.triggers.arm(condition, ...)` returns a `Trigger`
   holding the number the simulation gave it.
2. **Let time pass.** `simulation.advance(seconds)` on a held clock. The
   simulation watches while the firmware runs.
3. **Read.** `simulation.triggers.current(trigger)` gives the trigger as the
   simulation holds it *now*: `fires`, `last_fired_at_us`, `state`. What
   `arm` returned is how the trigger stood when it was armed; it does not
   update itself, so read `current` after the time has passed.

Times in a trigger are **simulated microseconds** and end in `_us`, the same
unit as in the event stream. `advance` takes seconds.

## Single and normal

`mode` says what a trigger does when it fires.

`TriggerMode.SINGLE` (the default)
: Fires once, then **holds the simulation** `post_us` later -- for every
  client. A looper-gui window attached to the same simulation stops at the
  same instant. With `post_us=0` the hold is at the fire itself.

`TriggerMode.NORMAL`
: Counts every fire and never holds. The simulation runs on; you read
  `fires` at the end.

```{figure} ../images/trigger-hold.svg
:alt: A timeline. The simulation runs until the trigger fires, goes on for post_us, and is then held; advance returns at that hold point, before the two seconds it was asked for.

A SINGLE trigger fires, goes on for `post_us`, and holds the simulation.
`advance` returns at the hold point, early.
```

On a held clock, `advance` returns early at the hold point. So after a
SINGLE trigger fired, ask the simulation where it is rather than assuming the
whole span passed:

```python
held_at_us = round(simulation.simulated_seconds * 1_000_000)
assert held_at_us == fired.last_fired_at_us + 1_000       # fire time + post_us
```

The hold stops that one run, not the simulation for good: the next
`advance` runs its whole span. The trigger stays `HELD` and does not fire
again until it is disarmed and armed anew.

`trigger.state` tells where a trigger stands: `ARMED` while it watches,
`FIRED` and `HELD` once a SINGLE trigger has fired and the simulation holds
at `hold_at_us`, `DISARMED` after it was stopped, and `REFUSED` if the
simulation turned it down. A NORMAL trigger stays `ARMED` however often it
fires; its `fires` count is what changes. `has_fired` is true from the first
fire, and `is_live` while the trigger still watches or holds.

## Conditions

A condition says what to watch for. Pins are named by `pin_id`, watched
variables by `channel_id`:

```python
led = simulation.pin("LED_STATUS").pin_id
button = simulation.pin("BUTTON_MODE").pin_id
counter = simulation.watch_variable(variable.variable_id).channel_id
```

| Condition | Fires when |
| --- | --- |
| `looper.Edge(pin_id, polarity)` | the pin changes level; `polarity` is `Polarity.RISE`, `FALL` or `ANY` (the default) |
| `looper.Pattern((PinLevel(pin_id, high=True), ...))` | every pin named stands at its level -- at the moment this *becomes* true |
| `looper.EdgeWhile(edge, levels)` | the edge happens while the other pins stand at their `levels` |
| `looper.Width(pin_id, high, comparison, duration_us)` | a high (or low) pulse whose length compares as asked is seen; see below |
| `looper.Quiet(pin_id, duration_us)` | the pin does not change for `duration_us` |
| `looper.Value(channel_id, comparison, value, mask, on_change)` | a watched variable compares as asked, or changes at all |
| `looper.BusReceived(bus_id, address, ...)` | a message crosses a bus; see [Chains](chains.md#the-builders) |
| `looper.BusTimeout(bus_id, address, duration_us, ...)` | no such message came for `duration_us` |
| `looper.Clock(period_us, phase_us)` | at the phase, then every period |
| `looper.Start(first_life_only)` | at 0 s and after every reset |
| `looper.Interrupt(source_id, on_entry)` | a source becomes pending, or its handler is entered |
| `looper.ResetSeen(cause)` | a life begins after a reset of that cause |

The last six are the conditions of [chains](chains.md) too -- a trigger is a
chain of one condition and, for a SINGLE trigger, a hold -- so what they
mean is told there.

A few examples:

```python
# the LED rises while the mode button is held down (it is active low)
looper.EdgeWhile(
    looper.Edge(led, looper.Polarity.RISE),
    (looper.PinLevel(button, high=False),),
)

# a high pulse on the LED that lasts longer than 600 microseconds
looper.Width(led, high=True, comparison=looper.Comparison.GT, duration_us=600)

# the button pin does not change for five milliseconds
looper.Quiet(button, duration_us=5_000)

# the low four bits of a watched variable are at least 3
looper.Value(counter, looper.Comparison.GE, value=3, mask=0xF)

# the variable changes, whatever it changes to
looper.Value(counter, on_change=True)
```

### When exactly a condition fires

- **Width.** `GT` and `GE` fire **the moment the length is exceeded**, in the
  middle of the pulse. `EQ`, `NE`, `LT` and `LE` can only be decided when the
  pulse ends, so they fire at the **closing edge**.
- **Pattern** fires when the pattern becomes true, not on every pass it stays
  true.
- **Value** is compared where the simulation reads the watch, **at most once
  per pass**. A variable that goes to 3 and back between two reads is not
  seen. `mask=0` means all bits.

## Label, before and after

`label` is text other clients are shown next to the trigger; the simulation
describes the condition itself as well, in `trigger.description` (for
example `BUTTON falls`). `pre_us` and `post_us` are for a window: how much
before a fire it shows, and how much after. `post_us` is also, for a SINGLE
trigger, how long the simulation goes on before it holds.

## Clean up after yourself

Triggers are **shared** between all clients and **outlive the connection**.
What a test arms stays armed when the test ends. On a simulation of your own
that does not matter; on one a window is also looking at, a left-over SINGLE
trigger would hold the window's simulation. So disarm in a `finally`:

```python
try:
    ...
finally:
    simulation.triggers.disarm_own()
```

`disarm_own()` stops every live trigger this process armed and returns where
each stood. `disarm(trigger)` stops one, by object or by number, whichever
client armed it. To look around: `triggers.all()` lists every trigger the
simulation holds, from every client; `triggers.live()` only those still
watching or holding.

Other clients see your tests under the name `looper-py` and the process
number. It is for display only; it does not authorise anything.

## What the simulation refuses

Not everything can be watched as a trigger. A condition on analog channels is
not supported (a *Threshold* is a block of [chains](chains.md)), and a pin or
channel the simulation does not have is refused. The refusal is a
`looper.SimulationRefusedError` with the simulation's own sentence, which says
what it can do instead. `current` and `disarm` raise it as well for a trigger
number the simulation does not hold.

For a trigger in a whole test, see the recipe
[What does the firmware do right after an event?](../recipes/trigger-reaction.md).
