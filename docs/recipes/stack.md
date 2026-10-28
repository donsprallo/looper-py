# How deep does the stack get?

**The question.** Will the firmware's call depth -- and with it its stack --
fit on the target, and does it stay that way?

**Why it is worth a test.** A stack overflow on a microcontroller rarely
announces itself; it overwrites whatever lies below and fails somewhere else.
A test that guards the depth fails the build instead.

## Prerequisite

The simulation has to be built with the profile on, which measures every
call:

```toml
# looper.toml
[simulation]
profile = true
```

Without it, stack expectations **fail** with
`saw nothing instrumented ran in this build`.

## Example

```python
def test_the_call_depth_stays_shallow(simulation):
    check = simulation.expect()
    check.stack().no_deeper_than(16)
    check.stack().stays_below(1024)

    report = check.evaluate(for_seconds=2.0)
    assert report, report.summary
```

```text
2 of 2 met
ok    the stack: expected at most 16 frames, saw 4 frames at the deepest
ok    the stack: expected at most 1024 bytes of stack, saw 352 bytes at the deepest
```

## Frames or bytes?

| | `no_deeper_than(frames)` | `stays_below(bytes)` |
| --- | --- | --- |
| measures | how deep calls nest | stack bytes at the deepest moment |
| carries over to the target | **yes** -- the nesting is your code's | no -- frame sizes are your computer's |
| use it for | a guard that means the same on the board | noticing that something changed |

Size the target's stack from the deepest path and the frame sizes of the
board's compiler; {rs}`Memory analysis step by step <analysis/memory.html>`
in looper-rs walks through it.

## When it fails

```text
FAIL  the stack: expected at most 3 frames, saw 4 frames at the deepest
```

Something nests deeper than the limit. The {rs}`Memory page <gui/memory.html>`
of looper-rs shows the deepest path, function by function.

## Choosing the limit

Leave room for harmless change: when the firmware is at 4 frames, a limit of
16 catches a recursion or a deep new call chain, and a limit of 4 fails on the
next refactoring that adds one helper function.
