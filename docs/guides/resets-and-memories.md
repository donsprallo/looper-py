# Resets, lives and the memories

A device is reset by its own code, by its watchdog, by a pin and at power-on,
and what it does afterwards is worth a test. This guide is the reference of
what looper-py offers for it: pulling the reset, reading the **lives** of the
firmware, reaching the **retained memory** and the **flash**, and the
expectations on resets and on the flash. For a walk through with a small
firmware, see {learn}`Test a reset and a watchdog <guides/test-a-reset.html>`; for
what a reset *is* in a simulation, and how the server handles a watchdog, a hang
and a reset loop, see {core}`Resets, the watchdog and what survives them <resets.html>`.

The examples use `examples/reset_firmware` of looper-docs. Its pins are
`LED` (1), `RESET_BUTTON` (2), `STOP_KICKING` (3) and `HANG` (4); it keeps a
configuration in a flash partition `config` and counts its starts in
retained memory.

## A reset is not a restart

A **reset** begins the *firmware* again, at the simulated time at which it
ended; the clock, the recording and your connection go on. A **restart** starts
the simulation over at 0 s. After a reset the retained memory and the flash are
as the firmware left them, and its RAM is new. The span between two resets is a
**life**.

```{figure} ../images/reset-window.svg
:alt: Two rows. The top row, the window of evaluate for 0.15 s, a bar from 20 ms to 170 ms. The bottom row, the firmware time from 0 to 170 ms: life 1 until 118.75 ms, a double red line, and life 2. Under the line the expectation reset(cause="watchdog").happened_once() reads watchdog at 0.118750 s.

An expectation looks at the resets inside its window.
```

## `simulation.reset()`

```python
simulation.reset()               # the reset pin
simulation.reset("power-on")     # a power-on from outside
simulation.reset("brown-out")    # the supply fell and came back
```

From outside, a reset is `pin` (the default), `power-on` or `brown-out`. A
`power-on` or a `brown-out` from outside clears the retained memory unless
`[retained] battery = true`, and leaves only its own reset flag; the flash keeps
what it holds. A `pin` reset keeps both. The causes `software` and `watchdog`
are the firmware's and the watchdog's own: asking for one raises
`SimulationRefusedError` with the server's sentence. A word that is no cause at
all -- `reset("reboot")` -- raises `ValueError` and sends nothing.

Keys in `looper.toml` are written with underscores (`power_on`, `brown_out`),
like every key there; the cause as a word -- in texts, in `Life.cause`, in
`simulation.reset("power-on")` -- is written with a hyphen.

It takes effect at the next point of the simulation, as every change does: on a
**held** clock the firmware is reset when the test next lets time pass.

```python
simulation.reset()
simulation.advance(0.01)         # now the firmware has begun its next life
```

After a reset the jobs the simulation sends on a bus go on in the next life,
with the first round that begins at or after the reset (the rest of a round
already started is not sent, and the counters start over). A value set on the
signal graph stays. The debugger is detached. If the next life does not start,
the simulation is held with *The next life did not start: ...*.

A firmware that **hangs** with no watchdog to reset it holds the simulation; the
reason names the way out. `simulation.reset()` (the pin) or
`simulation.reset("power-on")` ends the hang at once and the next life begins.

## The lives

`simulation.lives()` returns every `Life` of the run, the one that runs now last:

| Field | Meaning |
| --- | --- |
| `number` | 1 for the first life |
| `started_at_us`, `ended_at_us` | simulated microseconds; `ended_at_us` is 0 while it runs |
| `cause` | why it ended: `power-on`, `software`, `watchdog`, `pin` or `brown-out`; empty while it runs |
| `text` | the line the window shows for it |
| `has_dump` | whether what it left behind can be read |
| `is_running` | whether it is the life that runs now |

```python
first, second = simulation.lives()
assert (first.cause, first.ended_at_us) == ("watchdog", 118_750)
assert second.started_at_us == first.ended_at_us
```

`simulation.life(n)` returns a `LifeDump`: the `life`, and what it left behind
when it ended -- its heap book (`memory`, as `MemoryUsage`, needs
`track_allocations = true`), its `profile` (needs `profile = true`) and a `note`.

```python
dump = simulation.life(1)
print(dump.memory.heap.allocations, dump.memory.heap.live_bytes)
```

It raises `SimulationRefusedError` for the life that runs now (its dump is taken
when it ends), for a life that does not exist and for one the server no longer
keeps: the dumps of the first life and the 64 most recent are kept. A firmware
that **hung** and was reset by its watchdog leaves a dump with a `note` instead
of readings: *The firmware hung and was reset by its watchdog: nothing of this
life could be read.*

## The retained memory

`simulation.retained()` returns a `Retained`: a few bytes the hardware keeps
through a reset (`[retained]` in `looper.toml`).

```python
retained = simulation.retained()
retained.read()                  # all of it, as bytes; b"" when there is none
retained.read(8, 4)              # four bytes from offset 8
retained.word(8)                 # one little endian word, 4 bytes wide
retained.word(8, width=2)        # or 1, 2 or 8 bytes
retained.write(8, (5).to_bytes(4, "little"))
```

A write is a change like any other: it takes effect at the next point, so let a
held clock run a little before you read it back. A write outside the memory, or
with none, raises `SimulationRefusedError`.

The retained memory begins at zero with every run; a reset keeps it. A
`power-on` or a `brown-out` from outside clears it, unless `[retained] battery =
true` says the memory has a battery.

## The flash

`simulation.flash()` returns a `Flash` (`[flash]` in `looper.toml`). A flash has
a flash's rules: **bits go from 1 to 0** when programmed and back only when a
**sector** is erased.

```python
flash = simulation.flash()
flash.read(0x3000, 12)           # bytes from the flash's beginning; length 0 reads to the end
flash.write(0x3000, data)        # by the rules; raw=True lays the bytes down past them
flash.erase(sector=3)            # one sector; erase() alone is the whole flash
```

Offsets count from the **beginning of the flash**, not from the address the
firmware sees it at. A **partition** is a name for a stretch, and its offsets
count from its own beginning:

```python
config = flash.partition("config")      # SimulationRefusedError if there is none
config.read(0, 12)                      # 0 as length reads to the partition's end
config.write(0, data)                   # a write past its end is refused
config.write(0, broken, raw=True)       # a broken configuration, on purpose
config.erase()                          # every sector of the partition
```

| Call | Does |
| --- | --- |
| `write(offset, data, raw=False)` | by the flash's rules: where a bit is already 0 it stays 0, and one that wants to go from 0 to 1 is a **violation**. It must start on a flash word and cover whole words (`[flash] word_size`); anything else is refused and recorded as a violation, whatever `on_violation` says. With `raw=True` the bytes are laid down as they are, and not checked |
| `erase(sector=None)` | one sector, or with none the whole flash but its read-only partitions |
| `erase_partition(name)` | a partition |
| `save()`, `save_file(path)` | the whole flash, as bytes or into a file |
| `load(content)`, `load_file(path)` | lays a saved flash down, but for the read-only partitions |

A **read-only** partition is never written -- not by the rules, not with
`raw=True`, not by `load` -- and cannot be erased: the call raises
`SimulationRefusedError` saying so. `load` of a content of another size than the
flash is refused too. Without `[flash]` in `looper.toml` every call raises
`SimulationRefusedError`: *This simulation has no flash: describe [flash] in
looper.toml.* Writes, erases and loads take effect at the next point of the
simulation.

```{note}
The server takes and gives messages of up to 64 MiB, so a saved flash of 16 MiB
loads. The firmware's own access to the flash is by its role
calls only; see {core}`the limits <resets.html#limits>`.
```

## Expecting resets

`check.reset(cause="")` expects something of the resets **inside the window**
of `evaluate`: those whose simulated time is in it.

```python
check = simulation.expect()
check.reset(cause="watchdog").happened_once()
check.reset().no_loop()
simulation.toggle_pin(3)                      # STOP_KICKING
report = check.evaluate(for_seconds=0.15)
assert report, report.summary
```

```text
2 of 2 met
ok    watchdog reset: expected once, saw watchdog at 0.118750 s
ok    the resets: expected no reset loop, saw 1 resets, no loop
```

| Expectation | Met when |
| --- | --- |
| `reset(cause).happened_once()` | exactly one reset of that cause was in the window |
| `reset(cause).happened(times=3)` | exactly three; with `times=0`, the default, at least one |
| `reset().no_loop()` | the server found no reset loop: ten resets within one second |

`cause` is `watchdog`, `software`, `pin`, `power-on` or `brown-out`; empty, the
default, counts the resets of every cause. A failing expectation says what it
saw:

```text
FAIL  the resets: expected no reset loop, saw Reset loop: 10 resets within 1 s (watchdog each time).
```

`no_loop()` asks the server's finding at the end of the window, so it also
fails for a loop that began before the window and is still going. A reset loop
holds a free-running simulation at once; a run with a target -- `advance`,
`evaluate`, RunFor -- still reaches its target and is held when it gets there.
See {core}`A reset loop <resets.html#a-reset-loop>`.

The resets are also in the event stream: `simulation.read_events(since)`
returns a page whose `resets` are `ResetMark`s -- `sim_us`, `cause` and the
`life` that ended -- and whose `flash_marks` are `FlashMark`s.

## Expecting the flash

```python
check = simulation.expect()
check.flash().no_violation()
simulation.reset()
report = check.evaluate(for_seconds=0.02)
assert report, report.summary
```

`check.flash().no_violation()` is met when every write in the window kept the
flash's rules: no bit went from 0 to 1 without an erase, nothing was written
outside the flash or into a read-only partition. It reads `saw none`, or
names the offsets and partitions where a rule was broken. A write is recorded
in the window it takes effect in; write *before* `evaluate` and the recording
has been cleared by the time it starts.

Every `FlashMark` has a `kind` -- `write`, `erase`, `violation` -- an `offset`,
a `length`, a `partition` and `by_client`, which says whether the test did it
rather than the firmware:

```python
marks = simulation.read_events(0).flash_marks
violations = [one for one in marks if one.kind == "violation"]
```

## What a reset does not do

- It does not start the simulation over: time, the recording and the
  connection go on. For that, restart the simulation.
- It does not clear the retained memory or the flash. A run does: every run,
  also a restart, begins with zero retained memory and an erased flash, unless
  `persist = true` keeps `build/flash.bin`.
- It does not take the signals you applied, the watches or the triggers: they
  are set again in the next life.
- It does not stop the jobs on a bus: they go on in the next life, but their
  counters start over, and the rest of a round already started is not sent. The
  number of times a trigger fired is not summed over the lives.

A hang is noticed after about 2 s of real time in which simulated time stood
still while a request waited, so a test that makes the firmware hang waits that
long once. The time is fixed on purpose: a shorter one would let a slow machine
mistake a busy host for a hung firmware and reset it where the real board would
not.
