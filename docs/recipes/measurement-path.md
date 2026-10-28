# Does a measurement path work end to end?

**The question.** A value enters the firmware at an analog input, is
converted, filtered and published. Does what comes out match what went in --
how fast, how accurately, and without leaving its range?

**Why it is worth a test.** A wrong scale factor, a filter constant off by ten
or a sign error passes every unit test of the pieces and fails only end to
end.

## How

1. Apply a known signal to the input channel.
2. Let the path settle, if you want to check the steady state.
3. Expect the output channel to `reach` the value, or to `stay_between` the
   limits it must keep.

## Example: the step response

```python
import looper


def test_the_filter_follows_a_step_within_half_a_second(simulation):
    shunt = simulation.channel("SHUNT_CURRENT")
    filtered = simulation.channel("FILTERED")

    simulation.apply_signal(shunt.channel_id, looper.Signal(offset=5.0))

    check = simulation.expect()
    check.channel(filtered.channel_id, "FILTERED").reaches(4.95, tolerance=0.05, within_seconds=0.5)
    report = check.evaluate(for_seconds=1.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    assert report, report.summary
```

```text
ok    FILTERED: expected 4.95 +/- 0.05 within 0.5 s, saw reached after 0.389 s
```

## Example: a ripple stays within limits

With 2 A and a 1 A ripple at 5 Hz on the input, the filtered value has to stay
well inside 1 .. 3 A. Let the filter settle first -- the transient from 0 A is
not what this checks:

```python
def test_a_ripple_is_smoothed(simulation):
    shunt = simulation.channel("SHUNT_CURRENT")
    filtered = simulation.channel("FILTERED")
    ripple = looper.Signal(waveform="sine", offset=2.0, amplitude=1.0, frequency_hz=5.0)

    simulation.apply_signal(shunt.channel_id, ripple)
    simulation.advance(1.0)                                        # settle

    check = simulation.expect()
    check.channel(shunt.channel_id, "SHUNT_CURRENT").stays_between(1.0, 3.0)   # what went in
    check.channel(filtered.channel_id, "FILTERED").stays_between(1.5, 2.5)     # what came out
    report = check.evaluate(for_seconds=1.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    assert report, report.summary
```

```text
2 of 2 met
ok    SHUNT_CURRENT: expected every sample within 1 .. 3, saw 1 .. 3 over 1000 samples
ok    FILTERED: expected every sample within 1.5 .. 2.5, saw 1.6953 .. 2.30469 over 1000 samples
```

Checking the input as well costs nothing and makes a failure easy to read:
you see what went in beside what came out.

## When it fails

```text
FAIL  FILTERED: expected every sample within 1 .. 3, saw 1.69546 .. 4.97 over 1000 samples
```

The highest value is far outside the range, the lowest is not: the window
started while the filter was still coming down from an earlier value. Let it
settle before the window -- `simulation.advance(...)` -- or reset the input at
the end of the test that raised it.

```text
FAIL  FILTERED: expected every sample within 1 .. 3, saw nothing recorded
```

Nothing was published on that channel in the window. Either the number is
wrong -- use `simulation.channel("NAME").channel_id` -- or the firmware stopped
publishing.

## Variations

- **Calibration.** `reaches(expected, tolerance=...)` at several input levels
  with [`parametrize`](sweeps.md) checks a scale factor across the range.
- **Saturation.** Apply more than the range allows and check that the output
  `stays_between` its limits rather than wrapping around.
