# Does the firmware allocate, or leak?

**The question.** Many firmware projects have a rule: no heap after start-up.
Others allow it, but nothing may leak. Does the firmware keep the rule?

**Why it is worth a test.** Rules like these are kept by reading code, and
break the day someone calls a library function that allocates behind the
scenes. On a host, the allocator can be watched, and the rule becomes a test.

## Prerequisite

The simulation has to be built with the allocator wrapped:

```toml
# looper.toml
[simulation]
track_allocations = true
```

Without it, every memory expectation **fails** with
`saw the allocator is not being watched in this build`.

## Example: no heap after start-up

```python
def test_nothing_is_allocated_after_start_up(simulation):
    check = simulation.expect()
    check.memory().never_allocates()

    report = check.evaluate(for_seconds=5.0)
    assert report, report.summary
```

```text
ok    the heap: expected no allocation at all, saw 0 allocations
```

The fixture lets one second pass before the test, so start-up -- where
allocating is allowed -- is outside the window.

## Example: allowed, but nothing leaks and it stays small

```python
def test_the_heap_stays_bounded(simulation):
    check = simulation.expect()
    check.memory().nothing_leaked()
    check.memory().peak_below(256)

    report = check.evaluate(for_seconds=5.0)
    assert report, report.summary
```

```text
2 of 2 met
ok    the heap: expected everything freed again, saw 0 allocated, 0 freed
ok    the heap: expected at most 256 bytes out at once, saw 120 bytes at the peak
```

## Reading the numbers

- `never_allocates` and `nothing_leaked` look at the window only. A block
  taken before it -- by the C runtime, by your start-up code -- is neither an
  allocation in the window nor a leak.
- `peak_below` looks at what was out at once, including what was taken before
  the window and is still held. The 120 bytes above are such a block, held by
  the C runtime from before the window.

## When it fails

```text
FAIL  the heap: expected no allocation at all, saw 3 allocations
```

Something allocated during the window. The {rs}`Memory page of looper-rs <gui/memory.html>`
shows where each block still out came from, by function.

```text
FAIL  the heap: expected everything freed again, saw 12 allocated, 9 freed
```

Three blocks taken during the window were not given back by its end. Run a
longer window: a leak grows with it, a buffer that is freed a little later
does not.
