# API reference

Everything a test needs is importable from `looper` itself:

```python
import looper

looper.run, looper.connect                        # reaching a simulation
looper.Simulation, looper.Expectations            # what you work with
looper.Signal, looper.BusMessage                  # what you send
looper.Pin, looper.Channel, looper.Bus            # what you read
looper.Variable, looper.Watch                     # the firmware's variables
looper.ExpectationReport, looper.Outcome          # what comes back
looper.ClockMode
looper.Triggers, looper.Trigger                   # arming and reading triggers
looper.Edge, looper.Pattern, looper.EdgeWhile     # trigger conditions
looper.Width, looper.Quiet, looper.Value
looper.PinLevel, looper.Polarity, looper.Comparison
looper.TriggerMode, looper.TriggerState
looper.SimulationRefusedError, looper.SimulationUnreachableError
looper.ServerStartError, looper.ContractMismatchError  # LooperCliError: deprecated alias
looper.ProFeatureLockedError                        # a looper Pro part without a licence
looper.Profile, looper.ProfileEntry               # where the time went
looper.Findings, looper.Finding, looper.Dependency  # what the architecture analysis found (Pro)
looper.SignalGraph, looper.SignalNodeKind         # a graph of signals and models
looper.BusReceived, looper.Sequence, looper.Fault, looper.ChainRun  # chains: conditions, logic, actions
looper.Life, looper.LifeDump, looper.Lives        # the firmware's lives
looper.ResetMark, looper.FlashMark                # resets and flash operations in the stream
looper.Retained, looper.Flash, looper.FlashPartition  # what survives a reset
looper.NodeOutput, looper.SignalModel, looper.ModelParameter
looper.CompareSettings, looper.SignalGraphState, looper.GraphProbe, looper.PinTargetState  # the applied graph
looper.SampleMode, looper.SampleSettings, looper.TableFile  # sample and hold, a table read by the server
looper.LimitSettings, looper.SlewSettings          # a limit's limits, a slew rate's rates
looper.Starters, looper.Starter, looper.StarterNeeds  # the graphs to begin with
looper.PinDelay                                   # the delay between two pins a window measures
looper.SignalLabel, looper.LabelState, looper.BlockState, looper.GraphCapacity  # labels and what runs
looper.SwitchGroup, looper.GroupDo, looper.ChainGroupState, looper.GraphSwitchMark  # switching groups
looper.TimeModel, looper.TimeModelParameter, looper.ActiveTimeModel  # time models
looper.PwmOutput, looper.PwmOutputs               # the PWM outputs of contract.toml
looper.run_bench, looper.Bench                    # devices with joined buses on one clock (Pro)
looper.BenchState, looper.BenchDevice, looper.BenchPhase, looper.JoinedBus, looper.BenchMark
looper.JoinCandidates, looper.JoinCandidate, looper.JoinBusChoice  # joining from a running simulation
looper.BenchProLockedError                        # a bench refused for want of a licence
```

## Reaching a simulation

```{eval-rst}
.. autofunction:: looper.run

.. autofunction:: looper.connect
```

## The simulation

```{eval-rst}
.. autoclass:: looper.Simulation
   :members:
   :inherited-members:
   :exclude-members: __init__
```

## Expectations

```{eval-rst}
.. autoclass:: looper.Expectations
   :members: channel, bus, call, memory, stack, reset, flash, boot_chain, firmware_is_alive, add, evaluate

.. autoclass:: looper.application.subjects.ChannelExpectation
   :members:

.. autoclass:: looper.application.subjects.CallExpectation
   :members:

.. autoclass:: looper.application.subjects.MemoryExpectation
   :members:

.. autoclass:: looper.application.subjects.StackExpectation
   :members:

.. autoclass:: looper.application.subjects.BusExpectation
   :members:

.. autoclass:: looper.application.subjects.MessageExpectation
   :members:

.. autoclass:: looper.application.subjects.ProfileExpectation
   :members:

.. autoclass:: looper.application.subjects.ResetExpectation
   :members:

.. autoclass:: looper.application.subjects.FlashExpectation
   :members:

.. autoclass:: looper.application.subjects.PartitionExpectation
   :members:

.. autoclass:: looper.application.subjects.BootChainExpectation
   :members:
```

## What comes back

```{eval-rst}
.. autoclass:: looper.ExpectationReport
   :members:

.. autoclass:: looper.Outcome
   :members:
```

## What you send and read

```{eval-rst}
.. autoclass:: looper.Signal
   :members: pulse, table, from_csv, levels

.. autoclass:: looper.BusMessage

.. autoclass:: looper.Pin

.. autoclass:: looper.Channel

.. autoclass:: looper.Bus

.. autoclass:: looper.Exchange
   :members:

.. autoclass:: looper.EventPage

.. autoclass:: looper.RunStatus

.. autoclass:: looper.TimeModel

.. autoclass:: looper.TimeModelParameter

.. autoclass:: looper.ActiveTimeModel
   :members:

.. autoclass:: looper.CallTiming
   :members:

.. autoclass:: looper.MemoryUsage

.. autoclass:: looper.HeapUsage

.. autoclass:: looper.Variable

.. autoclass:: looper.Watch

.. autoclass:: looper.ClockMode
   :members:
   :undoc-members:
```

## The profile and the findings

`simulation.profile()` returns a `Profile`, `simulation.findings()` a
`Findings`; the guide [The profile and the
findings](../guides/profile-and-findings.md) explains how they are used.

```{eval-rst}
.. autoclass:: looper.Profile
   :members: heaviest_first, heaviest, entry

.. autoclass:: looper.ProfileEntry

.. autoclass:: looper.Findings
   :members: of_kind, new, between

.. autoclass:: looper.Finding
   :members: is_new, is_accepted

.. autoclass:: looper.Dependency
```

## Resets, lives and memories

`simulation.reset()` resets the firmware, `simulation.lives()` and
`simulation.life(n)` read its lives, `simulation.retained()` and
`simulation.flash()` reach what survives a reset; the guide [Resets, lives and the
memories](../guides/resets-and-memories.md) explains how they are used.

```{eval-rst}
.. autoclass:: looper.Life

.. autoclass:: looper.LifeDump

.. autoclass:: looper.Lives

.. autoclass:: looper.Retained
   :members:

.. autoclass:: looper.Flash
   :members:

.. autoclass:: looper.FlashPartition
   :members:

.. autoclass:: looper.ResetMark

.. autoclass:: looper.FlashMark
```

## PWM outputs

`simulation.pwms()` reads every PWM output of `contract.toml` with its state
now, `simulation.pwm(name)` one of them: `.duty` (0 to 1), `.frequency_hz`,
`.enabled` and the server's `.text`, such as `20.0 kHz · 37.5 % · center`.
Both raise `SimulationRefusedError` on a simulation without PWM outputs. The
checks of an output and of a pin's pulses are in the
[reference of expectations](expectations.md); they are free.

```{eval-rst}
.. autoclass:: looper.PwmOutputs
   :members: named

.. autoclass:: looper.PwmOutput
```

## The board

`simulation.board()` reads the device as a block diagram, as looper-srv
describes it: the MCU, its ports (pins and analog channels), the buses with
the devices on them, the contract's sources, DMA channels and PWM outputs, the
wires between them and the notes about what the picture cannot show. Every
text and key is the server's. `board.port("ZC")` is a port by its name, with
what drives it in the applied signal graph (`.driven_by_text`,
`.driven_by_node_key`) and what reads it (`.read_by`, `.read_by_text`);
`board.bus("SPI1").tap("AS8510").text` is where a chip hangs, `CS 0`. The
board has a `revision` and a `revision_text` that says what changed since the
one before.

`simulation.board_state()` reads its live state: `state.pin("ZC")` and
`state.channel("POT")` a port's `.state_text` and `.value`,
`state.tap("device:SPI1:0")` a chip's `.exchanges` and `.unanswered`,
`state.rail("SPI1")` a bus's exchanges and its last one, `.last_us`. A state of
another `revision` than the board's means the board is to be read again.

Both are free. Where the server shows no board -- a project's code without a
simulation -- they raise `SimulationRefusedError` with the server's sentence.

```{eval-rst}
.. autoclass:: looper.Board
   :members: port, bus, node, of_kind, mcu, devices, ports, buses

.. autoclass:: looper.BoardNode

.. autoclass:: looper.BoardBus
   :members: tap

.. autoclass:: looper.BoardTap

.. autoclass:: looper.BoardEdge

.. autoclass:: looper.BoardNote

.. autoclass:: looper.BoardGraphRef

.. autoclass:: looper.BoardState
   :members: node, pin, channel, rail, tap

.. autoclass:: looper.BoardNodeState

.. autoclass:: looper.BoardTapState
```

## A bench (Pro)

A bench is two to eight devices on this PC whose CAN buses are joined, each
with a server of its own, on one clock: looper-srv builds each device as a
library and a bench host runs them in lockstep and plays the bus between them
(looper-srv `docs/bench.md`). `looper.run_bench("bench.toml")` starts
`looper-srv run --bench bench.toml` and attaches to every device's server:

```toml
[bench]
name = "lab"

[[members]]
name = "thermostat"                 # the first member leads
project = "thermostat/looper.toml"  # beside bench.toml

[[members]]
name = "gateway"
project = "gateway/looper.toml"

[[joins]]
bus = "CAN1"
members = { thermostat = "CAN1", gateway = "CAN1" }
```

```python
with looper.run_bench("bench.toml") as bench:
    gateway = bench.member("gateway")          # a Simulation, through its own server
    bench.advance(0.25)                        # the whole bench, on held clocks
    status = gateway.bus_records("CAN1", sender="thermostat")
    assert status[0].acknowledged_by_text == "acknowledged by gateway"
    bench.hold()                               # returns once every device is held
    print(bench.state().device("gateway").state_text)
```

Every device runs on a held virtual clock. Run control from any device acts on
the whole bench; `bench.advance`, `bench.hold` and `bench.pace` go through the
leader, and `hold` and `pace` wait until every device followed.
`bench.state()` is the bench as the leader's server sees it: its devices, the
joined buses, the other devices' resets as `marks`. Those come from the other
servers within a fraction of a second, so a test that reset one device reads
the mark a moment later.

`simulation.bus_records(bus, sender=..., since=...)` reads the recorded frames
until the recording reached the clock, so a reading right after `advance`
sees the last frames too. On a bench a frame another device sent names it:
`sender_device` (what `sender="gateway"` matches; `sender="peer"` takes any
other device), `sender_text`, `acknowledged_by_text` and `refused_text`.
`RunStatus` carries the bench's texts, `bench_text`, `peer_stop_text`,
`bench_chip_text` and `bench_chip_hover_text`; the board a `PEER` node.

From two simulations that already run, `simulation.join_candidates("CAN1")`
lists the other servers on this PC, and `simulation.join_bus("CAN1",
candidate)` joins them: both servers build their devices as libraries and
restart into one host, this one leading; it returns once the bench formed.
`other.wait_for_bench()` waits for the other device, whose connection drops and
comes back as well. `simulation.leave_bench()` restarts every device alone.

A bench is Pro. Without a licence `run_bench` raises `BenchProLockedError`, a
`ServerStartError` and a `ProFeatureLockedError` at once, with the server's
sentence; the bench calls raise `ProFeatureLockedError`. A bench file that
does not fit, or a join the firmware has no bus for, raises `ServerStartError`
with the server's sentence; a join that did not go through raises
`SimulationRefusedError` with it.

```{eval-rst}
.. autofunction:: looper.run_bench

.. autoclass:: looper.Bench
   :members: member, member_names, leader, state, advance, advance_microseconds, hold, pace, close

.. autoclass:: looper.BenchState
   :members: device, device_names, this_device, leader

.. autoclass:: looper.BenchDevice

.. autoclass:: looper.BenchPhase

.. autoclass:: looper.JoinedBus

.. autoclass:: looper.BenchMark

.. autoclass:: looper.JoinCandidates
   :members: running

.. autoclass:: looper.JoinCandidate
   :members: preselected_bus

.. autoclass:: looper.JoinBusChoice
```

## Interrupts and DMA

`simulation.interrupts()` reads the interrupt sources and the lock,
`simulation.dma()` the DMA channels, `simulation.raise_interrupt(name, after_us)`
makes a source due, and `simulation.race(name)` is a `with` block that runs the
race mode (looper Pro). They return dataclasses (`Interrupts`, `InterruptSource`,
`InterruptLock`, `DmaChannels`, `DmaChannel`, `RaceCoverage`) whose fields the guide
[Interrupts and DMA from a test](../guides/interrupts-and-dma.md) lists. The checks
are in the [reference of expectations](expectations.md); every one is looper Pro.

```{eval-rst}
.. autoclass:: looper.Interrupts
   :members: source

.. autoclass:: looper.InterruptSource

.. autoclass:: looper.InterruptLock

.. autoclass:: looper.DmaChannels
   :members: channel

.. autoclass:: looper.DmaChannel

.. autoclass:: looper.RaceCoverage
   :members: complete
```

## The bootloader (Pro)

`simulation.images()`, `simulation.boot_chains()`, `simulation.power_cut()`,
`simulation.disarm_power_cut()` and `simulation.otp()` reach the bootloader's
parts; `flash.partition(name).write_image(...)` and `.header()` write an image
into a partition and read what it holds. The guide [The bootloader from a
test](../guides/bootloader.md) explains how they are used; the calls are looper
Pro, except for the partition names.

```{eval-rst}
.. autoclass:: looper.Image

.. autoclass:: looper.PartitionHeader

.. autoclass:: looper.BootChain
   :members:

.. autoclass:: looper.BootStep

.. autoclass:: looper.Otp
   :members:

.. autofunction:: looper.sweep_power_cuts
```

## Signal graphs

`simulation.apply_signal_graph(graph)` drives analog inputs and input pins from a
graph and `simulation.set_graph_value(node, value)` changes a value node of it;
`simulation.models()` and `simulation.model(name)` say which models the project
offers. `simulation.signal_graph()` reads the applied graph back -- its probes,
the pins it drives, its comparators, linked generators, selects, sample and
hold nodes, limits and slew rates, with a limit's `fault_text` -- and
`simulation.probe(name)` finds a probe's trace channel.
`simulation.read_table(path)` has the server read a CSV or PWL file for a Table
generator (`Signal.from_csv` does it in one step), and `simulation.starters()`
lists the graphs to begin with. `simulation.switch_groups(groups, blocks)`,
`switch_group(key, on)` and `switch_block(key, on)` switch groups and blocks of
the applied graph in one step, `simulation.graph_switches(since)` walks the
switches the stream recorded, and `simulation.chain_groups()` and
`chain_group(key)` read the groups. See [Setting the scene](../guides/scene.md#a-graph-of-signals),
[Comparators and input pins](../guides/scene.md#comparators-and-input-pins),
[Generators that move and signal logic](../guides/scene.md#generators-that-move-and-signal-logic) and
[Groups, labels and sums](../guides/scene.md#groups-labels-and-sums).

```{eval-rst}
.. autoclass:: looper.SignalGraph
   :members: generator, channel, pin, watch, value, operation, sum, compare, select, sample_hold, limit, slew_rate, model, label, set_signal, read_signal, switched_off, title, drive, drive_pin, probe

.. autoclass:: looper.SignalNodeKind
   :members:
   :undoc-members:

.. autoclass:: looper.NodeOutput

.. autoclass:: looper.CompareSettings

.. autoclass:: looper.SampleMode
   :members:
   :undoc-members:

.. autoclass:: looper.SampleSettings

.. autoclass:: looper.LimitSettings

.. autoclass:: looper.SlewSettings

.. autoclass:: looper.SignalGraphState
   :members: pin_target, node, node_state, label, value

.. autoclass:: looper.SignalLabel

.. autoclass:: looper.LabelState

.. autoclass:: looper.BlockState
   :members: is_live

.. autoclass:: looper.BlockLiveness
   :members:
   :undoc-members:

.. autoclass:: looper.GraphCapacity

.. autoclass:: looper.GraphValueState

.. autoclass:: looper.ChainGroupState

.. autoclass:: looper.GraphSwitchMark

.. autoclass:: looper.GraphProbe

.. autoclass:: looper.PinTargetState

.. autoclass:: looper.GraphNodeState

.. autoclass:: looper.TableFile
   :members: signal

.. autoclass:: looper.Starters
   :members: names, named

.. autoclass:: looper.Starter

.. autoclass:: looper.StarterNeeds

.. autoclass:: looper.SignalModel
   :members: output

.. autoclass:: looper.ModelParameter
```

### Chains

The event half of a graph: conditions, logic and actions that run inside the
simulation. The guide [Chains from a test](../guides/chains.md) explains them;
`simulation.chains()`, `simulation.chain_groups()`, `simulation.switch_chain(group, on)`,
`simulation.run_until_chain(name, timeout_s)` and
`simulation.export_chain(group, run_for_s)` read, switch, run and export them;
`simulation.read_dbc(path)` reads a DBC file's messages for the fields of a
message.

```{eval-rst}
.. autoclass:: looper.SignalGraph
   :members: when, threshold, delay, counter, once, any_of, all_of, gate, logic, sequence, switch_signal, switch_group, inject_fault, raise_interrupt, reset_firmware, send, reply, set_pin, mark, hold, link, group
   :noindex:

.. autoclass:: looper.DbcFile
   :members: message

.. autoclass:: looper.DbcMessage

.. autoclass:: looper.DbcSignal

.. autoclass:: looper.BusReceived

.. autoclass:: looper.BusTimeout

.. autoclass:: looper.Crossing
   :members:
   :undoc-members:

.. autoclass:: looper.Clock

.. autoclass:: looper.Start

.. autoclass:: looper.Interrupt

.. autoclass:: looper.ResetSeen

.. autoclass:: looper.Threshold

.. autoclass:: looper.Delay

.. autoclass:: looper.WhileWaiting
   :members:
   :undoc-members:

.. autoclass:: looper.Counter

.. autoclass:: looper.Logic

.. autoclass:: looper.Sequence

.. autoclass:: looper.Step

.. autoclass:: looper.StepKind
   :members:
   :undoc-members:

.. autoclass:: looper.BusSend

.. autoclass:: looper.BusReply

.. autoclass:: looper.Field

.. autoclass:: looper.SetPin

.. autoclass:: looper.PinDo
   :members:
   :undoc-members:

.. autoclass:: looper.Mark

.. autoclass:: looper.Hold

.. autoclass:: looper.SwitchSignal

.. autoclass:: looper.SignalDo
   :members:
   :undoc-members:

.. autoclass:: looper.SwitchGroup

.. autoclass:: looper.GroupDo
   :members:
   :undoc-members:

.. autoclass:: looper.Fault

.. autoclass:: looper.FaultKind
   :members:
   :undoc-members:

.. autoclass:: looper.ChainGroup

.. autoclass:: looper.ChainBlockState

.. autoclass:: looper.ChainRun

.. autoclass:: looper.SequenceState
   :members:

.. autoclass:: looper.SequenceProgress
   :members:
   :undoc-members:

.. autofunction:: looper.step_port
```

## Triggers

`simulation.triggers` is a `Triggers`; the guide [Triggers](../guides/triggers.md)
explains how they are used.

```{eval-rst}
.. autoclass:: looper.Triggers
   :members:

.. autoclass:: looper.Trigger
   :members: has_fired, is_live

.. autoclass:: looper.TriggerMode
   :members:
   :undoc-members:

.. autoclass:: looper.TriggerState
   :members:
   :undoc-members:

.. autoclass:: looper.Edge

.. autoclass:: looper.Pattern

.. autoclass:: looper.PinLevel

.. autoclass:: looper.EdgeWhile

.. autoclass:: looper.Width

.. autoclass:: looper.Quiet

.. autoclass:: looper.Value

.. autoclass:: looper.Polarity
   :members:
   :undoc-members:

.. autoclass:: looper.Comparison
   :members:
   :undoc-members:
```

## Strategies for property tests

Needs the optional dependency `hypothesis` (`looper-py[hypothesis]`).

```{eval-rst}
.. automodule:: looper.strategies
   :members: unsigned, signed, one_of_values, raw, fields, length_prefixed, with_checksum, sum8, xor8, bus_messages
```

## Errors

```{eval-rst}
.. autoexception:: looper.SimulationRefusedError

.. autoexception:: looper.ProFeatureLockedError

.. autoexception:: looper.SimulationUnreachableError

.. autoexception:: looper.ServerStartError

.. autoexception:: looper.BenchProLockedError

.. autoexception:: looper.ContractMismatchError
```
