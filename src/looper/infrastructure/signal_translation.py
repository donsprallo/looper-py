"""A generated signal, and a table file read for one, between the domain and the contract.

A signal goes out field for field, the same for an analog input and for a
generator of the graph. A pulse is the one waveform the server reads by its
low and high rather than its offset and amplitude; a pulse given only the
latter, as the server's own pytest export writes it, sends the two levels
they stand for.
"""

from __future__ import annotations

from looper.domain.model.signal_waves import Signal, TableFile
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The waveform read by its low and high.
PULSE = "pulse"


def signal_view_of(signal: Signal) -> contract.SignalView:
    """A signal as the contract carries it; a choice left empty is the server's first."""
    view = contract.SignalView(
        waveform=signal.waveform,
        amplitude=signal.amplitude,
        offset=signal.offset,
        frequency_hz=signal.frequency_hz,
        phase_degrees=signal.phase_degrees,
        rectification=signal.rectification,
        sweep_from_hz=signal.sweep_from_hz,
        sweep_to_hz=signal.sweep_to_hz,
        sweep_seconds=signal.sweep_seconds,
        sweep_spacing=signal.sweep_spacing,
        sweep_end=signal.sweep_end,
        table_times=signal.table_times,
        table_values=signal.table_values,
        table_between=signal.table_between,
        table_end=signal.table_end,
        table_time_scale=signal.table_time_scale,
    )
    if signal.duty is not None:
        view.duty = signal.duty
    if signal.waveform == PULSE:
        view.low, view.high = signal.levels
    return view


def table_file_of(message: contract.TableView) -> TableFile:
    """A table file as the server read it; the preview stays with the window."""
    return TableFile(
        path=message.path,
        problem_text=message.problem_text,
        summary_text=message.summary_text,
        columns=tuple(message.columns),
        value_column=message.value_column,
        rows=message.rows,
        times=tuple(message.times),
        values=tuple(message.values),
        simplified_text=message.simplified_text,
        max_error=message.max_error,
        hash=message.hash,
        warning_text=message.warning_text,
    )
