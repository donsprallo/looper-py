# Interrupts and DMA from a test

A firmware with interrupts does what it does *between* two lines of its loop,
behind a lock, or in a buffer a DMA channel fills without asking it. This guide
is the reference of what looper-py offers for it: reading the interrupt
**sources** and the DMA **channels**, **raising** a source, the **race mode**,
and the expectations on interrupts, the lock, DMA and the findings of a run. For
a walk through with a small firmware, see {learn}`Test an interrupt-driven button
and a UART receive by DMA <guides/test-an-interrupt.html>`; for what an
interruption point is, what a lock costs and what each finding means, see
{core}`Interrupts <interrupts.html>` and {core}`DMA <dma.html>`.

The examples use `examples/interrupt_firmware` of looper-docs. Its pins are
`BUTTON` (1, EXTI0), `LOCK` (2), `PEEK` (3) and `LED` (4); it has the sources
`EXTI0`, `TIM2` (1 ms), `USART2_RX_EVENT` and `USART2_IDLE`, and a circular DMA
channel `USART2_RX`.

```{admonition} What is free and what is Pro
:class: important
`simulation.interrupts()`, `simulation.dma()` and `simulation.raise_interrupt()`
are **free**. **Every check** of this page – `check.interrupt()`,
`check.interrupts()`, `check.dma()` and `check.run_findings()` – and
`simulation.race()` are **looper Pro**: they read the findings of the run, and
without a licence for them `evaluate()` and `race()` raise
`looper.ProFeatureLockedError` with the server's sentence. See
{learn}`Editions and licence <licence.html>`.
```

## `simulation.interrupts()`

```python
interrupts = simulation.interrupts()
tim2 = interrupts.source("TIM2")
assert (tim2.raised, tim2.handled, tim2.lost) == (20, 20, 0)
assert interrupts.lock.longest_us == 0
```

It returns the sources, the lock and the server's note. `source(name)` raises
`KeyError` for a name that is no source. Every time is in simulated
microseconds, and every `*_text` is the server's sentence, the one the window
shows.

| `InterruptSource` | Meaning |
| --- | --- |
| `source_id`, `name` | the number a raise names, and the name in `contract.toml` |
| `kind_text` | what makes it due: `timer, every 1 ms`, `pin BOARD_PIN_BUTTON, rising edge` |
| `handler` | the firmware's function that handles it; empty without one |
| `priority`, `enabled`, `pending` | the line's priority (smaller is more urgent), and whether it is enabled and waiting now |
| `raised`, `handled`, `lost` | how often it fell due, how often its ISR ran, how often it was lost behind a pending bit |
| `latency_max_us`, `latency_mean_us` | due to start, in simulated time |
| `duration_max_us`, `duration_mean_us` | how long the ISR ran, in simulated time |
| `period_us` | a timer's period; 0 otherwise |
| `is_raisable` | whether a test may raise it: every source but the end of a transfer |
| `state_text` | `idle`, `pending`, `running` or `disabled` |

| `InterruptLock` | Meaning |
| --- | --- |
| `disabled_now` | whether interrupts are masked now |
| `sections` | how often they were masked and unmasked in this life |
| `longest_us`, `total_us` | the longest section, and all of them together |

`Interrupts.installed` says whether the firmware called an interrupt role yet –
before that the counts are not live – and `Interrupts.note` carries the server's
word on the time model: *Computing takes no simulated time in looper: what is
measured is what waits, locks and other ISRs cause.*

**Latency and duration are zero unless something waits.** An ISR runs at an
interruption point and the clock only moves in waits, so a latency above zero
means a lock, another ISR or a loop without a point held the interrupt back. The
{core}`time model <interrupts.html#the-time-model>` says why.

## `simulation.raise_interrupt(name, after_us=0)`

```python
simulation.raise_interrupt("EXTI0")                  # as its pin would, at the next point
simulation.raise_interrupt("EXTI0", after_us=3000)   # 3 ms from now
```

It makes the source due as its pin or timer would. `KeyError` for a name that is
no source; `SimulationRefusedError` for a source that is the end of a DMA
transfer (`is_raisable` is false). On a held clock the change takes effect at the
next run, like any change; `after_us` counts from then. It is free.

**How far a held run advances.**

A held simulation stops only where the firmware returns to its loop, at the end of
a pass. So an `advance`, a `run_for_us` or a `run_until_us` ends at the **first
pass boundary at or after its target**. A wait *between* two passes is cut exactly
at the target; a wait *inside* a pass – a `HAL_Delay`, a `__WFI()` that waits for
the next tick, a timeout inside a HAL call – always runs to its end. A firmware
that waits for a 1 ms tick in every pass therefore moves in steps of 1 ms, also
for `advance(0.0001)`.

A change with `after_us`, such as `raise_interrupt("EXTI0", after_us=500)`, is
still applied **exactly at its time**, also in the middle of such a wait, and the
ISR runs then. Only the state you read *after* the advance is the state at the
pass boundary. Read when an interrupt ran from the events (`read_events`, Logic), not
from the counts after an `advance`, and expect "not yet" only before a pass
boundary that lies before the time.


## `simulation.dma()`

```python
channel = simulation.dma().channel("USART2_RX")
assert (channel.position, channel.announced, channel.laps) == (5, 5, 0)
assert channel.state_text == "running, at 5 of 64"
```

| `DmaChannel` | Meaning |
| --- | --- |
| `dma_id`, `name` | its number, and its name in `contract.toml` |
| `peripheral_text`, `direction`, `mode` | `UART 2 -> rx_buf`, `receive`, `circular` |
| `running` | whether a transfer runs now |
| `buffer_name`, `buffer_bytes`, `length`, `width` | the variable the transfer writes into, from the debug information (empty and 0 where it is unknown), and the transfer's length and element width |
| `position` | the element written next |
| `announced` | the elements the firmware was told of by half, end or idle |
| `laps`, `elements` | rounds of a circular channel completed, and elements moved |
| `overruns`, `unclaimed` | halves overwritten before their ISR ended, and bytes lost because no transfer ran |
| `guard`, `guard_text` | `off`, `precise`, `coarse`, `downgraded`, `unavailable`, `debugger`, `stack` or `locked`, and its sentence |
| `neighbours` | the firmware's own variables on the buffer's pages, which the guard traps too |
| `state_text` | `running, lap 3, at 12 of 64` |

`DmaChannels.channel(name)` raises `KeyError` for no such channel; `installed`
says whether the firmware started a transfer yet. Reading the buffer through a
test – a watch – is no access of the firmware and never trips the guard. To feed
a UART channel, send bytes to its bus, **64 at most per message**:

```python
simulation.send_bus_message(looper.BusMessage(2, 0, b"hello"))
```

The `guard` of a receive channel is `locked` without a licence for the run
findings, `precise` with one (on Windows and Linux on x86-64), and `debugger`
while one is attached. What it catches, and its limits, are in
{core}`DMA <dma.html#the-guard-pro>`.

## `simulation.race(name)` (Pro)

```python
with simulation.race("TIM2") as race:
    simulation.advance(0.02)
    coverage = race.coverage()
assert coverage.complete
```

The race mode raises the source at the next interruption point of each pass,
at a different point each pass, so that over a few passes every point has had
its turn – deterministically, in one run. It **provokes** the failure; **your
assertions** find it. `race()` raises `KeyError` for a name that is no source,
and `looper.ProFeatureLockedError` when the block is entered without the licence.
The race mode counts the points the firmware reaches while it runs: a place that
is only reached when the chosen source has not come in that pass yet (a
`while (ticks == seen) __WFI();` while racing the timer) is not seen.
Leaving the block – also by an exception – switches the mode off, and a reset
switches it off too.

| `RaceCoverage` | Meaning |
| --- | --- |
| `on`, `source` | whether it raises a source, and which (empty while off) |
| `points_seen`, `points_covered` | the distinct points seen outside ISRs since it began, and those it raised at |
| `cycles` | how often it went round every point of a pass |
| `text` | the server's sentence, `3 of 3 points, 26 cycles` |
| `uncovered` | the functions that hold points it has not raised at yet |
| `complete` | `on`, at least one point seen, every point seen was raised at, and one full cycle at least |

## Expectations (Pro)

They are declared like all expectations (see
[Expecting things](expectations.md)) and judged at the end of the window of
`evaluate()` from what the server found:

```python
check = simulation.expect()
check.interrupt("TIM2").never_lost()
check.interrupts().locked_at_most()
check.dma("USART2_RX").not_accessed_while_running()
check.run_findings().none()

report = check.evaluate(for_seconds=0.02)
assert report, report.summary
```

| Expectation | Met when | Finding behind it |
| --- | --- | --- |
| `check.interrupt(name).latency_below(amount, unit="us")` | every ISR of the source in the window started less than `amount` after it fell due | `IRQ_LATENCY`, with `max_latency` in the contract |
| `check.interrupt(name).never_lost()` | no interrupt of the source was lost in the window | `IRQ_LOST` |
| `check.interrupt(name).handled_at_least(times)` | the ISR ran at least `times` in the window | |
| `check.interrupt(name).shorter_than_period()` | a timer's ISR always ended within its period | `IRQ_LONGER_THAN_PERIOD` |
| `check.interrupts().locked_at_most(amount=0, unit="us")` | interrupts were never masked longer than `amount`; without one, than `[interrupts] max_disabled` of `looper.toml` | `IRQ_LOCK_TOO_LONG` |
| `check.run_findings().none(kinds=())` | the server found no finding in the run, of the kinds given or of any | all |
| `check.dma(name).no_overrun()` | the channel never wrote into a half whose ISR had not ended | `DMA_OVERRUN` |
| `check.dma(name).not_accessed_while_running()` | the firmware never read or wrote the buffer where the channel still worked | `DMA_READ_UNWRITTEN`, `DMA_READ_UNANNOUNCED`, `DMA_WRITE_CONFLICT` |
| `check.dma(name).length_fits()` | every transfer of the channel fit the variable it was given | `DMA_LENGTH` |

Units are `"us"`, `"ms"` and `"s"`. A source or a channel that does not exist
fails with `no such interrupt source` and `no such DMA channel`; it does not pass.
`handled_at_least`, `never_lost` and `latency_below` count the events of the
window, and **leave out** what the race mode raised on purpose.

A failed outcome says what was seen in the words of the finding:

```text
FAIL the interrupts  expected masked no longer than [interrupts] max_disabled   saw Interrupts disabled for 2 ms (limit 1 ms)
FAIL TIM2            expected none lost                                         saw 1 lost
FAIL USART2_RX       expected not accessed while the channel ran                saw The firmware read USART2_RX's buffer while the channel ran
```

A finding that has no expectation of its own – `IRQ_STORM`, `DMA_UNCLAIMED`,
`DMA_BUFFER_ON_STACK`, `DMA_GUARD_DOWNGRADED` – is caught by
`check.run_findings().none()`, or by `none(["IRQ_STORM"])` for one kind; the
finding's `check_text` says so. `IRQ_NEVER_HANDLED` is `check.interrupt(name).handled_at_least(1)`. Every
finding names a function in the window, not a line.

## Without a licence

`interrupts()`, `dma()` and `raise_interrupt()` work. A check evaluated, or a race
entered, raises `looper.ProFeatureLockedError`, a kind of
`SimulationRefusedError`, with the sentence *Run findings is part of looper Pro*.
A test of yours that uses them can skip itself on a machine without a licence:

```python
@pytest.fixture
def simulation():
    with looper.run("looper.toml", virtual=True) as started:
        yield started


def test_no_lost_ticks(simulation):
    check = simulation.expect()
    check.interrupt("TIM2").never_lost()
    try:
        report = check.evaluate(for_seconds=0.1)
    except looper.ProFeatureLockedError as error:
        pytest.skip(str(error))
    assert report, report.summary
```
