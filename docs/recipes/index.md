# Recipes

Each recipe starts from a question you have about your firmware and ends with
a test that answers it. They use the blinky example of looper-docs (`examples/blinky`) where it
has what the recipe needs, and say so where they assume more -- a CAN bus,
say.

| Question | Recipe | Expectations it uses |
| --- | --- | --- |
| Does the firmware react to a button, a voltage, a current? | [Input reaction](input-reaction.md) | `happened_at`, `reaches` |
| Does a measurement get from the input to where it is used? | [Measurement path](measurement-path.md) | `reaches`, `stays_between` |
| Does something stand behind every adapter call? | [Hollow adapter](hollow-adapter.md) | `was_answered` |
| Does the firmware use the heap after start-up, or leak? | [Memory](memory.md) | `never_allocates`, `nothing_leaked`, `peak_below` |
| How deep does the stack get? | [Stack](stack.md) | `no_deeper_than`, `stays_below` |
| Does a periodic task keep its rate? | [Periodic task](periodic-task.md) | `happened_at` |
| What does the firmware do right after an event? | [Trigger reaction](trigger-reaction.md) | triggers instead of expectations |
| Is the firmware reset when it should be, and does it come back as it should? | [Reset](reset.md) | `reset(...).happened_once`, `no_loop`, `flash().no_violation` |
| Does an update survive a power cut, and does a bad one get rolled back? (Pro) | [Update](update.md) | `boot_chain().went`, `flash().partition(...).is_valid` |
| Does a bus carry what it should, and is nothing refused? | [Bus](bus.md) | `nothing_refused`, `carried_at_least` |
| Does it hold across a range of inputs? | [Sweeps](sweeps.md) | any, with `parametrize` |
| Does the firmware survive every message of a format? | [Property tests](property-tests.md) | `firmware_is_alive`, `nothing_refused`, with Hypothesis |

All recipes assume a `simulation` fixture like the one in
[Tests in pytest and CI](../guides/pytest.md):

```python
import pytest
import looper


@pytest.fixture
def simulation():
    with looper.run("looper.toml", virtual=True) as started:
        started.advance(1.0)  # past start-up
        yield started
```
