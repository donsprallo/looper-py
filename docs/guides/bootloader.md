# The bootloader from a test

```{admonition} looper Pro
:class: important
Everything on this page is **looper Pro**, except the partition names, which
stay free. Without a licence the calls raise `looper.ProFeatureLockedError`,
and a project with `[[images]]`, `[flash.initial]` or `[otp]` does not build.
See {learn}`Images, the bootloader and the power cut <manual/bootloader.html#what-the-edition-decides>`.
```

A device with a bootloader is several programs: a first stage, a second stage
with two copies of itself, an application in one of two slots. What goes wrong
goes wrong *between* them – a header that does not hold, an update that is cut
off in the middle, an application that never confirms itself. This guide is the
reference of what looper-py offers for it: **writing an image** into a partition,
reading **which image each life ran** and the **boot chains**, **cutting the
power**, reading and burning the **OTP**, the expectations on a boot chain and on
a partition's header, and the systematic power cut.

For a walk through on a small board, see
{learn}`Test an A/B update with a power cut <guides/test-an-update.html>`. What an
image, a header, a jump and a power cut *are* in a simulation, and how
`looper.toml` describes them, is in
{learn}`Images, the bootloader and the power cut <manual/bootloader.html>`.

The examples use `examples/boot_chain` of looper-docs: stage 0 in a read-only
partition, stage 1 in `stage1_a` and `stage1_b`, the application in `app_a` and
`app_b`, a `boot_state` partition and an OTP of 32 bytes. Its pin 4,
`COPY_UPDATE`, makes the application in A copy itself into B.

## The images

```python
for image in simulation.images():
    print(image.ref, image.built, image.version_text, image.payload_size)
```

`simulation.images()` returns every image of `[[images]]` in every variant, as
`Image`:

| Field | Meaning |
| --- | --- |
| `ref` | `app@2.1`, as `write_image` takes it; an image without variants is just `stage0` |
| `built` | whether it is built |
| `version_text` | `0x0201`, from the image's define `VERSION` |
| `payload_size` | bytes of its payload: its size on the target |
| `identity_hex` | which build it is, once built |
| `text` | the server's line for it |

In the example it lists `stage0`, `stage1@1.0`, `app@2.0`, `app@2.1`,
`app@2.1-unconfirmed` and `app@2.1-watchdog`. Without a licence it raises
`ProFeatureLockedError`.

## Writing an image into a partition

```python
flash = simulation.flash()
flash.partition("app_b").write_image("app@2.1")
flash.partition("app_b").write_image_file("builds/app-2.2.img")
```

`write_image(ref)` **erases the partition** and writes the built image behind its
header, padded to the flash word. A variant that is not built yet is built first,
silently. `write_image_file(path)` does the same with an image file, **whatever
its header names**: the server reads the path, so give it one the server can see.
A header that holds but names no built image is what a jump into it then finds –
see [A jump into an image looper does not know](#a-jump-into-an-image-looper-does-not-know).
A read-only partition – stage 0 – takes an image only from `[flash.initial]`; the
call raises `SimulationRefusedError`.

A broken header, a flipped bit, the bytes by hand are the ordinary
`flash.partition(...).write(offset, data, raw=True)` and are free.

### What a partition holds

```python
header = flash.partition("app_a").header()
print(header.state, header.text)         # valid  valid · app@2.0 · v0x0200
for name, header in flash.headers().items():
    print(name, header.state)
```

A `PartitionHeader` has the partition's `name`, the `state` and the server's
sentence `text`:

| `state` | `text` | When |
| --- | --- | --- |
| `valid` | `valid · app@2.1 · v0x0201` | the header and the payload hold, and the identity is a built image |
| `empty` | `empty (erased)` | erased |
| `broken` | `broken: the payload CRC does not match (stored …, computed …)` | the magic is there, but the header CRC, the payload CRC or the length does not hold |
| `unknown image` | `valid header, but no built image has identity 7f3a…e1` | the header holds, and nothing built has that identity |
| `no header` | `holds no image header` | no magic, and not erased: data, such as a boot state – or an image whose first bytes were hit, a magic a power cut stopped in its first word |

Without a licence there is no state and no text. `no header` is a state like the others: a partition with data is not startable, and `is_invalid()` counts it.
An image header begins with the four ASCII characters `LIMG`; the `LOOP` of early sketches does not apply. The header is read by the
server; your test only compares. Both the layout and the sentences are in
{learn}`the manual <manual/bootloader.html#the-image-header>`.

## Which image each life ran

The lives of the firmware carry the image and the partition:

```python
for life in simulation.lives():
    print(life.number, life.image, life.partition, life.entered_by)
# 1 stage0      stage0    power-on
# 2 stage1@1.0  stage1_a  jump
# 3 app@2.0     app_a     jump
```

`entered_by` says how a life began: `reset`, `jump` or `power-on`, and
`ended_by` how it ended: `reset`, `jump` or `power cut` (empty while it runs).
`Life.cause` is the cause of the reset that ended it, `power-on` for a life a
power cut ended, and **empty for a life a jump ended** – a jump is no reset, and
has no cause; `ended_by` says it. A **jump is
not a reset**: it ends the life of one image and begins the next with the clock,
the retained memory and the flash as they were, and it counts for no reset
expectation. Without images `image` and `partition` are empty.

### The boot chains

The lives between two resets are one **boot chain**: every life a reset or the
power began, and the lives the jumps began after it.

```python
for chain in simulation.boot_chains():
    print(chain.text, "|", chain.started_by, "|", chain.partitions)
# stage0 → stage1_a 1.0 → app_a 2.0 | power-on | ('stage0', 'stage1_a', 'app_a')
```

A `BootChain` has `steps` (a `BootStep` for each life: `life`, `image`,
`partition`, `at_us`, `text`), `started_by` – the cause of the reset that began
it, as the server says the word: `power-on`, `pin`, `software`, `watchdog` – and its `text`. `partitions` is
the partitions it went through, in the words `went` takes. The chains are the
run's, oldest first; looper does not know what a stage *is*, and the A/B logic is
your firmware's.

## Cutting the power

```python
simulation.power_cut(after_bytes=4096, during="flash.write", off_for_us=5000, seed=1)
simulation.power_cut(off_for_us=10_000)      # now
simulation.disarm_power_cut()                # take an armed cut back
```

| Argument | Meaning |
| --- | --- |
| `after_bytes` | the power goes after the firmware has programmed or erased so many more bytes, counted from now; `None` (the default) cuts it **now** |
| `during` | which of the firmware's flash calls count: `flash.write` (the default), `flash.erase` or `any`; anything else raises `ValueError` before it is sent |
| `off_for_us` | how long the board stays without power; the next life begins when it comes back |
| `seed` | which bits of the word in flight changed |

Only the **firmware's own flash calls count**: a write from your test is the
bench, not the board.

```{figure} ../images/power-cut-sweep.svg
:alt: The first 24 KiB of a partition B that the update copies into. An image of 64 bytes of header and 8192 bytes of payload fills the first 8256 bytes; the rest is erased. Cuts at 0, 4096 and 8192 bytes leave no header, a broken image and a broken image; cuts at 12288, 16384 and 20480 bytes leave a whole image that was not put on trial. Under it the state each cut leaves.

What a cut after so many bytes leaves in the partition the firmware copies an update into.
```

**The word in flight is partly programmed – and the same every time.** When the
power goes inside a flash call, the words before the one in flight are whole,
the words after it untouched, and that word keeps a part of the change: of the
bits that were to change, exactly those change for which
`splitmix64(seed ^ offset of the word ^ bit) & 1` holds, the offset counted from
the flash's beginning. Same seed, same firmware, same inputs: the same bytes. The
life that the cut ends reads `power cut` as its end in `Life.text`, and the
next life is entered by `power-on` after `off_for_us`; the retained memory is
cleared as for any power-on, unless the project says it has a battery.

**An armed cut outlives every reset and every jump.** It is the bench's switch,
not the firmware's, so a reset from outside, the watchdog's, the firmware's own
and a jump leave it armed, and the server arms it again in the next life with the
bytes it still waited for (this needs looper-rt 0.22.0, which the looper-rt
checkout beside looper-srv brings). After a hang, which says nothing of its own, the
cut keeps the count it had. Only the cut itself and `disarm_power_cut()` end it.

```python
simulation.power_cut(after_bytes=4096, off_for_us=5000)
simulation.reset()                    # the cut is still armed ...
simulation.advance(0.05)
print(simulation.run_state().power_cut_text)
# power cut armed: after 4096 bytes of a flash write
```

`RunState.power_cut_text` is what is armed, in the server's words, and empty when
nothing is; the window's header shows it as `PWR armed`.

A power cut is no cause of its own. The life it ends ends with `power cut`
(`Life.ended_by`), and the life after it begins with the cause `power-on`.

### Power cuts in turn

```python
def scenario(sim: looper.Simulation) -> None:
    sim.toggle_pin(COPY_UPDATE)
    sim.advance(0.012)
    sim.toggle_pin(COPY_UPDATE)
    sim.advance(0.1)


for after in looper.sweep_power_cuts(simulation, scenario, total_bytes=24576, every=4096):
    ...  # check what the cut at `after` bytes left
```

`sweep_power_cuts(simulation, scenario, total_bytes, every=4096, during="flash.write", off_for_us=0)`
runs the scenario once for every point a cut can come at, every `every` bytes
from 0 to `total_bytes`. It saves the flash once; for each point it lays the
flash down again, resets the firmware with a power-on, arms the cut after that
many bytes and runs the scenario, and then **yields the number of bytes** so
that your test checks the outcome before the next point. It is a generator, so
the check is yours: an assert with the point in its message, or the outcomes
collected in a dict.

The cut is armed right after the power-on is asked for, and it comes in the life
that power-on begins, because an armed cut outlives a reset. The sweep needs no
`advance` of its own, and a cut comes at **every** point, also on a held clock.

`off_for_us` is the time the board stays without power after each cut; the default
is 0. A scenario that presses a button and lets go of it later needs it: with no
time off, the board comes back while the bench still holds the button, and the
firmware does again what the button asked for. In the update of the example the
button makes slot A copy itself into B, so with `off_for_us=0` the copy finishes
on the second go and B is valid at every point. Give it more than the scenario
needs to let go of the button, 5000 for the example:

```python
for after in looper.sweep_power_cuts(
    simulation, scenario, total_bytes=24576, every=4096, off_for_us=5000
):
    outcomes[after] = simulation.flash().partition("app_b").header().state
```

`sweep_power_cuts` takes no seed. To cut with one, write the loop yourself: lay
the flash down, `reset("power-on")`, arm the cut with `seed=`, run the scenario.

## The OTP

```python
otp = simulation.otp()
otp.read()                    # the whole OTP, 32 bytes of zeros at the start
otp.read(0, 4)                # offset, length
otp.burn(0, b"\x03")
otp.burn(0, b"\x04")          # sets bit 2 and leaves the others: 0x07
```

**Burning sets bits**, as an OR: the bits that are 1 in the data are set and the
rest of the byte is left alone, and nothing takes a burned bit back. A burn that
would clear a bit is simply one that changes nothing, so there is no violation to
expect. The OTP is a file beside the flash – `build/otp.bin` with
`[flash] persist = true`, otherwise it begins with zeros at every run. `read`
returns empty bytes when the project has no `[otp]`.

## Expectations

```python
check = simulation.expect()
check.flash().partition("app_b").is_valid("app@2.1")
check.boot_chain().went("stage0", "stage1_a", "app_b")
simulation.reset()
report = check.evaluate(for_seconds=0.05)
assert report, report.summary
```

`check.boot_chain().went(*partitions)` expects **the last start of the board in
the window** to go through these partitions, in order. It reads
`stage0 → stage1_a 1.0 → app_b 2.1` when met, and names what it saw when not;
without any boot chain it fails with `no boot chain`.

`check.flash().partition(name)` expects something of one partition's **header at
the end of the window**:

| Expectation | Met when |
| --- | --- |
| `is_valid(image="")` | the header is `valid`, and names `image` when one is given |
| `is_invalid()` | the header is `broken`, `unknown image`, `empty` or `no header`: no image a bootloader would start |
| `is_empty()` | the partition is erased |

Without a licence the server gives no header state, and these are not met, with
*no header state (data, or looper Pro is not licensed)* in what they saw. A
partition that holds **no image header** – no magic, not erased – has the state
`no header`, so `is_invalid()` meets it, a cut in the first word of a copy
included.

## A jump into an image looper does not know

Write a header that holds and names no built image, and let a stage jump into it:

```python
simulation.flash().partition("app_b").write_image_file("foreign.img")
simulation.reset()
with pytest.raises(looper.SimulationRefusedError):
    simulation.advance(0.05)
print(simulation.run_state().hold_reason)
```

A jump into garbage is a crash on a board, and so the board stands still here:
the run is **held** with the reason *The firmware jumped to 0x0800C000 (app_b),
where the flash holds no image it can start: valid header, but no built image has
identity 0001…0f.* A running watchdog resets the board at its deadline instead.
`advance` raises `SimulationRefusedError` with the sentence, and so does any call
that needs the firmware, such as `toggle_pin`.

**The memories stay in reach while the board stands.** The flash, the retained
memory and the OTP are read as always (`flash().read`, `partition().read`,
`headers()`, `otp().read`), and an image can be written into a partition before
the reset:

```python
simulation.flash().partition("app_b").write_image("app@2.1")
simulation.reset()
simulation.advance(0.05)         # the board starts, and app_b runs
```

A write by the rules goes only onto whole, erased words (`write_image` erases its
partition first, so it always does); on anything else it raises
`SimulationRefusedError` – *The firmware is held: write it raw, or reset the
firmware first.* A raw write is allowed, a read-only partition takes none, and
**burning the OTP is refused** with the sentence of the hold. A write made while
the board stands records no flash mark.

A **reset from outside**
ends the hold: `simulation.reset()` starts the board from its boot partition
again. If stage 1 jumps into the same image again, the hold comes again; the boot
state's own rollback – three tries – is what then leaves it.

## Without a licence

Each of these raises `looper.ProFeatureLockedError`, a kind of
`SimulationRefusedError`, with a sentence: `images()`, `write_image`,
`write_image_file`, `boot_chains()`, `power_cut()`, `disarm_power_cut()` and the
OTP. `flash().headers()` answers without a state. A project with `[[images]]`
does not build.

## What is not built yet

- **Signatures.** An image header has a `signature_length`, always 0; nothing
  checks who made an image. They are not built, and will be when someone needs
  them.
- **Building an image from a test.** `write_image` builds the variant it needs
  and that is all; there is no call to build one, and no state *building* or
  *failed*.
- **An update over UART**, as an example. The update in the example is the
  application in A that copies itself into B.
