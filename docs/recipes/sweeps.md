# Does it hold across a range of inputs?

**The question.** A behaviour is right at the one value you tried. Is it right
at the edges, just below a threshold and just above it, at the extremes?

**Why it is worth a test.** Off-by-one comparisons, a `>` that should be
`>=`, a scale factor that overflows at the top of the range -- they live at
the values nobody tries by hand.

## How

`pytest.mark.parametrize` runs one test over many values. A module scoped
simulation runs all of them against one started firmware, so a sweep of
twenty values costs twenty windows, not twenty starts.

```python
import pytest
import looper

DEFINITION = "looper.toml"


@pytest.fixture(scope="module")
def simulation():
    with looper.run(DEFINITION, virtual=True) as started:
        started.advance(1.0)
        yield started
```

## Example: the over-current threshold

Blinky blinks fast above 4 A. Sweep across the threshold:

```python
@pytest.mark.parametrize(
    "amps, hertz",
    [
        (0.0, 2.0),
        (3.5, 2.0),   # below the threshold
        (4.5, 10.0),  # above it
        (8.0, 10.0),
    ],
)
def test_the_blink_rate_follows_the_current(simulation, amps, hertz):
    shunt = simulation.channel("SHUNT_CURRENT")
    simulation.apply_signal(shunt.channel_id, looper.Signal(offset=amps))
    simulation.advance(1.0)  # let the filter settle

    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(hertz, tolerance=0.15)
    report = check.evaluate(for_seconds=2.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    simulation.advance(1.0)
    assert report, report.summary
```

```console
$ uv run pytest -v tests/test_sweep.py
test_sweep.py::test_the_blink_rate_follows_the_current[0.0-2.0] PASSED
test_sweep.py::test_the_blink_rate_follows_the_current[3.5-2.0] PASSED
test_sweep.py::test_the_blink_rate_follows_the_current[4.5-10.0] PASSED
test_sweep.py::test_the_blink_rate_follows_the_current[8.0-10.0] PASSED
```

Each case leaves the input at zero and lets the filter come down again, so the
order the cases run in does not matter.

## Example: a waveform sweep

The same shape works for anything that can be parametrized -- a frequency, a
waveform, an amplitude:

```python
@pytest.mark.parametrize("waveform", ["sine", "square", "triangle", "sawtooth"])
def test_a_ripple_of_any_shape_is_smoothed(simulation, waveform):
    shunt = simulation.channel("SHUNT_CURRENT")
    filtered = simulation.channel("FILTERED")
    ripple = looper.Signal(waveform=waveform, offset=2.0, amplitude=1.0, frequency_hz=5.0)

    simulation.apply_signal(shunt.channel_id, ripple)
    simulation.advance(1.0)

    check = simulation.expect()
    check.channel(filtered.channel_id, "FILTERED").stays_between(1.5, 2.5)
    report = check.evaluate(for_seconds=1.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    simulation.advance(1.0)
    assert report, report.summary
```

## Tips

- Give each case an `id` when the values alone do not say what it is about:
  `pytest.param(4.5, 10.0, id="just above the limit")`.
- A sweep shares one simulation, so every case has to undo what it did. Put
  the undoing in a fixture or a `finally` when an assertion could skip it.
