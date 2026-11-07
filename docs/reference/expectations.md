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

Narrowed to the messages of one kind -- `check.bus(bus_id, name).message(address=None, direction=None,
starts_with=b"")`:

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `happened_at_least(count)` | at least `count` of them crossed | `saw 12` |
| `happened_between(at_least, at_most)` | their number is within the range | `saw 12` |
| `never()` | none crossed | `saw 0` |
| `happened_at(hertz, tolerance=0.05)` | their rate over the window is within `tolerance` of `hertz` | `saw 10 Hz` |

`direction` is `"outbound"` (what the firmware sent) or `"inbound"`; the address is
the CAN identifier, I2C address or chip select.

## Resets -- `check.reset(cause="")`

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `happened_once()` | exactly one reset of the cause was in the window | `saw watchdog at 0.118750 s` |
| `happened(times=0)` | exactly `times` resets of the cause were in the window; with 0, at least one | `saw watchdog at 0.100000 s, ...` |
| `no_loop()` | the server found no reset loop: 10 resets within 1 s | `saw 1 resets, no loop` |

`cause` is `watchdog`, `software`, `pin`, `power-on` or `brown-out`; empty counts
every cause. Fails with `saw no reset` when there was none. `no_loop` fails with
the server's sentence, `Reset loop: 10 resets within 1 s (watchdog each time).`

## The flash -- `check.flash()`

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `no_violation()` | every write in the window kept the flash's rules | `saw none` |

When it fails it names the offsets and the partitions: `saw at 0x3000 (config)`.

## The boot chain -- `check.boot_chain()` (Pro)

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `went(*partitions)` | the last start of the board in the window went through these partitions, in order | `saw stage0 → stage1_a 1.0 → app_b 2.1` |

It fails with `no boot chain` when there was none. The last chain is the one that
counts: a window that holds several starts expects the newest.

## A partition's header -- `check.flash().partition(name)` (Pro)

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `is_valid(image="")` | the header at the window's end is `valid`, and names `image` when one is given | `saw valid · app@2.1 · v0x0201` |
| `is_invalid()` | the header is `broken`, `unknown image` or `empty`: no image a bootloader would start | `saw broken: the payload CRC does not match (…)` |
| `is_empty()` | the partition is erased | `saw empty (erased)` |

A partition with no image header at all (data, a boot state) has no state, so
`is_invalid()` is not met by it. Without the licence the server gives no state and
the outcome says so.

## Interrupts -- `check.interrupt(name)` and `check.interrupts()` (Pro)

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `check.interrupt(name).latency_below(amount, unit="us")` | every ISR of the source in the window started less than `amount` after it fell due | `saw at most 0 us over 3 ISRs` |
| `check.interrupt(name).never_lost()` | no interrupt of the source was lost in the window | `saw 0 lost` |
| `check.interrupt(name).handled_at_least(times)` | its ISR ran at least `times` in the window | `saw 20 times` |
| `check.interrupt(name).shorter_than_period()` | a timer's ISR always ended within its period | `saw always within it` |
| `check.interrupts().locked_at_most(amount=0, unit="us")` | interrupts were never masked longer than `amount`; without one, than `[interrupts] max_disabled` | `saw within the limit`, or the longest section |

A source that does not exist fails with `no such interrupt source`. What the race
mode raised is left out of the counts. Without a licence for the run findings
`evaluate()` raises `looper.ProFeatureLockedError`.

## DMA -- `check.dma(channel)` (Pro)

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `no_overrun()` | the channel never wrote into a half whose ISR had not ended | `saw none found` |
| `not_accessed_while_running()` | the firmware never read or wrote the buffer where the channel still worked | `saw none found` |
| `length_fits()` | every transfer of the channel fit the variable it was given | `saw none found` |

A failed one names the server's finding: `saw The firmware read USART2_RX's buffer
while the channel ran`. A channel that does not exist fails with `no such DMA channel`.

## The findings of a run -- `check.run_findings()` (Pro)

| Expectation | Met when | Outcome when met |
| --- | --- | --- |
| `none(kinds=())` | the server found no finding in the run, of the kinds given or of any | `saw none` |

`kinds` are the names of the findings: `none(["IRQ_STORM", "DMA_UNCLAIMED"])`.

## The profile -- `check.profile()`

| Expectation | Met when | Needs in `looper.toml` |
| --- | --- | --- |
| `heaviest_is(function, origin="firmware")` | the function spent more time in itself than any other of that origin | `profile = true` |

Without the instrument it fails with `saw the build is not woven for profiling`.

## The window -- `check.evaluate(for_seconds=1.0)`

1. Clears the recordings and measurements, for every client.
2. Lets `for_seconds` pass: a held clock is run for exactly that long, a clock
   that runs by itself is waited out. The mode is read for every window.
3. Reads the clock and the call counts together, then the window's samples
   and exchanges, then the heap and the stack.
4. Returns an `ExpectationReport` with one `Outcome` per expectation, in the
   order they were declared.
