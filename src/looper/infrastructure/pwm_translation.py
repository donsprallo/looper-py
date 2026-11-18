"""The PWM outputs, their changes and the measurements, from the contract into the domain."""

from __future__ import annotations

from typing import Any

from looper.domain.model.pwm import (
    PinMeasurement,
    PwmChange,
    PwmMeasurement,
    PwmOutput,
    PwmOutputs,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract

ALIGNMENTS = {contract.PWM_ALIGNMENT_EDGE: "edge", contract.PWM_ALIGNMENT_CENTER: "center"}
POLARITIES = {
    contract.PWM_POLARITY_ACTIVE_HIGH: "active high",
    contract.PWM_POLARITY_ACTIVE_LOW: "active low",
}


def outputs_of(message: contract.PwmList) -> PwmOutputs:
    """Every output in the contract's order, and why there are none."""
    return PwmOutputs(
        outputs=tuple(output_of(view) for view in message.pwms), state_text=message.state_text
    )


def output_of(view: contract.PwmView) -> PwmOutput:
    """One output with its state."""
    return PwmOutput(
        pwm_id=view.pwm_id,
        name=view.name,
        enabled=view.enabled,
        duty=view.duty,
        frequency_hz=view.frequency_hz,
        period_ns=view.period_ns,
        compare=view.compare,
        reload=view.reload,
        timer=view.timer,
        pin=view.pin,
        output=view.output,
        alignment=ALIGNMENTS.get(view.alignment, "edge"),
        polarity=POLARITIES.get(view.polarity, "active high"),
        full_scale=view.full_scale,
        mean=view.mean,
        changed_at_us=view.changed_at_us,
        text=view.text,
        state_text=view.state_text,
        output_text=view.output_text,
        detail_text=view.detail_text,
    )


def changes_of(batch: contract.EventBatch) -> tuple[PwmChange, ...]:
    """The changes of the PWM outputs on one page of the stream."""
    return tuple(
        PwmChange(
            pwm_id=event.pwm.pwm_id,
            sim_us=event.sim_us,
            enabled=event.pwm.enabled,
            duty=event.pwm.duty,
            period_ns=event.pwm.period_ns,
        )
        for event in batch.events
        if event.HasField("pwm")
    )


def pwm_measurement_of(message: contract.PwmMeasurement) -> PwmMeasurement:
    """One output over a stretch."""
    return PwmMeasurement(
        pwm_id=message.pwm_id,
        from_us=message.from_us,
        to_us=message.to_us,
        measured=message.measured,
        duty=message.duty,
        duty_min=message.duty_min,
        duty_max=message.duty_max,
        frequency_hz=message.frequency_hz,
        frequency_min_hz=message.frequency_min_hz,
        frequency_max_hz=message.frequency_max_hz,
        high_width_ns=message.high_width_ns,
        on_us=message.on_us,
        changes=message.changes,
        duty_text=message.duty_text,
        frequency_text=message.frequency_text,
        high_width_text=message.high_width_text,
        on_text=message.on_text,
        text=message.text,
        note=message.note,
    )


def pin_measurement_of(message: contract.PinMeasurement) -> PinMeasurement:
    """One pin over a stretch."""
    return PinMeasurement(
        pin_id=message.pin_id,
        from_us=message.from_us,
        to_us=message.to_us,
        measured=message.measured,
        rising_edges=message.rising_edges,
        falling_edges=message.falling_edges,
        pulses=message.pulses,
        high_width_min_us=message.high_width_min_us,
        high_width_max_us=message.high_width_max_us,
        high_width_mean_us=message.high_width_mean_us,
        low_width_min_us=message.low_width_min_us,
        low_width_max_us=message.low_width_max_us,
        periods=message.periods,
        period_min_us=message.period_min_us,
        period_max_us=message.period_max_us,
        period_mean_us=message.period_mean_us,
        frequency_hz=message.frequency_hz,
        duty=message.duty,
        high_us=message.high_us,
        high_width_text=message.high_width_text,
        frequency_text=message.frequency_text,
        text=message.text,
        note=message.note,
        **_delay_of(message),
    )


def _delay_of(message: contract.PinMeasurement) -> dict[str, Any]:
    """The delay from a reference pin, when the request named one."""
    if not message.HasField("reference_pin_id"):
        return {}
    return {
        "reference_pin_id": message.reference_pin_id,
        "delays": message.delays,
        "delay_min_us": message.delay_min_us,
        "delay_max_us": message.delay_max_us,
        "delay_mean_us": message.delay_mean_us,
        "delays_missed": message.delays_missed,
        "delay_text": message.delay_text,
    }
