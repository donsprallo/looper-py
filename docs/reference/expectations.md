# Expectations at a glance

Every expectation, what it checks, what it needs, and how its outcome reads.
`check` is what `simulation.expect()` returned.

## Analog channels -- `check.channel(channel_id, name)`

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `stays_between(low, high)` | every sample in the window is within `low .. high` | `saw 1.6953 .. 2.30469 over 1000 samples` |
| `reaches(value, tolerance=0.0, within_seconds=inf)` | the first sample within `tolerance` of `value` comes no later than `within_seconds` after the window's first sample | `saw reached after 0.389 s` |

Fails with `saw nothing recorded` when the channel recorded nothing.

## Adapter calls -- `check.call(function)`

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `happened_at_least(count)` | the function was called at least `count` times | `saw 12` |
| `happened_at(hertz, tolerance=0.05)` | calls over the window's duration are within `tolerance` of `hertz`, relatively | `saw 1000 Hz` |
| `was_answered()` | something implemented every call | `saw 1000 of 1000 answered` |
| `check.firmware_is_alive()` | the firmware called any adapter function at all | `saw 12004 calls` |

`was_answered` fails with `saw never called` when there was no call to answer.

## Memory -- `check.memory()` and `check.stack()`

| Expectation | Met when | Needs in `looper.toml` |
| --- | --- | --- |
| `memory().never_allocates()` | nothing was allocated in the window | `track_allocations = true` |
| `memory().nothing_leaked()` | everything allocated in the window was freed in it | `track_allocations = true` |
| `memory().peak_below(bytes_allowed)` | the heap never held more than `bytes_allowed` at once | `track_allocations = true` |
| `stack().no_deeper_than(frames_allowed)` | calls never nested deeper than `frames_allowed` | `profile = true` |
| `stack().stays_below(bytes_allowed)` | the stack never used more than `bytes_allowed` host bytes | `profile = true` |

Without the instrument they fail, saying so.

## Buses -- `check.bus(bus_id, name)`

| Expectation | Met when | Outcome when not met |
| --- | --- | --- |
| `nothing_refused()` | everything that crossed the bus was taken | `saw 1 of 2 refused at 0x701` |
| `carried_at_least(count)` | at least `count` exchanges crossed it; events the recording lost are named, not counted | `saw 3` |

## The window -- `check.evaluate(for_seconds=1.0)`

1. Clears the recordings and measurements, for every client.
2. Lets `for_seconds` pass: a held clock is run for exactly that long, a clock
   that runs by itself is waited out. The mode is read for every window.
3. Reads the clock and the call counts together, then the window's samples
   and exchanges, then the heap and the stack.
4. Returns an `ExpectationReport` with one `Outcome` per expectation, in the
   order they were declared.
