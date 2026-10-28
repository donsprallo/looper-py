# Installation

A test written with looper-py needs three things:

| What | Why | Check with |
| --- | --- | --- |
| Python 3.13 or newer | the library and your tests | `python --version` |
| the `looper-cli` command from `looper-core` | it builds, starts and serves the simulation | `looper-cli --version` |
| a C compiler (`gcc` or `clang`) | the simulation is your firmware, compiled for your computer | `gcc --version` |

looper-py itself depends only on `grpcio` and `protobuf`. It does not import
`looper-core`; it starts `looper-cli` as a separate program and talks to it.

## Step 1: make `looper-cli` available

`looper-cli` comes with `looper-core`. Either install it as a tool, so that
it is on your `PATH` everywhere:

::::{tab-set}

:::{tab-item} uv
```console
$ uv tool install ../looper-core
$ looper-cli --version
looper 0.1.0
```
:::

:::{tab-item} pipx
```console
$ pipx install ../looper-core
$ looper-cli --version
looper 0.1.0
```
:::

::::

or leave it in its checkout and tell looper-py how to run it. The library
reads the command from the `LOOPER_CLI` environment variable:

::::{tab-set}

:::{tab-item} bash
```console
$ export LOOPER_CLI="uv run --project ../looper-core looper-cli"
```
:::

:::{tab-item} PowerShell
```console
PS> $env:LOOPER_CLI = "uv run --project ../looper-core looper-cli"
```
:::

::::

The same command can also be passed to [`looper.run`](../guides/reaching.md)
as `looper_cli=...`, which is handy in a `conftest.py`.

## Step 2: add looper-py to your test environment

From a checkout beside your project:

::::{tab-set}

:::{tab-item} uv
```console
$ uv add --dev --editable ../looper-py
```
:::

:::{tab-item} pip
```console
$ pip install -e ../looper-py
```
:::

::::

Then check that the import works:

```console
$ python -c "import looper; print(looper.__version__)"
0.1.0
```

```{note}
The distribution is called `looper-py`, the package is `looper`. Do not
install `looper-py` into the same environment as `looper-core` itself: both
carry the inspector contract, and the two copies collide in one process.
Install `looper-core` as a tool, or point `LOOPER_CLI` at its own
environment, as above.
```

## Step 3: a project the library can run

`looper.run` takes the build definition of a simulation, the `looper.toml`
that `looper-core` reads. If your firmware has none yet, start with the
example that ships with `looper-core`:

```console
$ ls ../looper-core/examples/blinky/looper.toml
../looper-core/examples/blinky/looper.toml
```

How to write a `looper.toml` for your own firmware is described in
{core}`Building a simulation <building.html>`. For tests it is worth turning
on the instruments that the memory and stack expectations read:

```toml
[simulation]
# ... headers, contract, sources, includes ...

# Debug information, so that the build can be read.
warnings = ["-Wall", "-g"]
# Measure the stack depth: check.stack()
profile = true
# Watch the allocator: check.memory()
track_allocations = true
```

Next: [Your first test](first-test.md).
