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
def simulation():
    with looper.run("looper.toml", virtual=True) as started:
        started.advance(1.0)  # past start-up
        yield started


def test_every_command_is_survived(simulation):
    can = simulation.bus("CAN2")

    @settings(max_examples=200, deadline=None)
    @given(message=strategies.bus_messages(can, payloads=COMMAND, addresses=[0x6FF]))
    def survives(message):
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

- One simulation serves every example: starting the firmware once per message
  would cost seconds each. The firmware's state therefore carries from one
  message to the next, as it would on the bus. If a failure depends on what
  came before, Hypothesis cannot shrink it reliably; restart in a fixture and
  run fewer examples.
- The `given` function lives inside the test so that it can use the
  `simulation` fixture; Hypothesis warns about function-scoped fixtures used
  directly in `@given`.
- `max_examples` sets how hard it tries. A few hundred is a good start; a
  nightly run can take thousands.
- This is black-box testing: Hypothesis does not see which code a message
  reached. Coverage-guided fuzzing of a firmware is planned for looper Pro.
