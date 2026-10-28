# Your first test

This walks through a test of the blinky example that ships with
`looper-core`. Blinky is small enough to keep in your head:

- an LED on pin `LED_STATUS` toggles every 500 ms,
- and every 100 ms while the button on pin `BUTTON_MODE` is pressed -- the
  button is active low, so pressed means `low` --
- or while the current it measures on channel `SHUNT_CURRENT` is above 4 A.
  It filters that current and publishes the result on channel `FILTERED`.

Everything below is what the example really answers.

## 1. Start the simulation and look around

Create `tests/test_blinky.py`:

```python
import looper

DEFINITION = "../looper-core/examples/blinky/looper.toml"


def test_the_simulation_starts():
    with looper.run(DEFINITION, virtual=True) as simulation:
        print(simulation.firmware_name, simulation.time_mode.value)
        for pin in simulation.pins():
            print(pin)
        for channel in simulation.channels():
            print(channel)
```

```console
$ uv run pytest -s tests/test_blinky.py
blinky virtual
Pin(pin_id=17, name='LED_STATUS', level='low', is_drivable=False)
Pin(pin_id=4, name='BUTTON_MODE', level='high', is_drivable=True)
Channel(channel_id=0, name='SHUNT_CURRENT', unit='A', direction='input', value=0.0, is_drivable=True, display_value='no data')
Channel(channel_id=1, name='FILTERED', unit='A', direction='output', value=0.0, is_drivable=False, display_value='no data')
.
```

`looper.run` did four things: it started `looper-cli run`, which built the
simulation and started it, connected to the server `looper-cli` started
beside it, and checked that the two speak the same contract. When the
`with` block ends, all of it stops again.

`virtual=True` puts the simulation on a virtual clock. It stands still until
the test lets time pass, which makes every run of the test see exactly the
same thing. The clock is at zero: nothing has run yet.

## 2. Expect something

```python
def test_the_led_blinks_and_nothing_is_allocated():
    with looper.run(DEFINITION, virtual=True) as simulation:
        simulation.advance(1.0)  # let the firmware settle first

        check = simulation.expect()
        check.firmware_is_alive()
        check.call("adapter_blinky_gpio_set").happened_at(2.0, tolerance=0.1)
        check.memory().never_allocates()
        check.stack().no_deeper_than(16)

        report = check.evaluate(for_seconds=2.0)
        assert report, report.summary
```

```{figure} ../images/evaluate-steps.svg
:alt: Declare, clear, let time pass, observe, check.

`expect()` collects expectations; `evaluate` does the rest in one call.
```

`check.evaluate(for_seconds=2.0)` clears what was recorded so far, lets two
seconds of simulated time pass, reads back what happened and checks every
expectation against it. It returns an `ExpectationReport`, which is true
when everything was met. `assert report, report.summary` is the idiom: the
summary becomes the failure message.

## 3. Make it fail, and read why

Change the rate to `10.0` and run it again:

```text
FAILED tests/test_blinky.py::test_the_led_blinks_and_nothing_is_allocated
AssertionError: 3 of 4 met
FAIL  adapter_blinky_gpio_set: expected 10 Hz +/- 10%, saw 2 Hz
ok    the firmware: expected still calling the adapter, saw 24008 calls
ok    the heap: expected no allocation at all, saw 0 allocations
ok    the stack: expected at most 16 frames, saw 4 frames at the deepest
```

```{figure} ../images/report-anatomy.svg
:alt: The heading says how many were met; failures come first; each line says what was expected and what was seen.

Every line says what was checked, what was expected and what was seen.
```

## 4. Set the scene

Now press the button and expect the faster rate:

```python
def test_pressing_the_button_makes_the_led_blink_faster():
    with looper.run(DEFINITION, virtual=True) as simulation:
        button = simulation.pin("BUTTON_MODE")
        assert simulation.toggle_pin(button.pin_id) == "low"  # pressed

        check = simulation.expect()
        check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)

        report = check.evaluate(for_seconds=2.0)
        assert report, report.summary
```

```text
1 of 1 met
ok    adapter_blinky_gpio_set: expected 10 Hz +/- 5%, saw 9.5 Hz
```

9.5 rather than 10: the window starts at the very beginning, and the first
toggle comes 100 ms into it. Let the firmware settle first
(`simulation.advance(1.0)`) and it is exactly 10.

`simulation.pin("BUTTON_MODE")` finds a pin by the name the firmware gave it.
A name that does not exist is refused with the names there are:

```text
looper.SimulationRefusedError: the firmware registered no pin named 'BUTTON'; it has BUTTON_MODE, LED_STATUS
```

## 5. Share the simulation between tests

Building and starting takes about half a second when nothing changed. For a
module of tests, start the simulation once in a fixture:

```python
import pytest
import looper


@pytest.fixture(scope="module")
def simulation():
    with looper.run(DEFINITION, virtual=True) as started:
        yield started
```

How to keep tests that share a simulation independent of each other is in
[Tests in pytest and CI](../guides/pytest.md).

## Where to go from here

- [How it works](../concepts.md): what happens between your test and the firmware.
- [Setting the scene](../guides/scene.md): pins, analog signals, bus messages and time.
- [Expecting things](../guides/expectations.md): every expectation and what it means.
- [Recipes](../recipes/index.md): concrete questions about a firmware, answered.
