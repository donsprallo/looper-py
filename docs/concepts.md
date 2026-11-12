# How it works

You can write tests without reading this page. Read it when a test does
something you did not expect -- most surprises come from one of the five
ideas below.

## 1. Your test talks to a server, not to the firmware

```{figure} images/system-overview.svg
:alt: Your test talks gRPC to looper-srv run, which builds and runs the simulation and talks to it over pipes.

Three processes: your test, `looper-srv run`, and the simulation.
```

The simulation is your firmware compiled for your computer, linked with the
looper runtime and a device model that plays the hardware. It has exactly one
client: the `looper-srv run` process that started it. That process serves
everybody else -- your test, a {rs}`looper-gui <index.html>` window -- over
gRPC, through the *inspector contract*.

`looper.run` starts that process for you and stops it when you are done:

```{mermaid}
sequenceDiagram
    autonumber
    participant T as your test
    participant C as looper-srv run
    participant S as simulation
    T->>C: starts it: run looper.toml --listen 127.0.0.1:0
    C->>C: generates and compiles (only what changed)
    C->>S: starts it, pipes on stdin and stdout
    C-->>T: "listening on 127.0.0.1:50123"
    T->>C: Describe: which contract, which firmware, which clock
    loop the test
        T->>C: set the scene, let time pass, read
        C->>S: asks over the pipes
        S-->>C: answers
        C-->>T: answers
    end
    T->>C: closes its standard input
    C->>S: closes the pipe
    S-->>C: ends its loop
```

Because the boundary is a process, your test environment needs only this
library and the `looper-srv` program -- none of its dependencies.

The library starts `looper-srv` unless you name another command (`server=`
or `LOOPER_SRV`, in that order). A {rs}`looper-gui <index.html>`
window starts **looper-srv** in the same way, so a test and the window talk
to the same kind of server and the same contract; see
[Starting and attaching](guides/reaching.md).

## 2. There is one simulation, and everybody looks at it

Any number of clients may look at one simulation: two tests, a test and a
window. They all see the same firmware. Whatever one of them changes, it
changes for all of them:

| Shared by everybody | Each client's own |
| --- | --- |
| a driven pin, an applied signal, a message put on a bus | how much of the timeline it shows |
| the recordings and the measurements -- and clearing them | which bus it shows as a conversation |
| the clock, and letting time pass | where it has read the recordings up to |

`evaluate` clears the recordings and the measurements before it watches, so
that a check sees its own window. If a looper-gui window is looking at the same
simulation, it sees them cleared as well. That is the honest arrangement --
they are looking at one firmware -- and it is why tests usually get a
simulation of their own (see [Starting and attaching](guides/reaching.md)).

## 3. A held clock runs in step with your test

A simulation's clock goes in one of three ways, and `simulation.clock_mode`
tells you which one it is right now:

`held` (`ClockMode.HELD`)
: The firmware runs only when a client lets time pass, exactly as long as it
  was let, and is then held again. While it is held it still answers every
  question -- it just does not move. A test sees the same thing on every run,
  on every machine, however loaded. `virtual=True` starts a simulation like
  this.

`paced` (`ClockMode.PACED`)
: The clock follows your computer's clock, at a speed the simulation names
  (1.0 is real time). This is what a person watching in a window needs. A
  test on it waits for real and sees slightly different things on every run.

`max` (`ClockMode.MAX`)
: The clock runs as fast as the computer allows.

The mode is not fixed at the start. Any client attached to the simulation --
a looper-gui window, another test -- can switch it while it runs, so
`clock_mode` asks the simulation each time you read it.

```{figure} images/lockstep.svg
:alt: On a held clock, simulated time stands still while the test sets the scene and reads, and moves only while the test lets time pass.

On a held clock, simulated time moves only where the test lets it.
```

Use the held clock for tests. `simulation.advance(seconds)` runs a held clock
for a span of simulated time outside of an `evaluate`, for instance to let the
firmware start up or a filter settle before you start checking. If the clock
is not held, `advance` is refused: a clock that runs by itself is not
something a test can steer. The refusal carries the server's words, such as
`the clock runs in real time and cannot be advanced`.

Sometimes a test wants the other two. `simulation.pace(10.0)` lets the clock
run by itself at ten times real time, `simulation.run_at_max()` as fast as
the computer allows, and `simulation.hold()` takes it back so that `advance`
works again. Reach for them when something outside the simulation has to keep
talking to the firmware while time passes -- a device scan over a modelled
bus, a protocol client of your own -- because on a held clock the firmware
runs only while you are advancing it, and answers nothing in between. A long
measurement is the other case: ten minutes of simulated time at ten times
real time cost one minute of waiting.

```{warning}
A paced clock *may* slip. When the computer cannot keep up, the simulation
re-anchors and gives the owed time away; `simulation.run_state()` reports how
much as `slipped_us`, and what it still owes as `behind_us`. A measurement
that counts on the pace reads those afterwards -- and reads its span from
`simulated_seconds`, never from your computer's clock.
```

```{note}
Every pass of the firmware's main loop costs a little simulated time -- 250
microseconds unless the application says otherwise -- and a firmware that
calls a delay costs that delay. So one second of simulated time is about four
thousand passes of a polling loop. On your computer that takes a few
milliseconds.
```

## 4. Expectations are declared first and checked afterwards

```{figure} images/evaluate-steps.svg
:alt: Declare, clear, let time pass, observe, check.

One `evaluate` call does steps 2 to 5.
```

`simulation.expect()` gives you an `Expectations` object. Each call on it --
`check.channel(...).reaches(...)`, `check.call(...).was_answered()` -- only
writes down what you expect. Nothing is read until `evaluate`:

1. **Clear** the recordings and the measurements, so the window starts empty.
   The clear starts a new recording for every client of the simulation.
2. **Let time pass**: run the clock if it is held, or wait if it runs by
   itself. The mode is read at the start of every window.
3. **Observe**: read the clock and the call counts together, then every
   recorded sample and exchange of the window, then the heap and the stack.
4. **Check** every expectation against that one observation, and return an
   `ExpectationReport`.

That ordering is what lets twenty expectations cost one reading of each
recording, and what lets an expectation look at the whole window rather than
at the instant it happened to run.

## 5. Two ways to say no

When the simulation cannot do what a test asked, the library tells you which
of two things happened:

`looper.SimulationRefusedError`
: The request was refused, and the message says why: an output pin driven,
  a signal applied to an output channel, a bus that takes no messages, time
  advanced on a clock that is not held, a name the firmware does not have. Your test
  asked for something the firmware does not allow -- fix the test.

`looper.SimulationUnreachableError`
: The simulation, or the server in front of it, stopped answering. The
  firmware may have crashed; what it printed is in your test's output.

A server that is too old or too new for this library is neither: it raises
`looper.ContractMismatchError` when you attach.

Everything else -- `looper-srv` not found, a build that failed -- is raised
when the simulation is started, as `looper.ServerStartError`. See
[Troubleshooting](troubleshooting.md).
