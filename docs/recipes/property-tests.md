# Does the firmware survive every message?

**The question.** The firmware parses what arrives on a bus: commands over
UART, frames over CAN. You tried the messages you thought of. Does it also
survive the ones you did not -- a length field that lies, a command it does
not know, an argument at the top of its range?

**Why it is worth a test.** A parser is where a buffer overflows. A test with
ten hand-written messages checks ten; a property test states what must hold
for *every* message of a kind and lets [Hypothesis](https://hypothesis.readthedocs.io)
draw hundreds of them. When one fails, Hypothesis shrinks it to the smallest
message that still fails, which is usually the bug, spelled out.

`looper.strategies` draws messages field by field. It needs Hypothesis,
which is an optional dependency:

```console
uv add --dev "looper-py[hypothesis]"
```

## Example: every well-formed command is survived

Say the firmware takes commands on `CAN2` at identifier `0x6FF`: one byte of
command, one byte of length, that many bytes of argument, then a sum-8
checksum. Describe that once:

```python
import pytest
from hypothesis import given, settings

import looper
from looper import strategies

COMMAND = strategies.with_checksum(
    strategies.fields(
        strategies.one_of_values([0x01, 0x02, 0x10, 0x11], size=1),
        strategies.length_prefixed(strategies.raw(max_size=5)),
    ),
    strategies.sum8,
)


@pytest.fixture(scope="module")
def can():
    """The bus, read from a first start that also builds the firmware."""
    with looper.run("looper.toml", virtual=True) as simulation:
        yield simulation.bus("CAN2")


def test_every_command_is_survived(can):
    @settings(max_examples=200, deadline=None)
    @given(message=strategies.bus_messages(can, payloads=COMMAND, addresses=[0x6FF]))
    def survives(message):
        # A simulation of its own for every message: a fault ends only this
        # message's simulation, and the message Hypothesis shrinks to is the one
        # that caused it.
        with looper.run("looper.toml", virtual=True, build=False) as simulation:
            simulation.advance(1.0)  # past start-up
            simulation.send_bus_message(message)
            check = simulation.expect()
            check.firmware_is_alive()
            check.bus(can.bus_id, "CAN2").nothing_refused()
            report = check.evaluate(for_seconds=0.05)
            assert report, report.summary

    survives()
```

The checksum is computed *after* the fields are drawn, so every message gets
past the firmware's check and reaches the parser behind it. To test the check
itself, leave `with_checksum` out: then most messages are wrong on purpose.

When it fails, pytest shows the message Hypothesis shrank it to, such as
`BusMessage(bus_id=1, address=0x6FF, payload=b'\x10\x05\x00\x00\x00\x00\x00\x15')`:
command `0x10` with the longest argument. Put that message into an ordinary
test as a regression.

## The pieces

| Strategy | Draws |
| --- | --- |
| `unsigned(size, min_value=, max_value=, byteorder=)` | an unsigned field of `size` bytes |
| `signed(size, ...)` | a two's complement field |
| `one_of_values(values, size=1)` | one of the values an enumeration names |
| `raw(min_size, max_size)` | bytes nobody describes |
| `fields(*parts)` | the parts one after the other |
| `length_prefixed(body, size=1)` | a body behind a field holding its length |
| `with_checksum(payload, sum8)` | the payload and its checksum (`sum8`, `xor8`, or any function of the bytes) |
| `bus_messages(bus, payloads=, addresses=, extended=)` | messages for `send_bus_message`; never longer than the bus carries |

## Tips

- Every example starts a simulation of its own (`build=False`: the module
  fixture built the firmware once). With one simulation for all examples, the
  first fault would end it, every later example would fail as well, and
  Hypothesis would shrink to a message that has nothing to do with the bug. A
  start costs a moment, so a few hundred examples take minutes, not seconds.
- The `given` function lives inside the test so that it can use the
  `can` fixture; Hypothesis warns about function-scoped fixtures used
  directly in `@given`.
- `max_examples` sets how hard it tries. A few hundred is a good start; a
  nightly run can take thousands.
- Build the firmware with a sanitizer (`sanitizers = ["address", "undefined"]`
  in `looper.toml`, with clang) to catch a fault the moment it happens rather
  than when it finally crashes; the failure then names the line.
- This is black-box testing: Hypothesis does not see which code a message
  reached. Coverage-guided fuzzing of a firmware is planned for looper Pro.
