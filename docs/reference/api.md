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
   :members: channel, bus, call, memory, stack, firmware_is_alive, add, evaluate

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
