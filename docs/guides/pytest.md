# Tests in pytest and CI

looper-py has no test runner of its own; it is made to be used from pytest.
This page collects the patterns that make a firmware test suite fast,
independent and easy to read when it fails.

## A fixture for the simulation

Put the simulation in a fixture in `tests/conftest.py`, so every test asks
for it by name:

```python
# tests/conftest.py
from pathlib import Path

import pytest
import looper

DEFINITION = Path(__file__).parents[1] / "looper.toml"


@pytest.fixture(scope="module")
def simulation():
    """The firmware, built once per test module and started with a held clock."""
    with looper.run(DEFINITION, virtual=True) as started:
        yield started
```

```python
# tests/test_led.py
def test_the_led_blinks(simulation):
    simulation.advance(1.0)

    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(2.0, tolerance=0.1)

    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary
```

### Which scope

| Scope | Starts the simulation | Good for |
| --- | --- | --- |
| `function` | for every test | tests that change inputs and must not see each other |
| `module` | once per file | a file of related tests that leave the scene as they found it |
| `session` | once per run | read-only checks, or a suite that resets everything itself |

Starting is cheap -- about half a second for an unchanged build -- so
`function` scope is a reasonable default when in doubt. Building happens on
the first start only; later starts find nothing to compile.

## Keeping tests independent

Tests that share a simulation share its state: a pressed button, an applied
signal, and the simulated time. Two habits keep them independent:

1. **Leave the scene as you found it.** Release what you pressed, remove the
   signal you applied -- in a `finally`, or in a fixture of its own:

   ```python
   @pytest.fixture
   def over_current(simulation):
       shunt = simulation.channel("SHUNT_CURRENT")
       simulation.apply_signal(shunt.channel_id, looper.Signal(offset=5.0))
       simulation.advance(1.0)
       yield simulation
       simulation.apply_signal(shunt.channel_id, looper.Signal())
       simulation.advance(1.0)


   def test_an_over_current_blinks_fast(over_current):
       check = over_current.expect()
       check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)
       report = check.evaluate(for_seconds=2.0)
       assert report, report.summary
   ```

2. **Do not depend on absolute time.** `simulated_seconds` keeps growing from
   test to test. Measure differences, and let `evaluate` choose the window.

`evaluate` clears the recordings and measurements itself, so those never leak
from one test into the next.

## Many cases, one simulation

`pytest.mark.parametrize` runs one test over many inputs. With a module
scoped simulation, all of them run against one started firmware:

```python
@pytest.mark.parametrize("amps, hertz", [(0.0, 2.0), (3.5, 2.0), (4.5, 10.0), (8.0, 10.0)])
def test_the_blink_rate_follows_the_current(simulation, amps, hertz):
    shunt = simulation.channel("SHUNT_CURRENT")
    simulation.apply_signal(shunt.channel_id, looper.Signal(offset=amps))
    simulation.advance(1.0)

    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(hertz, tolerance=0.15)
    report = check.evaluate(for_seconds=2.0)

    simulation.apply_signal(shunt.channel_id, looper.Signal())
    assert report, report.summary
```

More in the recipe [Does it hold across a range of inputs?](../recipes/sweeps.md).

## Marking tests that need a simulation

Firmware tests need a C compiler and `looper-cli`. Mark them, so a developer
without them can still run the rest:

```python
# tests/conftest.py
import shutil

import pytest

needs_simulation = pytest.mark.skipif(
    shutil.which("gcc") is None and shutil.which("clang") is None,
    reason="no C compiler on PATH",
)
```

```python
from conftest import needs_simulation


@needs_simulation
def test_the_led_blinks(simulation):
    ...
```

## Seeing what the firmware printed

What `looper-cli` and the firmware print goes to the test's error stream.
pytest shows it under *Captured stderr* for a failed test, and always with
`pytest -s`.

## Watching a test in a window

To see what a test does, start `looper-cli run` yourself, open a looper-rs
window on it, and point the test at it with `looper.connect`:

```console
$ looper-cli run looper.toml --virtual --listen 127.0.0.1:50051
$ looper-rs --server 127.0.0.1:50051
```

```python
@pytest.fixture(scope="module")
def simulation():
    address = os.environ.get("LOOPER_SERVER")
    if address:
        with looper.connect(address) as attached:
            yield attached
        return
    with looper.run(DEFINITION, virtual=True) as started:
        yield started
```

```console
$ LOOPER_SERVER=127.0.0.1:50051 pytest tests/test_led.py
```

## In CI

A CI job needs Python, uv, a C compiler and the `looper-core` checkout. For
GitHub Actions on Linux:

```yaml
name: firmware tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: firmware
      - uses: actions/checkout@v4
        with:
          repository: your-org/looper-core
          path: looper-core
      - uses: actions/checkout@v4
        with:
          repository: your-org/looper-py
          path: looper-py
      - uses: astral-sh/setup-uv@v5
      - run: sudo apt-get install -y gcc
      - run: uv tool install ./looper-core
      - working-directory: firmware
        run: |
          uv add --dev --editable ../looper-py
          uv run pytest --junitxml=report.xml
```

On a held clock the results do not depend on how busy the CI machine is:
the same commit gives the same report on every run.
