# looper-py

**looper-py** lets you write tests against your firmware without the board.
Your firmware runs on your computer as a looper simulation; a test starts it,
sets the scene -- presses a button, applies a current, puts a frame on a
bus -- lets time pass, and checks what the firmware did:

```python
import looper


def test_pressing_the_button_makes_the_led_blink_faster():
    with looper.run("examples/blinky/looper.toml", virtual=True) as simulation:
        simulation.toggle_pin(simulation.pin("BUTTON_MODE").pin_id)

        check = simulation.expect()
        check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)
        check.memory().never_allocates()
        check.stack().no_deeper_than(16)

        report = check.evaluate(for_seconds=2.0)
        assert report, report.summary
```

When something is wrong, the report says what was expected and what was seen
rather than only "failed":

```text
2 of 3 met
FAIL  adapter_blinky_gpio_set: expected 10 Hz +/- 5%, saw 2 Hz
ok    the heap: expected no allocation at all, saw 0 allocations
ok    the stack: expected at most 16 frames, saw 4 frames at the deepest
```

The distribution is called `looper-py`; in your code it is `import looper`.

## What you can find out with it

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Does the firmware react to its inputs?
:link: recipes/input-reaction
:link-type: doc

Press a button, apply a voltage or a current, and check that the firmware
reacts -- that an LED changes its rate, that a value is published, that a
call happens.
:::

:::{grid-item-card} Does a measurement path work end to end?
:link: recipes/measurement-path
:link-type: doc

Drive an analog input with a constant, a sine or a square wave and check
what the firmware makes of it: how fast it follows, and whether it stays in
range.
:::

:::{grid-item-card} Is a peripheral driver really implemented?
:link: recipes/hollow-adapter
:link-type: doc

Find the adapter functions nothing stands behind -- the ones that hand the
firmware a zero and let it believe it.
:::

:::{grid-item-card} Does the firmware allocate, or leak?
:link: recipes/memory
:link-type: doc

Turn "this firmware does not use the heap after start-up" and "nothing
leaks" into tests that fail when someone breaks them.
:::

:::{grid-item-card} How deep does the stack get?
:link: recipes/stack
:link-type: doc

Guard the call depth, so that a refactoring that nests five calls deeper
fails the build instead of the board.
:::

:::{grid-item-card} Does a periodic task keep its rate?
:link: recipes/periodic-task
:link-type: doc

Check that a sampling loop, a heartbeat or a blink runs at the frequency it
should -- exactly, on a held clock.
:::

:::{grid-item-card} Does a bus carry what it should?
:link: recipes/bus
:link-type: doc

Check that nothing on a bus is refused and that enough traffic crossed it,
and put messages on it to provoke the firmware.
:::

:::{grid-item-card} Does it hold across a range of inputs?
:link: recipes/sweeps
:link-type: doc

Run the same expectation over many input values with
`pytest.mark.parametrize`, without starting the simulation each time.
:::

::::

## How it fits together

```{figure} images/system-overview.svg
:alt: Your test talks gRPC to looper-cli run, which builds and runs the simulation and talks to it over pipes. A looper-rs window can look at the same simulation.

A test reaches the simulation through `looper-cli run`, which the library
starts for it. The looper-rs window can look at the same simulation while the
test runs.
```

The library speaks the inspector contract that `looper-cli run` serves. It
does not import `looper-core` and needs nothing of it installed in your test
environment -- only the `looper-cli` command. See [How it works](concepts.md).

## Where to start

| If you … | read |
| --- | --- |
| have not installed anything yet | [Installation](getting-started/installation.md) |
| want to see a test pass before reading anything else | [Your first test](getting-started/first-test.md) |
| want to know what happens when a test runs | [How it works](concepts.md) |
| have a concrete question about your firmware | [Recipes](recipes/index.md) |
| want to know every expectation there is | [Expecting things](guides/expectations.md) and the [reference](reference/expectations.md) |
| are setting up a test suite and CI | [Tests in pytest and CI](guides/pytest.md) |
| see an error you do not understand | [Troubleshooting](troubleshooting.md) |

```{toctree}
:hidden:
:caption: Getting started

getting-started/installation
getting-started/first-test
concepts
```

```{toctree}
:hidden:
:caption: Guides

guides/reaching
guides/scene
guides/variables
guides/expectations
guides/pytest
```

```{toctree}
:hidden:
:caption: Recipes

recipes/index
recipes/input-reaction
recipes/measurement-path
recipes/hollow-adapter
recipes/memory
recipes/stack
recipes/periodic-task
recipes/bus
recipes/sweeps
```

```{toctree}
:hidden:
:caption: Reference

troubleshooting
reference/expectations
reference/api
```
