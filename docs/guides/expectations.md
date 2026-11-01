# Expecting things

`simulation.expect()` returns an `Expectations` object. You declare on it what
should be true, then call `evaluate`, which watches one window of time and
checks everything at once:

```python
check = simulation.expect()
check.channel(1, "FILTERED").stays_between(0.0, 5.5)
check.call("adapter_blinky_measure").was_answered()
check.memory().never_allocates()

report = check.evaluate(for_seconds=1.0)
assert report, report.summary
```

Every declaration returns the `Expectations` again, so they can be chained
when that reads better:

```python
report = (
    simulation.expect()
    .firmware_is_alive()
    .call("adapter_blinky_measure").was_answered()
    .evaluate(for_seconds=1.0)
)
```

This page goes through every expectation. The [reference](../reference/expectations.md)
lists them in one table, with the exact wording of their outcomes.

## The window

`evaluate(for_seconds=...)` is one window of simulated time:

- Before it starts, the recordings and the measurements are cleared -- for
  every client of the simulation, which starts a new recording for all of
  them. A check sees only its own window.
- On a held clock the window is run for exactly `for_seconds`. On a clock
  that runs by itself (paced or max) it is waited out on the host, and the
  window ends where the simulated clock stands afterwards. The mode is read
  at the start of every window, because any client may have switched it. The
  library never switches it for you.
- Afterwards everything recorded in it is read, once, and every expectation
  is checked against that. Samples and exchanges are stamped with simulated
  time in whole microseconds (`sim_us`); the ones stamped after the end of the
  window are not part of it, however long the server took to hand them over.
- If the recording overflowed, the server says how many events it could not
  keep, and the outcome of a channel or bus check says so in its note, for
  example `and 12 events the recording could not keep`. It does not say
  whether they were samples or exchanges, so a bus check does not count
  them in the bus's favour. On a held clock nothing is lost.
- If a debugger holds the firmware, or another client clears the recording
  during the window, `evaluate` raises `SimulationRefusedError`. See
  [Troubleshooting](../troubleshooting.md).

A second `evaluate` on the same `Expectations` watches a new window. To
check different things in different windows, ask `simulation.expect()` again.

```{tip}
Let the firmware settle before the window starts. The first moments after a
start or after you changed an input are rarely what you want to measure:
`simulation.advance(1.0)` first, then `evaluate`.
```

## Analog channels

`check.channel(channel_id, name)` -- the name is only what the report calls
it. Find the number with `simulation.channel("NAME").channel_id`.

```{figure} ../images/channel-checks.svg
:alt: reaches looks for the first sample inside a tolerance band and measures the time from the window start; stays_between wants every sample inside a range.

What `reaches` and `stays_between` look at.
```

### `stays_between(low, high)`

Every sample recorded in the window lies within `low .. high`:

```python
filtered = simulation.channel("FILTERED")
check.channel(filtered.channel_id, "FILTERED").stays_between(1.0, 3.0)
```

```text
ok    FILTERED: expected every sample within 1 .. 3, saw 1.6953 .. 2.30469 over 1000 samples
```

### `reaches(value, tolerance=0.0, within_seconds=inf)`

Some sample comes within `tolerance` of `value`, and the first one that does
comes no later than `within_seconds` after the first sample of the window.
The time is taken from the samples' simulated time in whole microseconds, so
it does not depend on how fast the computer is:

```python
check.channel(filtered.channel_id, "FILTERED").reaches(4.95, tolerance=0.05, within_seconds=0.5)
```

```text
ok    FILTERED: expected 4.95 +/- 0.05 within 0.5 s, saw reached after 0.389 s
```

When it never gets there, the report says how close it came:

```text
FAIL  FILTERED: expected 4.95 +/- 0.05 within 0.1 s, saw never closer than 7.30142e-05
```

```{important}
A channel nothing was recorded for **fails**, with `saw nothing recorded`. An
expectation that could not be tested is not one that was met.
```

## Adapter calls

`check.call(function)` is about one function of the adapter -- the boundary
between your firmware and its hardware, which looper generated.

### `happened_at_least(count)`

```python
check.call("adapter_blinky_gpio_set").happened_at_least(2)
```

### `happened_at(hertz, tolerance=0.05)`

The call rate over the window, within a relative tolerance:

```python
check.call("adapter_blinky_measure").happened_at(1000, tolerance=0.05)
```

```text
ok    adapter_blinky_measure: expected 1000 Hz +/- 5%, saw 1000 Hz
```

A rate is calls counted over the time the window took, so a slow event in a
short window is counted in whole events. Make the window a few periods long,
and give the tolerance room for one event at either edge:

```{figure} ../images/window-edges.svg
:alt: A 2 Hz toggle counted in a two second window: three or four toggles, depending on where the window starts.

Where a window starts decides whether an event at its edge is in it.
```

### `was_answered()`

Something implemented the call -- a hook in your device model, a component
on a bus -- rather than the generated default, which hands back the zero
value and lets the firmware believe it:

```python
check.call("adapter_blinky_measure").was_answered()
```

```text
ok    adapter_blinky_measure: expected every call answered, saw 1000 of 1000 answered
FAIL  adapter_can_init: expected every call answered, saw 0 of 1 answered
FAIL  adapter_blinky_flash: expected implemented and called, saw never called
```

See the recipe [Is a peripheral driver really implemented?](../recipes/hollow-adapter.md).

### `firmware_is_alive()`

The firmware still reaches its adapter at all -- the cheapest check that it
did not hang or crash:

```python
check.firmware_is_alive()
```

```text
ok    the firmware: expected still calling the adapter, saw 12004 calls
```

## Memory

These need the simulation built with `track_allocations = true` (the heap)
and `profile = true` (the stack) in its `looper.toml`. Without them they
**fail**, saying the instrument was missing -- not looking and seeing nothing
are different answers.

### `memory().never_allocates()`

Nothing asked the allocator for anything during the window:

```text
ok    the heap: expected no allocation at all, saw 0 allocations
```

### `memory().nothing_leaked()`

Everything allocated during the window was freed again during it. A block
taken before the window -- by the C runtime, by your start-up code -- does
not count:

```text
ok    the heap: expected everything freed again, saw 0 allocated, 0 freed
```

### `memory().peak_below(bytes_allowed)`

The heap never held more than so many bytes at once. The peak counts what was
still out from before the window as well:

```text
FAIL  the heap: expected at most 64 bytes out at once, saw 120 bytes at the peak
```

### `stack().no_deeper_than(frames_allowed)`

The deepest nesting of calls. The depth is your firmware's own and means the
same on the target:

```text
FAIL  the stack: expected at most 3 frames, saw 4 frames at the deepest
```

### `stack().stays_below(bytes_allowed)`

The most stack used, in bytes **of your computer**. Frame sizes differ on the
target; use this to notice that something changed, not to size a stack:

```text
ok    the stack: expected at most 1024 bytes of stack, saw 352 bytes at the deepest
```

## Buses

`check.bus(bus_id, name)` is about one bus. Find the number with
`simulation.bus("NAME").bus_id`.

### `nothing_refused()`

Everything that crossed the bus was taken by something -- a component that
answered, a filter that accepted a frame. The report names the addresses
nothing took:

```text
FAIL  CAN2: expected nothing refused, saw 1 of 2 refused at 0x701
```

### `carried_at_least(count)`

At least so many exchanges crossed the bus in the window:

```python
check.bus(can.bus_id, "CAN2").carried_at_least(10)
```

## Reading the report

```{figure} ../images/report-anatomy.svg
:alt: The heading says how many were met; failures come first; each line says what was expected and what was seen.

A report, failures first.
```

An `ExpectationReport` is true when every expectation was met.

| | |
| --- | --- |
| `bool(report)`, `report.passed` | whether everything was met |
| `report.summary` | the text above, for an assertion message |
| `report.failures` | the `Outcome`s that were not met |
| `report.outcomes` | every `Outcome`, in the order they were declared |

Each `Outcome` has `subject`, `expected`, `observed`, `met` and `line`, so a
test can look at one expectation on its own:

```python
report = check.evaluate(for_seconds=1.0)
first = report.outcomes[0]
assert first.met, first.line
```

## Choosing thresholds

Pick limits that catch a regression, not ones that describe today:

- `stack().no_deeper_than(16)` when the firmware is at 4 is a guard; `4` is a
  tripwire that fires on the next harmless refactoring.
- `happened_at(10, tolerance=0.05)` over two seconds tolerates the one event
  a window edge can add or remove; `tolerance=0.0` does not.
- `reaches(..., within_seconds=...)` with the time your requirement allows,
  not the time the firmware happens to need now.
