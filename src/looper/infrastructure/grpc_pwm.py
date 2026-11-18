"""The PWM calls over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.pwm_port import PwmInspector
from looper.domain.model.pwm import PinMeasurement, PwmMeasurement, PwmOutputs
from looper.domain.model.triggers import Polarity
from looper.infrastructure import pwm_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.trigger_translation import POLARITIES

EMPTY = contract.Empty()


class GrpcPwmCalls(PwmInspector):
    """The PWM outputs and the measurements, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    def read_pwms(self) -> PwmOutputs:
        """Every output with its state now."""
        return pwm_translation.outputs_of(self._call(self._stub.ObservePwms, EMPTY))

    def measure_pwm(self, pwm_id: int, from_us: int, to_us: int) -> PwmMeasurement:
        """One output over a stretch."""
        request = contract.PwmMeasureRequest(pwm_id=pwm_id, from_us=from_us, to_us=to_us)
        return pwm_translation.pwm_measurement_of(self._call(self._stub.MeasurePwm, request))

    def measure_pin(self, pin_id: int, from_us: int, to_us: int) -> PinMeasurement:
        """One pin over a stretch."""
        request = contract.PinMeasureRequest(pin_id=pin_id, from_us=from_us, to_us=to_us)
        return pwm_translation.pin_measurement_of(self._call(self._stub.MeasurePin, request))

    def measure_pin_delay(
        self,
        pin_id: int,
        reference_pin_id: int,
        from_us: int,
        to_us: int,
        edges: tuple[Polarity, Polarity] = (Polarity.RISE, Polarity.RISE),
    ) -> PinMeasurement:
        """One pin over a stretch, with its delay from the reference pin's edges."""
        reference_edge, edge = edges
        request = contract.PinMeasureRequest(
            pin_id=pin_id,
            from_us=from_us,
            to_us=to_us,
            reference_pin_id=reference_pin_id,
            reference_edge=POLARITIES[reference_edge],
            edge=POLARITIES[edge],
        )
        return pwm_translation.pin_measurement_of(self._call(self._stub.MeasurePin, request))
