# Installation

This page is what a test written with looper-py needs. Installing the whole
system – the window, the compilers, `gdb` – is described once, in
{learn}`Installation <getting-started/installation.html>` of looper-docs.

A test written with looper-py needs three things:

| What | Why | Check with |
| --- | --- | --- |
| Python 3.13 or newer | the library and your tests | `python --version` |
| the `looper-srv` program | it builds, starts and serves the simulation | `looper-srv --help` |
| a C compiler (`gcc` or `clang`) | the simulation is your firmware, compiled for your computer | `gcc --version` |

looper-py itself depends only on `grpcio` and `protobuf`. It starts
`looper-srv` as a separate program and talks to it.

## Step 1: make `looper-srv` available

`looper-srv` is built from its own checkout (`cargo build --release` in
`looper-srv`; the runtime `looper-rt` and the library `libclang` it needs are
described in {learn}`Installation <getting-started/installation.html>`). Either
put the program on your `PATH`, where the library finds it as `looper-srv`, or
leave it in its checkout and tell looper-py where it is. The library looks, in
this order, at the argument `server=` of `looper.run`, the environment
variable `LOOPER_SRV`, and then `looper-srv` on the `PATH`:

::::{tab-set}

:::{tab-item} bash
```console
$ export LOOPER_SRV="../looper-srv/target/release/looper-srv"
```
:::

:::{tab-item} PowerShell
```console
PS> $env:LOOPER_SRV = "../looper-srv/target/release/looper-srv"
```
:::

::::

A Windows installer that puts `looper-srv` and what it needs on the `PATH` is
coming; it is prepared but not built yet.

The same command can also be passed to [`looper.run`](../guides/reaching.md)
as `server=...`, which is handy in a `conftest.py`. (The older names,
`looper_cli=` and the environment variable `LOOPER_CLI`, still work but are
deprecated and warn.)

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
0.3.0
```

```{note}
The distribution is called `looper-py`, the package is `looper`.
```

## Step 3: a project the library can run

`looper.run` takes the build definition of a simulation, the `looper.toml`
that `looper-srv` reads. If your firmware has none yet, start with the
example in looper-docs:

```console
$ ls ../looper-docs/examples/blinky/looper.toml
../looper-docs/examples/blinky/looper.toml
```

How to write a `looper.toml` for your own firmware is described in
{learn}`Building a simulation <manual/building.html>`. For tests it is worth turning
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

Next: {learn}`Your first test <getting-started/first-test.html>`, which walks
through a test of the blinky example, or straight to
[Tests in pytest and CI](../guides/pytest.md) for how to keep tests that share a
simulation independent of each other.
