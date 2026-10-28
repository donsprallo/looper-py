# API reference

Everything a test needs is importable from `looper` itself:

```python
import looper

looper.run, looper.connect                        # reaching a simulation
looper.Simulation, looper.Expectations            # what you work with
looper.Signal, looper.BusMessage                  # what you send
looper.Pin, looper.Channel, looper.Bus            # what you read
looper.ExpectationReport, looper.Outcome          # what comes back
looper.TimeMode
looper.SimulationRefusedError, looper.SimulationUnreachableError
looper.LooperCliError, looper.ContractMismatchError
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

.. autoclass:: looper.TimeMode
   :members:
   :undoc-members:
```

## Errors

```{eval-rst}
.. autoexception:: looper.SimulationRefusedError

.. autoexception:: looper.SimulationUnreachableError

.. autoexception:: looper.LooperCliError

.. autoexception:: looper.ContractMismatchError
```
