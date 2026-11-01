# Starting and attaching

There are two ways to reach a simulation. Both return a
[`Simulation`](../reference/api.md), and both are used as a context manager.

| | `looper.run(definition, ...)` | `looper.connect(address)` |
| --- | --- | --- |
| what it does | builds the simulation, starts it, attaches | attaches to one that is already serving |
| when the block ends | stops the simulation | only lets go of it |
| typical use | tests, CI | debugging a test with a window open on the same simulation |

## `looper.run`

```python
import looper

with looper.run("path/to/looper.toml", virtual=True) as simulation:
    ...
```

| Argument | Default | Meaning |
| --- | --- | --- |
| `definition` | `looper.toml` in the working directory | the build definition of the simulation |
| `virtual` | `False` | start with a held clock, in step with the test -- what tests want |
| `build` | `True` | build first; `False` starts what was built last |
| `looper_cli` | `$LOOPER_CLI`, then `looper-cli` | the command that runs looper-cli, as text or as a list |

What `looper-cli` and the firmware print goes to the error stream of your
test process. pytest shows it for a failed test; `pytest -s` shows it always.

### Building, or not

`build=True` is cheap when nothing changed: `looper-cli` compiles only what
is out of date, which for an unchanged project is a check of a few file
times. Pass `build=False` when another step of your pipeline already built
the simulation and you want the test to fail rather than rebuild:

```python
with looper.run("looper.toml", virtual=True, build=False) as simulation:
    ...
```

### Telling it how to run looper-cli

```python
# as text, split at spaces
looper.run("looper.toml", looper_cli="uv run --project ../looper-core looper-cli")

# as a list, for paths with spaces in them
looper.run("looper.toml", looper_cli=["C:/Program Files/looper/looper-cli.exe"])
```

or once for the whole session, through the environment:

```console
$ LOOPER_CLI="uv run --project ../looper-core looper-cli" pytest
```

## `looper.connect`

Start `looper-cli run` yourself, on a fixed address:

```console
$ looper-cli run path/to/looper.toml --virtual --listen 127.0.0.1:50051
listening on 127.0.0.1:50051
```

and attach to it from a test, a notebook or the Python prompt:

```python
>>> import looper
>>> simulation = looper.connect("127.0.0.1:50051")
>>> simulation.firmware_name, simulation.definition_path
('blinky', '/home/me/fw/looper.toml')
>>> simulation.pins()
(Pin(pin_id=17, name='LED_STATUS', level='low', is_drivable=False), Pin(pin_id=4, name='BUTTON_MODE', level='high', is_drivable=True))
>>> simulation.close()
```

This is the way to watch a test in a {rs}`looper-rs <index.html>` window:
point the window at the same address (`looper-rs --server 127.0.0.1:50051`),
and step through the test. Remember that `evaluate` clears the recordings for
the window too.

## What a `Simulation` tells you about itself

```python
with looper.run("looper.toml", virtual=True) as simulation:
    simulation.firmware_name      # 'blinky'
    simulation.clock_mode         # ClockMode.HELD -- read from the simulation each time
    simulation.definition_path    # absolute path of the looper.toml it runs
    simulation.simulated_seconds  # 0.0 -- nothing has run yet
    simulation.description        # the name, the definition and the contract version
```

## Closing

Leaving the `with` block closes the simulation. Without a `with` block, call
`simulation.close()` yourself -- closing twice is fine. If your test process
is killed, `looper-cli` notices that its standard input closed and stops the
simulation anyway: nothing is left running.

## When the versions do not match

The library and the server compare the version of the inspector contract
they speak when they connect. If they differ, `looper.ContractMismatchError`
says which is which:

```text
looper.ContractMismatchError: the server speaks contract version 2, this library 3; update whichever is older
```

A server that predates the contract altogether does not even know its
methods; it is reported the same way, as `the server does not speak contract
version 3`.
