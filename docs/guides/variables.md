# Reaching the firmware's variables

A real device lets you reach only what its interface offers. A simulation
lets you reach every global of the firmware: a configuration byte that no
published schema describes is, here, simply a variable. The server reads the
debug information of the build, so the test needs no decoder of its own.

## The catalogue

```python
with looper.run("looper.toml", virtual=True) as simulation:
    for variable in simulation.variables():
        print(variable.variable_id, variable.path, variable.display_type)
```

```text
7 config.gain uint 1 B
```

A variable is found by its `variable_id`, not by its path: two translation
units may each declare a static of one name. When the build cannot be read,
`variables()` refuses and the message says why.

A firmware of ordinary size lists tens of thousands of variables, so ask once
and keep the result.

## Watching and writing

Only a watched variable can be read or written. Watching one gives a `Watch`,
and the number to write and remove it by is its `channel_id`:

```python
gain = next(one for one in simulation.variables() if one.path == "config.gain")

watch = simulation.watch_variable(gain.variable_id)
simulation.write_variable(watch.channel_id, 3.0)
simulation.advance(0.1)

print(simulation.watches()[0].display_value)

simulation.remove_watch(watch.channel_id)
```

Every change -- watching, writing, removing -- is acknowledged by the
simulation. When it declines, the call raises `looper.SimulationRefusedError`
with its reason, for example for a variable that is not in the catalogue or a
watch that is not writable.

`Watch.value` is the number, `display_value` is the value written the way its
own type reads, and `range_text` says what the variable can hold, for example
`uint8, 0 to 255`. `is_writable` says whether the server takes a write at all.
