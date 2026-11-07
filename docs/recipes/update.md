# Does an update survive losing its power?

**The question.** A device with a bootloader updates itself: it writes a new
application into a slot, asks the bootloader to try it, and resets. What happens
if the power goes in the middle of the write? If the new application never
confirms itself? Does the board always come back with *an* application?

**Why it is worth a test.** An update that breaks the device is the failure that
cannot be fixed in the field. On a board you cannot pull the power at byte 4097
of a flash write. In a simulation you can, and the word in flight is left
partly programmed the same way every time.

```{admonition} looper Pro
:class: important
The bootloader is looper Pro; partition names are free. See
[The bootloader from a test](../guides/bootloader.md).
```

## Prerequisite

`looper.toml` describes the images (`[[images]]`), what the flash holds at the
start (`[flash.initial]`) and the partition the board starts from
(`[flash] boot`), and the hardware layer has the roles `boot.jump`, the flash
roles and, for an anti-rollback counter, `otp.read` and `otp.burn`. The example
is `examples/boot_chain` of looper-docs; `COPY_UPDATE` (pin 4) makes the
application in slot A copy itself into slot B, and a power cut is armed for the
copy.

## Example: a cut in the middle leaves slot A running

```python
COPY_UPDATE = 4


def test_a_cut_in_the_middle_of_the_copy_leaves_a_running(simulation):
    simulation.power_cut(after_bytes=8192, during="flash.write", off_for_us=5000, seed=1)
    check = simulation.expect()
    check.boot_chain().went("stage0", "stage1_a", "app_a")
    check.flash().partition("app_b").is_invalid()
    simulation.toggle_pin(COPY_UPDATE)
    simulation.advance(0.012)
    simulation.toggle_pin(COPY_UPDATE)

    report = check.evaluate(for_seconds=0.1)
    assert report, report.summary
```

The cut comes while the firmware programs slot B. The board is off for 5 ms, comes
back with a power-on, and stage 0 and stage 1 pick slot A because the boot state
never asked for a trial of B. Releasing the button before the board comes back is
the bench's part; a button that stays held would start the copy again.

## Example: an update that never confirms is given up

```python
def test_an_unconfirmed_update_is_given_up_after_three_tries(simulation):
    flash = simulation.flash()
    flash.partition("app_b").write_image("app@2.1-unconfirmed")
    flash.partition("boot_state").write(0, ON_TRIAL, raw=True)
    simulation.reset()
    simulation.advance(0.4)

    chains = simulation.boot_chains()
    assert [chain.partitions[-1] for chain in chains[1:]] == ["app_b"] * 3 + ["app_a"]
```

`ON_TRIAL` is your firmware's boot state, laid down raw. The test reads the way
the board went from the boot chains; the three tries and the fall back are your
bootloader's, and the chains are how a test sees them.

## Example: every point, one after the other

```python
for after in looper.sweep_power_cuts(
    simulation, run_the_update, total_bytes=24576, every=4096, off_for_us=5000
):
    assert simulation.boot_chains()[-1].partitions[-1] == "app_a", after
```

`looper.sweep_power_cuts` lays the flash down as it was, resets the board with a
power-on, arms the cut and runs the update, once for each point. The armed cut
outlives that power-on and comes in the life it begins, so the sweep needs no
`advance` of its own. `off_for_us` is the time the board stays without power:
without it the bench still holds the update button when the board comes back, and
slot A copies itself again. See [Power cuts in turn](../guides/bootloader.md#power-cuts-in-turn).

## Reading the numbers

`power_cut` counts **the firmware's** flash bytes from the moment it is armed: a
write from your test is the bench, not the board, and does not count. An image
takes 64 bytes of header and its payload, so a cut inside the first
`64 + payload_size` bytes of a copy leaves the target partition broken (or without
a header, when it falls in the first word), and a cut
after them leaves a whole image that was never put on trial. An armed cut
outlives every reset and every jump, and comes in the next life with the bytes it
still waited for.
