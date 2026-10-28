# Is a peripheral driver really implemented?

**The question.** The firmware calls an adapter function -- read a sensor, send
a frame, check whether the flash is ready. Does anything stand behind that
call in the simulation, or does the firmware get a zero back and carry on as
if everything were fine?

**Why it is worth a test.** looper generates every adapter function. One that
nothing implements returns the zero value of its type: `0`, `false`, a null
pointer. A firmware asking "is the flash ready?" hears "no" forever; one
asking "how many bytes arrived?" hears "none". The simulation runs, quietly
wrong.

## How

`check.call(function).was_answered()` counts the calls something implemented
-- a hook in the device model, a component on a bus -- against all calls.

## Example

```python
ADAPTER = [
    "adapter_blinky_gpio_get",
    "adapter_blinky_gpio_set",
    "adapter_blinky_measure",
    "adapter_blinky_publish",
    "adapter_blinky_is_ready",
]


def test_every_adapter_call_is_answered(simulation):
    check = simulation.expect()
    for function in ADAPTER:
        check.call(function).was_answered()

    report = check.evaluate(for_seconds=1.0)
    assert report, report.summary
```

```text
5 of 5 met
ok    adapter_blinky_gpio_get: expected every call answered, saw 2002 of 2002 answered
ok    adapter_blinky_gpio_set: expected every call answered, saw 2 of 2 answered
ok    adapter_blinky_measure: expected every call answered, saw 1000 of 1000 answered
ok    adapter_blinky_publish: expected every call answered, saw 1000 of 1000 answered
ok    adapter_blinky_is_ready: expected every call answered, saw 2000 of 2000 answered
```

## When it fails

```text
FAIL  adapter_can_init: expected every call answered, saw 0 of 1 answered
```

The firmware called it once, and nothing answered: the device model has no
hook for it. Either add one, or accept the zero and say so in the contract.

```text
FAIL  adapter_blinky_flash: expected implemented and called, saw never called
```

The firmware never called it in the window -- maybe it only does so at
start-up, before the window, maybe the name is misspelled. A function that is
only called at start-up is checked with a fresh simulation and a window from
the very start: no `advance` before `evaluate`.

## Before running anything

`looper-cli audit` answers the same question statically, from the headers and
the contract, without building or running anything -- see
{core}`Checking a simulation <checking.html>`. The test above answers it for
what the firmware really calls.
