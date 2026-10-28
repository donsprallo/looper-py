# Does the firmware react to its inputs?

**The question.** When this input changes, does the firmware do what the
requirement says -- and how quickly?

**Why it is worth a test.** A reaction is the first thing a refactoring of the
input handling breaks, and the last thing anybody checks by hand.

## How

1. Change the input: `toggle_pin` for a digital one, `apply_signal` for an
   analog one.
2. Expect the reaction: a call that should happen at a new rate, a value that
   should arrive, a channel that should change.
3. Evaluate over a window long enough for the reaction.

## Example: a button changes the blink rate

Blinky toggles its LED every 500 ms, and every 100 ms while `BUTTON_MODE` is
pressed. The button is active low.

```python
import looper


def test_pressing_the_button_makes_the_led_blink_faster(simulation):
    button = simulation.pin("BUTTON_MODE")
    assert button.level == "high"                      # released

    assert simulation.toggle_pin(button.pin_id) == "low"   # pressed
    try:
        check = simulation.expect()
        check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)
        report = check.evaluate(for_seconds=2.0)
    finally:
        simulation.toggle_pin(button.pin_id)           # released again
    assert report, report.summary
```

```text
1 of 1 met
ok    adapter_blinky_gpio_set: expected 10 Hz +/- 5%, saw 10 Hz
```

Each toggle of the LED is one call of `adapter_blinky_gpio_set`, so the call
rate is the toggle rate.

## Example: a current above a limit

Blinky also blinks fast while the current it measures is above 4 A. Apply
5 A and check both the reaction and how fast the filtered value gets there:

```python
def test_an_over_current_is_noticed_within_half_a_second(simulation):
    shunt = simulation.channel("SHUNT_CURRENT")
    filtered = simulation.channel("FILTERED")

    simulation.apply_signal(shunt.channel_id, looper.Signal(offset=5.0))

    check = simulation.expect()
    check.channel(filtered.channel_id, "FILTERED").reaches(4.95, tolerance=0.05, within_seconds=0.5)
    check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    assert report, report.summary
```

```text
2 of 2 met
ok    FILTERED: expected 4.95 +/- 0.05 within 0.5 s, saw reached after 0.389 s
ok    adapter_blinky_gpio_set: expected 10 Hz +/- 5%, saw 10 Hz
```

## When it fails

```text
FAIL  adapter_blinky_gpio_set: expected 10 Hz +/- 5%, saw 2 Hz
```

The firmware did not react: it still toggles at the idle rate. Check that you
drove the right pin and the right level -- `simulation.pin(...)` after the
toggle shows what it is now.

```text
FAIL  FILTERED: expected 4.95 +/- 0.05 within 0.1 s, saw reached after 0.389 s
```

It reacted, but more slowly than required. The number is how long it took,
measured in simulated time from the start of the window.

## Variations

- **A reaction that should *not* happen.** `happened_at(2.0)` after a change
  that must not affect the rate, or `stays_between` on an output that must
  stay put.
- **A reaction to a slow ramp.** `Signal(waveform="sawtooth", ...)` with a low
  frequency sweeps the input through a range; `reaches` tells you when the
  firmware followed it past a threshold.
