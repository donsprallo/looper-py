# Recipes

Each recipe starts from a question you have about your firmware and ends with
a test that answers it. They use the blinky example of `looper-core` where it
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
| Does a bus carry what it should, and is nothing refused? | [Bus](bus.md) | `nothing_refused`, `carried_at_least` |
| Does it hold across a range of inputs? | [Sweeps](sweeps.md) | any, with `parametrize` |

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
