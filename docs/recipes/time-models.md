# Does it hold on both time models?

**The question.** The firmware runs on a simulated clock whose steps are decided
by a *time model*. Does the test mean what it says on every model, or only on
the one it was written on?

**Why it is worth a test.** A rate that the firmware keeps with a timer is a
statement about the firmware. A count of passes, or the instant a polling loop
notices an edge, is a statement about the time model as well. Running a test on
`fixed` and on `adaptive` tells the two apart: what holds on both is about the
firmware.

## How

Start the simulation on a model with `time_model=`, and run the test once for
each model with a parametrized fixture:

```python
import pytest
import looper


@pytest.fixture(params=["fixed", "adaptive"])
def simulation(request):
    with looper.run("looper.toml", virtual=True, time_model=request.param) as started:
        started.advance(1.0)  # past start-up
        yield started
```

`simulation.time_model.summary_text` names the model the test ran on, such as
`fixed · step_us=500` or `adaptive · min_step_us=1 · max_step_us=500 ·
time_read_cost_ns=1000`. Put it into the message of a failing assertion, so that
a failure says which model it was.

## Example: the LED blinks at 2 Hz, on both

Blinky counts its LED's period on the millisecond clock, and the time of the
firmware's clock is the same on every model, so the rate must not depend on it:

```python
def test_the_led_blinks_at_two_hertz(simulation):
    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(2.0, tolerance=0.1)

    report = check.evaluate(for_seconds=10.0)
    assert report, f"{simulation.time_model.summary_text}: {report.summary}"
```

```text
fixed · step_us=500: 1 of 1 met
ok    adapter_blinky_gpio_set: expected 2 Hz +/- 10%, saw 2 Hz
adaptive · min_step_us=1 · max_step_us=500 · time_read_cost_ns=1000: 1 of 1 met
ok    adapter_blinky_gpio_set: expected 2 Hz +/- 10%, saw 2 Hz
```

## Example: what a model *does* change

A call made in the loop is counted in passes, and how many passes there are in
a second of simulated time is what the time model decides. Blinky's
`adapter_blinky_measure` is called from its loop: in a run on the example it was
called at 3400 Hz on `fixed` with a step of 500 µs and at 3382 Hz on `adaptive`,
which takes a pass right at each event and fewer idle ones. A test that expects an exact number there belongs to one model
and should say so:

```python
@pytest.mark.parametrize("model", ["fixed"])
def test_the_measure_loop_runs_every_pass(model):
    with looper.run("looper.toml", virtual=True, time_model=model) as simulation:
        ...
```

Where a test is about the rate of something the firmware *does*, give it a
tolerance that holds on both, as above. Where it is about the resolution at which
the firmware sees time (a wait of a few microseconds, an edge noticed by polling),
run it on `adaptive`, which has a microsecond, and say so in the test.

## A restart changes the model without a build

A test that compares the two on one simulation restarts it:

```python
simulation.restart(time_model="fixed", time_params={"step_us": 100})
```

The restart begins at 0 s again and the recordings begin anew, so measure each
model from its start. `restart(from_definition=True)` goes back to what
`looper.toml` chooses. See [Concepts](../concepts.md) for the models and their
parameters, and the manual's
{learn}`Time and time models <manual/time.html>` for why.
