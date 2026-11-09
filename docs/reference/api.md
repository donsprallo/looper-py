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
looper.LooperCliError, looper.ContractMismatchError
looper.ProFeatureLockedError                        # a looper Pro part without a licence
looper.Profile, looper.ProfileEntry               # where the time went
looper.Findings, looper.Finding, looper.Dependency  # what the architecture analysis found (Pro)
looper.SignalGraph, looper.SignalNodeKind         # a graph of signals and models
looper.BusReceived, looper.Sequence, looper.Fault, looper.ChainRun  # chains: conditions, logic, actions
looper.Life, looper.LifeDump, looper.Lives        # the firmware's lives
looper.ResetMark, looper.FlashMark                # resets and flash operations in the stream
looper.Retained, looper.Flash, looper.FlashPartition  # what survives a reset
looper.NodeOutput, looper.SignalModel, looper.ModelParameter
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

.. autoclass:: looper.BusMessage

.. autoclass:: looper.Pin

.. autoclass:: looper.Channel

.. autoclass:: looper.Bus

.. autoclass:: looper.Exchange
   :members:

.. autoclass:: looper.EventPage

.. autoclass:: looper.RunStatus

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

`simulation.apply_signal_graph(graph)` drives analog inputs from a graph and
`simulation.set_graph_value(node, value)` changes a value node of it;
`simulation.models()` and `simulation.model(name)` say which models the project
offers. See [Setting the scene](../guides/scene.md#a-graph-of-signals).

```{eval-rst}
.. autoclass:: looper.SignalGraph
   :members: generator, channel, pin, watch, value, operation, model, drive, probe

.. autoclass:: looper.SignalNodeKind
   :members:
   :undoc-members:

.. autoclass:: looper.NodeOutput

.. autoclass:: looper.SignalModel
   :members: output

.. autoclass:: looper.ModelParameter
```

### Chains

The event half of a graph: conditions, logic and actions that run inside the
simulation. The guide [Chains from a test](../guides/chains.md) explains them;
`simulation.chains()`, `simulation.switch_chain(group, on)`,
`simulation.run_until_chain(name, timeout_s)` and
`simulation.export_chain(group, run_for_s)` read, switch, run and export them.

```{eval-rst}
.. autoclass:: looper.SignalGraph
   :members: when, threshold, delay, counter, once, any_of, all_of, gate, logic, sequence, switch_signal, inject_fault, raise_interrupt, reset_firmware, send, reply, set_pin, mark, hold, link, group
   :noindex:

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

## Errors

```{eval-rst}
.. autoexception:: looper.SimulationRefusedError

.. autoexception:: looper.ProFeatureLockedError

.. autoexception:: looper.SimulationUnreachableError

.. autoexception:: looper.LooperCliError

.. autoexception:: looper.ContractMismatchError
```
