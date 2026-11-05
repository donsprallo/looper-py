# The profile and the findings

Two more things a test can ask of a simulation, both about the firmware as a
whole and not about one window of a run: **where the time goes** (the profile),
and **what the analysis of the code found** (the findings, a looper Pro part).

## The profile

The server weaves the firmware and the device model with instrumentation when
`looper.toml` says `profile = true`, and ranks what it measured.
`simulation.profile()` reads that ranking since the measurements were last
cleared:

```python
def test_the_median_is_not_the_heaviest_function(simulation):
    simulation.clear_measurements()          # profile one phase alone
    simulation.advance(5.0)

    profile = simulation.profile()
    assert profile.is_profiling              # without it every figure is zero
    heaviest = profile.heaviest("firmware")
    assert heaviest.name != "sort", heaviest
```

| Member | Gives |
| --- | --- |
| `profile.functions` | every measured function, as `ProfileEntry` |
| `profile.heaviest_first(origin=None)` | the functions by the time spent in themselves, heaviest first |
| `profile.heaviest(origin=None)` | the first of them, or `None` when nothing was measured |
| `profile.entry(name)` | one function's measurement, or `None` |
| `profile.is_profiling` | whether the build is woven at all |
| `profile.note` | what the server says, including why it is empty |

A `ProfileEntry` has the function's `name` and `origin` (`firmware`, `device
model`, `adapter`, `component`, `runtime` or `library`), its `calls`, the
`self_nanoseconds` and `total_nanoseconds`, and where it is written
(`source_path`, `line`). The ranking is by **self time**, because the total time
of `main` would always win.

```{important}
A profile measured on the host does not say how long anything takes on the
target. What carries over is the **ranking**: the function that is heaviest here
is, in a build of the same code, very likely heaviest there. A test therefore
asks about the order, never about nanoseconds.
```

As an expectation, over one window:

```python
check = simulation.expect()
check.profile().heaviest_is("sort", origin="firmware")
report = check.evaluate(for_seconds=5.0)
assert report, report.summary
```

```text
ok    the firmware profile: expected sort the heaviest, saw sort the heaviest, 25901234 ns in itself
```

Only a window with such an expectation reads the profile, because ranking it
takes the server a while.

## The findings (looper Pro)

The **Architect** of looper reads the firmware's code, not a run: layers and
what uses what, cycles, functions grown past a limit, uses of `malloc`.
`simulation.findings()` reads what it found, and a test says which findings may
be there -- typically none that the project's baseline does not already accept:

```python
def test_no_new_architecture_findings(simulation):
    findings = simulation.findings()           # waits up to 60 s for every file to be read
    assert findings.is_complete, findings.note
    assert not findings.new(), [one.title for one in findings.new()]
```

`findings(wait_seconds=60.0)` waits until the analysis has read every file,
because some findings -- a function that could be static, one never named --
are only looked for then; `is_complete` says whether it got that far.

| Member | Gives |
| --- | --- |
| `findings.findings` | every `Finding` |
| `findings.of_kind(kind)` | the findings of one kind, such as `"rule violation"` or `"cycle"` |
| `findings.new()` | the findings the baseline does not hold: what `looper-cli audit --architecture` fails on |
| `findings.between(from_module, to_module)` | the findings about one module using another |
| `findings.fixed` | keys the baseline accepts that are no longer found |

A `Finding` has its `key` (kind and subject, stable across edits: what a baseline
accepts), `kind`, `severity` (`good`, `noticeable` or `critical`), a one-line
`title`, an `explanation`, the `modules` and `dependencies` it is about, the
`function` if it is about one, and its `state` against the baseline: `new`,
`known` or `accepted` (`is_new`, `is_accepted`), with a `note`.

```python
violations = simulation.findings().of_kind("rule violation")
assert [one.modules for one in violations] == [("app/app", "hal/pins")]
assert violations[0].severity == "critical"
```

The server has to analyse the project's code: it does when `looper-cli run` or
`looper-cli inspect` was started from a `looper.toml` whose sources it can read;
otherwise `findings()` raises `SimulationRefusedError`.

### A licence

The Architect is looper Pro. A server without a licence that unlocks it refuses
the call, and the library raises **`looper.ProFeatureLockedError`**, a kind of
`SimulationRefusedError` (so code that handles refusals handles this too) with
its own type so that a test or a pipeline can tell a missing licence from a
firmware that said no. The message is the server's sentence: *The Architect is
part of looper Pro - no licence found (looked in ...)*.

```python
import pytest
import looper


def test_the_architecture(simulation):
    try:
        findings = simulation.findings()
    except looper.ProFeatureLockedError as error:
        pytest.skip(str(error))
    assert not findings.new()
```

`simulation.description.edition` is `"pro"` or `"free"`, and
`simulation.description.licence_note` says why it is free, or that the licence ran
out; read them to decide before asking. Measures of a single function -- the
`profile()` above -- stay free.

**In CI** the licence is a secret. Put the text of the licence file into it and
hand it over in `LOOPER_LICENSE`, which takes a path or the file's content:

```yaml
- name: Run the tests
  env:
    LOOPER_CLI: uv run --project ../looper-core looper-cli
    LOOPER_LICENSE: ${{ secrets.LOOPER_LICENSE }}
  run: uv run pytest
```

looper-cli reads the licence when it starts, and again at every restart of the
simulation. A licence that ran out still works for 14 days with a note, then
the Architect is locked again. Where looper looks for a licence, in what order,
is in {core}`looper Pro and the licence <usage.html#looper-pro-and-the-licence>`.
The `looper-cli audit --architecture` command does the same check in a build
step, with exit code 3 for a missing licence and 1 for a finding.
