"""Reading the PWM outputs and the pulses of pins, for a window or right now (free).

A window's PWM expectations need the outputs as they stood when it began,
so they are read before the recording is cleared; what each output did in
the window -- its measurement and its changes -- is read once the window
is in hand. A pin is measured the same way, by its name, once the window
has passed, since the firmware registers its pins only when it starts.

A server says in its description whether it has PWM outputs and whether
it measures pins. Without that, a test is refused with a sentence that
says what is missing, rather than failing on an unknown call.
"""

from __future__ import annotations

from typing import Any

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import Description
from looper.domain.model.pwm import (
    PinMeasurement,
    PwmChange,
    PwmOutput,
    PwmOutputs,
    PwmWindow,
)

#: The capabilities, as `Description.capabilities` names them.
PWM_CAPABILITY = "pwm"
PIN_MEASURE_CAPABILITY = "pin_measure"

#: Why a test cannot look at a PWM output or measure a pin on this server.
NO_PWM = (
    "this simulation has no PWM outputs (CAPABILITY_PWM): describe [pwm.NAME] in "
    "contract.toml, and run a looper-srv that knows them"
)
NO_PIN_MEASURE = (
    "this server does not measure a pin's pulses (CAPABILITY_PIN_MEASURE): "
    "run a looper-srv that knows MeasurePin"
)


def require(description: Description, capability: str, refusal: str) -> None:
    """Refuse with `refusal` unless the server offers `capability`."""
    if capability not in description.capabilities:
        raise SimulationRefusedError(refusal)


def read_outputs(inspector: Inspector, description: Description) -> PwmOutputs:
    """Every PWM output with its state now.

    Raises:
        SimulationRefusedError: If the simulation has no PWM outputs.
    """
    require(description, PWM_CAPABILITY, NO_PWM)
    return inspector.read_pwms()


def output_named(outputs: PwmOutputs, name: str) -> PwmOutput:
    """The output called `name`, or a refusal that says which there are."""
    found = outputs.named(name)
    if found is None:
        raise SimulationRefusedError(
            f"contract.toml lists no PWM output named {name!r}; it lists {outputs.names}"
        )
    return found


class PulseWindow:
    """The PWM outputs and pins one window's expectations are about, read around it."""

    def __init__(self, inspector: Inspector) -> None:
        self._inspector = inspector
        self._pwm_names: list[str] = []
        self._pin_names: list[str] = []
        self._start = PwmOutputs()

    def wants_pwm(self, name: str) -> None:
        """Have the window read and measure this output."""
        if name not in self._pwm_names:
            self._pwm_names.append(name)

    def wants_pin(self, name: str) -> None:
        """Have the window measure this pin."""
        if name not in self._pin_names:
            self._pin_names.append(name)

    def begin(self) -> None:
        """Check what the server offers, and read the outputs before the recording is cleared.

        Raises:
            SimulationRefusedError: If the server has no PWM outputs or does
                not measure pins, and an expectation needs them.
        """
        if not self._pwm_names and not self._pin_names:
            return
        description = self._inspector.describe()
        if self._pin_names:
            require(description, PIN_MEASURE_CAPABILITY, NO_PIN_MEASURE)
        if self._pwm_names:
            self._start = read_outputs(self._inspector, description)

    def observed(
        self, start_us: int, end_us: int, changes: tuple[PwmChange, ...]
    ) -> dict[str, Any]:
        """The window's outputs and pins, as `Observation` takes them; none when unwanted."""
        observed: dict[str, Any] = {}
        if self._pwm_names:
            observed["pwm_outputs"] = self._start
            observed["pwm_windows"] = self._pwm_windows(start_us, end_us, changes)
        if self._pin_names:
            pin_ids = {pin.name: pin.pin_id for pin in self._inspector.read_pins()}
            observed["pin_names"] = tuple(pin_ids)
            observed["pin_measurements"] = self._pin_measurements(pin_ids, start_us, end_us)
        return observed

    def _pwm_windows(
        self, start_us: int, end_us: int, changes: tuple[PwmChange, ...]
    ) -> dict[str, PwmWindow]:
        """What each wanted output that the contract lists did over the window."""
        windows: dict[str, PwmWindow] = {}
        for name in self._pwm_names:
            output = self._start.named(name)
            if output is None:
                continue
            measurement = self._inspector.measure_pwm(output.pwm_id, start_us, end_us)
            own = tuple(change for change in changes if change.pwm_id == output.pwm_id)
            windows[name] = PwmWindow(output, start_us, own, measurement)
        return windows

    def _pin_measurements(
        self, pin_ids: dict[str, int], start_us: int, end_us: int
    ) -> dict[str, PinMeasurement]:
        """The measurement of each wanted pin the firmware registered."""
        return {
            name: self._inspector.measure_pin(pin_ids[name], start_us, end_us)
            for name in self._pin_names
            if name in pin_ids
        }
