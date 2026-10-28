# Does a bus carry what it should?

**The question.** The firmware talks on a bus -- SPI to a sensor, I2C to an
expander, CAN to the rest of the vehicle. Is everything it sends taken by
something, and does enough cross the bus?

**Why it is worth a test.** A frame nobody takes is the simulation's way of
saying "on the board, nobody would have answered": a wrong chip select, a
wrong address, a filter that does not match. It is easy to miss in a log and
easy to check.

```{note}
The blinky example has no bus. The examples on this page assume a firmware
with a CAN bus the firmware calls `CAN2`; the reports are what such a
firmware answers.
```

## Example: nothing refused, enough traffic

```python
def test_the_can_bus_is_healthy(simulation):
    can = simulation.bus("CAN2")

    check = simulation.expect()
    check.bus(can.bus_id, "CAN2").nothing_refused()
    check.bus(can.bus_id, "CAN2").carried_at_least(10)

    report = check.evaluate(for_seconds=1.0)
    assert report, report.summary
```

## Example: provoke the firmware

On CAN and UART a test can put a message on the bus as another node would,
and check what the firmware makes of it:

```python
import looper


def test_a_request_frame_is_answered(simulation):
    can = simulation.bus("CAN2")

    simulation.send_bus_message(looper.BusMessage(bus_id=can.bus_id, address=0x6FF, payload=b"\x01\x02"))

    check = simulation.expect()
    check.bus(can.bus_id, "CAN2").nothing_refused()
    check.call("adapter_can_send").happened_at_least(1)

    report = check.evaluate(for_seconds=0.1)
    assert report, report.summary
```

On SPI and I2C the firmware is the master; a test does not send there, it
changes what the component on the bus answers. `simulation.bus(name).accepts_messages`
says which kind a bus is.

## When it fails

```text
FAIL  CAN2: expected nothing refused, saw 1 of 2 refused at 0x701
```

Something was put on the bus at address `0x701`, and nothing took it. The
looper-rs {rs}`bus page <gui/buses.html>` shows the exchange, and as a ladder
diagram who was talking to whom.

```text
FAIL  CAN2: expected at least 10 exchanges, saw 3
```

Less traffic than expected. When the recording overflowed, the report says so
and counts the lost exchanges as well:

```text
ok    CAN2: expected at least 10 exchanges, saw 3, and 12 more the recording could not keep
```
