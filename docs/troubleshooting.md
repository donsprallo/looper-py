# Troubleshooting

## When starting

`looper.LooperCliError: could not start 'looper-cli': ...`
: The `looper-cli` command was not found. Install `looper-core` as a tool
  (`uv tool install ../looper-core`), or tell the library how to run it with
  `LOOPER_CLI` or `looper_cli=` -- see [Installation](getting-started/installation.md).

`looper.LooperCliError: looper-cli stopped before it served (exit 1)`
: `looper-cli` ran but gave up: the build definition was not found, the
  headers could not be parsed, or the compiler rejected the code. What it
  printed is in the test's error output, just above -- run the test with
  `pytest -s` to see it as it happens.

`looper.ContractMismatchError: the server speaks contract version 3, this library 2; ...`
: `looper-cli` and this library were made for different versions of the
  inspector contract. Update whichever is older.

`looper.SimulationUnreachableError: no inspector server at 127.0.0.1:50051`
: `looper.connect` found nothing at that address. Check the line
  `listening on ...` that `looper-cli run` printed.

## While a test runs

`looper.SimulationRefusedError: the firmware registered no pin named 'BUTTON'; it has BUTTON_MODE, LED_STATUS`
: A name that does not exist. The message lists the ones that do.

`looper.SimulationRefusedError: unknown pin, or the pin is an output`
: The firmware drives that pin itself. Only inputs can be toggled.

`looper.SimulationRefusedError: unknown channel, or the channel is an output`
: A signal can only be applied to an input channel; outputs are what the
  firmware publishes.

`looper.SimulationRefusedError: that bus is not one the simulation models`
: The bus number is wrong, or the bus takes no messages (SPI, I2C).

`looper.SimulationRefusedError: the clock runs in real time and cannot be advanced`
: `advance` on a real-time simulation. Start it with `virtual=True`.

`looper.SimulationUnreachableError: The simulation closed the channel`
: The firmware stopped -- it crashed, called `exit`, or was killed. What it
  printed is in the test's error output.

## When a report surprises you

`saw nothing recorded`
: Nothing was recorded on that channel in the window. Check the number --
  `simulation.channel("NAME").channel_id` -- and that the firmware publishes
  it at all.

`saw never called`
: The firmware did not call that adapter function in the window. It may only
  do so at start-up, before the window, or the name may be misspelled.

`saw the allocator is not being watched in this build`
: The memory expectations need `track_allocations = true` in `looper.toml`.

`saw nothing instrumented ran in this build`
: The stack expectations need `profile = true` in `looper.toml`.

A rate a little off, such as `expected 2 Hz +/- 10%, saw 1.5 Hz`
: A slow event counted in a short window. Make the window several periods
  long -- see [Periodic task](recipes/periodic-task.md).

A range check that fails only on its first or last values
: The window caught a transient: the firmware was still settling from an
  earlier input. `simulation.advance(...)` before `evaluate`.

Results differ between runs
: The simulation runs on the computer's clock. Start it with `virtual=True`;
  on a virtual clock every run sees the same thing.

A test passes alone and fails in the suite
: Tests share a simulation and one of them left the scene changed -- a pin
  pressed, a signal applied. See
  [Keeping tests independent](guides/pytest.md#keeping-tests-independent).
