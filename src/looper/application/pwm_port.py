"""What the port answers about the PWM outputs and the pulses of a pin (free).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. Every number here is measured by the server, which is where
Logic gets the same numbers from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.pwm import PinMeasurement, PwmMeasurement, PwmOutputs


class PwmInspector(ABC):
    """The PWM outputs of contract.toml, and measuring them and a pin over a stretch."""

    @abstractmethod
    def read_pwms(self) -> PwmOutputs:
        """Every PWM output with its state now, in the contract's order."""

    @abstractmethod
    def measure_pwm(self, pwm_id: int, from_us: int, to_us: int) -> PwmMeasurement:
        """Duty, frequency and on time of one output over ``[from_us, to_us)``.

        Raises:
            SimulationRefusedError: If there is no such output, or no simulation.
        """

    @abstractmethod
    def measure_pin(self, pin_id: int, from_us: int, to_us: int) -> PinMeasurement:
        """Pulse widths, periods and frequency of one pin over ``[from_us, to_us)``.

        Raises:
            SimulationRefusedError: If there is no simulation.
        """
