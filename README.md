# looper-py

The Python library tests are written with for [`looper`](../looper-core)
simulations: start a simulation or attach to a running one, set the scene,
let time pass, and say what should then be true. The repository is
`looper-py`; what a test imports is `looper`.

```python
import looper


def test_pressing_the_button_makes_the_led_blink_faster():
    with looper.run("examples/blinky/looper.toml", virtual=True) as simulation:
        button = next(pin for pin in simulation.pins() if pin.name == "BUTTON_MODE")
        simulation.toggle_pin(button.pin_id)

        check = simulation.expect()
        check.call("adapter_blinky_gpio_set").happened_at_least(9)
        check.stack().no_deeper_than(64)

        report = check.evaluate(for_seconds=1.0)
        assert report, report.summary
```

A failure says what was expected and what was seen:

```text
1 of 2 met
FAIL  adapter_blinky_gpio_set: expected at least 9 calls, saw 2
ok    the stack: expected at most 64 frames, saw 11 frames at the deepest
```

## How it reaches a simulation

```text
your test (looper)            looper-core                    your firmware
+------------------+  gRPC   +-------------------------+ pipes +-------------+
| Simulation       | ------> | looper-cli run          | ----> | simulation  |
| Expectations     | <------ |  use cases -> contract  | <---- | (looper-rt) |
+------------------+         +-------------------------+       +-------------+
        inspector contract: looper_inspector.proto
```

The library speaks the inspector contract that `looper-cli run` serves, and
imports nothing of `looper-core`. That is what lets a test and the window
of [`looper-rs`](../looper-rs) look at one simulation together.

| Call | What it does |
| --- | --- |
| `looper.run(definition, virtual=..., build=..., looper_cli=...)` | starts `looper-cli run` for a build definition and attaches to it; closing stops it |
| `looper.connect(address)` | attaches to a `looper-cli run` that is already serving |

The command that runs looper-cli defaults to `looper-cli`, or to the
`LOOPER_CLI` environment variable, for example
`LOOPER_CLI="uv run --project ../looper-core looper-cli"`.

## What a test can do

| On `simulation` | |
| --- | --- |
| `firmware_name`, `time_mode`, `definition_path` | what the server said about it |
| `simulated_seconds`, `advance(seconds)` | the clock, and moving a virtual one on |
| `pins()`, `toggle_pin(pin_id)` | the pins, and driving an input |
| `apply_signal(channel_id, looper.Signal(...))` | a generated signal on an analog input |
| `send_bus_message(looper.BusMessage(...))` | one message onto a bus |
| `expect()` | begin declaring what should be true |

| Subject | Expectation |
| --- | --- |
| `check.channel(id, name)` | `stays_between(low, high)`, `reaches(value, tolerance, within_seconds)` |
| `check.bus(id, name)` | `nothing_refused()`, `carried_at_least(count)` |
| `check.call(function)` | `was_answered()`, `happened_at_least(count)`, `happened_at(hertz, tolerance)` |
| `check.memory()` | `never_allocates()`, `peak_below(bytes)`, `nothing_leaked()` |
| `check.stack()` | `no_deeper_than(frames)`, `stays_below(bytes)` |
| `check.firmware_is_alive()` | the firmware still reaches the adapter |

`evaluate(for_seconds)` clears the recordings and measurements, lets the
window pass -- advanced on a virtual clock, waited out on the host's -- reads
everything back once and checks every expectation against it. The clearing
reaches every client of the simulation, a window included: there is one
simulation.

A refusal -- a pin the firmware drives, a host clock asked to move -- raises
`looper.SimulationRefusedError`; a simulation that stopped answering raises
`looper.SimulationUnreachableError`.

## Documentation

The handbook in `docs/` explains what the library can answer about a firmware
and how, with recipes for concrete questions:

```console
$ uv run --group docs sphinx-build -W docs docs/_build
```

The figures are drawn by `docs/draw_figures.py`.

## Development

```console
$ uv sync
$ uv run pytest
$ uv run ruff check src tests && uv run mypy
```

The tests under `tests/integration` build and run the blinky example of a
`looper-core` checkout beside this one, and skip without it or without a C
compiler. `LOOPER_CORE` points at a checkout elsewhere.

The contract is `src/looper/infrastructure/contract/looper_inspector.proto`,
a copy of the schema in `looper-core`; `tests/test_contract_in_step.py` fails
when the two differ. After copying it over:

```console
$ uv run python scripts/generate_contract.py
```

How the code is organised, and the rules it keeps, is in `CLAUDE.md`.
