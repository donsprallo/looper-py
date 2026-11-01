# Does a periodic task keep its rate?

**The question.** A sampling loop should run at 1 kHz, a heartbeat at 1 Hz, a
display refresh at 50 Hz. Does it?

**Why it is worth a test.** A rate breaks quietly: a blocking call added to
the main loop, a timer prescaler changed, a task that now runs every other
pass. On a held clock a rate can be checked exactly, independent of how
fast the computer is.

## How

Every periodic task reaches the adapter -- it reads an input, writes an
output, publishes a value. Count that call over a window:

```python
check.call(function).happened_at(hertz, tolerance=0.05)
```

## Example: the sampling loop

Blinky measures its current once per millisecond:

```python
def test_the_current_is_sampled_at_one_kilohertz(simulation):
    check = simulation.expect()
    check.call("adapter_blinky_measure").happened_at(1000, tolerance=0.01)
    check.call("adapter_blinky_publish").happened_at(1000, tolerance=0.01)

    report = check.evaluate(for_seconds=1.0)
    assert report, report.summary
```

```text
2 of 2 met
ok    adapter_blinky_measure: expected 1000 Hz +/- 1%, saw 1000 Hz
ok    adapter_blinky_publish: expected 1000 Hz +/- 1%, saw 1000 Hz
```

## Example: a slow rate

The LED toggles at 2 Hz. A slow event in a short window is counted in whole
events, so the window decides how exact the count can be:

```{figure} ../images/window-edges.svg
:alt: A 2 Hz toggle counted in a two second window: three or four toggles, depending on where the window starts.

One toggle more or less at the edge of a two second window is 0.5 Hz.
```

```python
def test_the_led_blinks_at_two_hertz(simulation):
    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(2.0, tolerance=0.1)

    report = check.evaluate(for_seconds=10.0)
    assert report, report.summary
```

```text
ok    adapter_blinky_gpio_set: expected 2 Hz +/- 10%, saw 2 Hz
```

Ten seconds of a 2 Hz toggle is 20 events; one at either edge is 5 %, inside
the tolerance. The ten simulated seconds take well under a second on your
computer.

## When it fails

```text
FAIL  adapter_blinky_measure: expected 1000 Hz +/- 1%, saw 500 Hz
```

The task runs at half its rate -- every other pass, or with a period twice as
long as intended.

```text
FAIL  adapter_blinky_gpio_set: expected 2 Hz +/- 10%, saw 1.5 Hz
```

Before suspecting the firmware, check the window: three events in two seconds
is a 2 Hz toggle that started after the window did. Make the window longer.
