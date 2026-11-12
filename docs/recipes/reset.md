# Is the firmware reset when it should be?

**The question.** A device has a watchdog so that a firmware that stops kicking
it is reset. And after any reset it has to come back: find its configuration,
count its boots, start its peripherals again. Does yours?

**Why it is worth a test.** On a board a reset is hard to provoke at the
millisecond you want, and nobody notices a watchdog that was never started until
the day the firmware hangs. In a simulation a reset is a call, and the moment of
a watchdog is exact. See
{learn}`Resets, the watchdog and what survives them <manual/resets.html>`.

## Prerequisite

The firmware's hardware layer needs the roles for what it uses -- a reset, a
watchdog, retained memory, flash -- and `looper.toml` the sections `[retained]`
and `[flash]` where it keeps something. The example is `examples/reset_firmware`
of looper-docs: a 100 ms watchdog, kicked every pass, a boot counter in the
retained memory and a checked configuration in the flash partition `config`.
`STOP_KICKING` (pin 3) stops the kicking.

## Example: the watchdog bites, once, when it should

```python
STOP_KICKING = 3


def test_the_watchdog_bites_100_ms_after_the_last_kick(simulation):
    check = simulation.expect()
    check.reset(cause="watchdog").happened_once()
    simulation.toggle_pin(STOP_KICKING)

    report = check.evaluate(for_seconds=0.15)
    assert report, report.summary
```

```text
ok    watchdog reset: expected once, saw watchdog at 0.118750 s
```

The deadline is the *last kick plus the timeout*, in simulated time. Here the
test set the pin at 20 ms, the last kick was at 18.75 ms, and 18.75 ms plus
100 ms is 118.75 ms.

## Example: a firmware that kicks is not reset

```python
def test_a_firmware_that_kicks_is_never_reset(simulation):
    check = simulation.expect()
    check.reset().no_loop()
    simulation.advance(0.98)

    report = check.evaluate(for_seconds=0.5)
    assert report, report.summary
    assert len(simulation.lives()) == 1
```

## Example: it comes back with its configuration

After a reset the firmware has to find what it kept. The retained memory and the
flash survive, its RAM does not:

```python
STARTS, CONFIG_STATE, BOOTS = 0, 8, 12


def test_the_firmware_comes_back_after_a_reset(simulation):
    simulation.reset()
    simulation.advance(0.01)

    retained = simulation.retained()
    assert retained.word(STARTS) == 2          # it started twice
    assert retained.word(CONFIG_STATE) == 1    # and found a valid configuration
    assert retained.word(BOOTS) == 2           # whose count is the flash's
```

## Example: it copes with a broken configuration

A flash can hold what a real flash should not -- after a write that was
interrupted in the middle, say. Lay it down raw, past the flash's rules, and see what the
firmware does:

```python
def test_a_broken_configuration_is_found_and_made_again(simulation):
    config = simulation.flash().partition("config")
    config.write(0, bytes.fromhex("00eeffc0" "07000000" "00000000"), raw=True)
    simulation.advance(0.001)

    simulation.reset()
    simulation.advance(0.01)

    assert simulation.retained().word(CONFIG_STATE) == 2     # it found it broken
    assert simulation.retained().word(BOOTS) == 1            # and began counting again
```

## Reading the numbers

- `happened_once()` is *exactly one*. A watchdog that bites twice in the window
  fails it, with both times in the message. `happened(times=0)` is *at least one*.
- Ten watchdog resets within a second are a **reset loop**, which `no_loop()`
  reports with the server's sentence. Use it as the guard of every test that
  provokes a reset: it fails when a fix makes things worse.
- A test reset (`simulation.reset()`) is the cause `pin`; from outside it may also be
  `power-on` or `brown-out`. The causes `software` and `watchdog` come from the
  firmware itself.

The complete guide, including a firmware that hangs and the flash expectations,
is [Resets, lives and the memories](../guides/resets-and-memories.md).
