"""The PWM part of the scripted inspector: fixed outputs, and measurements written down."""

from __future__ import annotations

from looper.application.ports import SimulationRefusedError
from looper.domain.model.pwm import (
    PinMeasurement,
    PwmChange,
    PwmMeasurement,
    PwmOutput,
    PwmOutputs,
)
from looper.domain.model.triggers import Polarity

#: The outputs a scripted firmware has: a motor at 20 kHz and 37.5 %, and an LED that is off.
MOTOR = PwmOutput(
    1, "MOTOR", enabled=True, duty=0.375, frequency_hz=20_000.0, text="20.0 kHz · 37.5 % · center"
)
LED = PwmOutput(2, "LED", text="off · 1.0 kHz · 0.0 % · edge", state_text="off")


class ScriptedPwms:
    """Answers the PWM questions from fixed outputs and measurements, and writes the asks down."""

    def __init__(self) -> None:
        self.pwm_outputs = PwmOutputs(outputs=(MOTOR, LED))
        self.pwm_measurements: dict[int, PwmMeasurement] = {}
        self.pin_measurements: dict[int, PinMeasurement] = {}
        self.pin_delays: dict[tuple[int, int], PinMeasurement] = {}
        self.delay_asks: list[tuple[int, int, int, int, tuple[Polarity, Polarity]]] = []
        self.measure_asks: list[tuple[str, int, int, int]] = []
        self.pwm_changes: tuple[PwmChange, ...] = ()

    def read_pwms(self) -> PwmOutputs:
        return self.pwm_outputs

    def measure_pwm(self, pwm_id: int, from_us: int, to_us: int) -> PwmMeasurement:
        self.measure_asks.append(("pwm", pwm_id, from_us, to_us))
        if pwm_id not in self.pwm_measurements:
            raise SimulationRefusedError(f"there is no PWM output {pwm_id}")
        return self.pwm_measurements[pwm_id]

    def measure_pin(self, pin_id: int, from_us: int, to_us: int) -> PinMeasurement:
        self.measure_asks.append(("pin", pin_id, from_us, to_us))
        return self.pin_measurements.get(pin_id, PinMeasurement(pin_id, from_us, to_us))

    def measure_pin_delay(
        self,
        pin_id: int,
        reference_pin_id: int,
        from_us: int,
        to_us: int,
        edges: tuple[Polarity, Polarity] = (Polarity.RISE, Polarity.RISE),
    ) -> PinMeasurement:
        self.delay_asks.append((pin_id, reference_pin_id, from_us, to_us, edges))
        unmeasured = PinMeasurement(pin_id, from_us, to_us, reference_pin_id=reference_pin_id)
        return self.pin_delays.get((pin_id, reference_pin_id), unmeasured)
