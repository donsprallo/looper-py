# looper-py

The Python library tests are written with for [`looper`](../looper-srv)
simulations: start a simulation or attach to a running one, set the scene,
let time pass, and say what should then be true. The repository is
`looper-py`; what a test imports is `looper`.

```python
import looper


def test_pressing_the_button_makes_the_led_blink_faster():
    with looper.run("../looper-docs/examples/blinky/looper.toml", virtual=True) as simulation:
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
your test (looper)            looper-srv                     your firmware
+------------------+  gRPC   +-------------------------+ pipes +-------------+
| Simulation       | ------> | looper-srv run          | ----> | simulation  |
| Expectations     | <------ |  use cases -> contract  | <---- | (looper-rt) |
+------------------+         +-------------------------+       +-------------+
        inspector contract: looper_inspector.proto
```

The library speaks the inspector contract that `looper-srv run` serves, and
imports nothing of looper's server. That is what lets a test and the window
of [`looper-gui`](../looper-gui) look at one simulation together.

| Call | What it does |
| --- | --- |
| `looper.run(definition, virtual=..., build=..., server=...)` | starts `looper-srv run` for a build definition and attaches to it; closing stops it |
| `looper.connect(address)` | attaches to a `looper-srv run` that is already serving |

The command that runs the server is looked up in this order: the argument
`server=`, the `LOOPER_SRV` environment variable, and then `looper-srv` on the
`PATH`, for example `LOOPER_SRV=../looper-srv/target/release/looper-srv`. The
old names `looper_cli=` and `LOOPER_CLI` are deprecated: they still work, with
a `DeprecationWarning`. A server that cannot be started, or that cannot build
the simulation, raises `looper.ServerStartError` (formerly `LooperCliError`,
which remains as a deprecated alias).

## What a test can do

| On `simulation` | |
| --- | --- |
| `firmware_name`, `definition_path` | what the server said about it |
| `clock_mode`, `simulated_seconds`, `advance(seconds)`, `advance_microseconds(us)` | how the clock goes (held, paced or max), where it is, and running a held one for a span |
| `pins()`, `toggle_pin(pin_id)` | the pins, and driving an input |
| `apply_signal(channel_id, looper.Signal(...))` | a generated signal on an analog input |
| `send_bus_message(looper.BusMessage(...))` | one message onto a bus |
| `exchanges(since)`, `read_events(since)` | reading the recorded traffic back, exchange by exchange or page by page |
| `clear_recordings()`, `clear_measurements()` | throwing away what was recorded and counted, between two phases of a test |
| `run_state()`, `timings()`, `memory()` | the run, the call counts and the heap and stack as they stand |
| `expect()` | begin declaring what should be true |
| `triggers.arm(looper.Edge(pin_id), ...)`, `triggers.current(trigger)`, `triggers.disarm_own()` | have the simulation watch for a pin edge, pattern, pulse width or value, and read when it fired |

| Subject | Expectation |
| --- | --- |
| `check.channel(id, name)` | `stays_between(low, high)`, `reaches(value, tolerance, within_seconds)` |
| `check.bus(id, name)` | `nothing_refused()`, `carried_at_least(count)` |
| `check.call(function)` | `was_answered()`, `happened_at_least(count)`, `happened_at(hertz, tolerance)` |
| `check.memory()` | `never_allocates()`, `peak_below(bytes)`, `nothing_leaked()` |
| `check.stack()` | `no_deeper_than(frames)`, `stays_below(bytes)` |
| `check.firmware_is_alive()` | the firmware still reaches the adapter |

`evaluate(for_seconds)` clears the recordings and measurements, lets the
window pass -- a held clock is run for it, a clock that runs by itself is
waited out -- reads everything back once and checks every expectation against
it. The clearing reaches every client of the simulation, a window included:
there is one simulation, and a clear starts a new recording for all of them.

A refusal -- a pin the firmware drives, a clock that is not held asked to
advance -- raises `looper.SimulationRefusedError` with the server's own words;
a simulation that stopped answering raises `looper.SimulationUnreachableError`.
The library speaks version 3 of the inspector contract.

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

The tests under `tests/integration` start looper-srv (`LOOPER_SRV_EXE`, by
default the debug build of a `looper-srv` checkout beside this one) and build
and run the test firmware in `fixtures/` of a `looper-docs` checkout beside this
one (`LOOPER_FIXTURES` points elsewhere); they skip without it or without a C
compiler. `LOOPER_TEST_SERVER=core` starts the reference, the historical
looper-core (`LOOPER_CORE`), instead.

The contract is `src/looper/infrastructure/contract/looper_inspector.proto`,
a copy of the schema in `looper-srv`; `tests/test_contract_in_step.py` fails
when the two differ. After copying it over:

```console
$ uv run python scripts/generate_contract.py
```

How the code is organised, and the rules it keeps, is in `CLAUDE.md`.
