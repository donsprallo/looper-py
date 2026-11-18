"""The PWM outputs and the measurements through the gRPC adapter, against a scripted server."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import SimulationRefusedError
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

MOTOR = contract.PwmView(
    pwm_id=1,
    name="MOTOR",
    timer="TIM1",
    alignment=contract.PWM_ALIGNMENT_CENTER,
    polarity=contract.PWM_POLARITY_ACTIVE_LOW,
    enabled=True,
    period_ns=50_000,
    compare=675,
    reload=1800,
    duty=0.375,
    frequency_hz=20_000.0,
    text="20.0 kHz · 37.5 % · center",
    state_text="on",
)


class PwmServicer(service.InspectorServicer):  # type: ignore[misc]
    """Lists MOTOR, measures what it is asked to, and refuses an output it does not have."""

    def __init__(self) -> None:
        self.asked: list[Any] = []

    def Describe(self, request: Any, context: Any) -> contract.Description:
        return contract.Description(
            capabilities=[contract.CAPABILITY_PWM, contract.CAPABILITY_PIN_MEASURE, 999]
        )

    def ObservePwms(self, request: Any, context: Any) -> contract.PwmList:
        return contract.PwmList(pwms=[MOTOR])

    def MeasurePwm(self, request: Any, context: Any) -> contract.PwmMeasurement:
        self.asked.append(request)
        if request.pwm_id != 1:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "there is no PWM output 9")
        return contract.PwmMeasurement(
            pwm_id=1,
            from_us=request.from_us,
            to_us=request.to_us,
            measured=True,
            duty_min=0.375,
            duty_max=0.5,
            duty_text="41.7 % (37.5 % – 50.0 %)",
            on_us=30_000,
        )

    def MeasurePin(self, request: Any, context: Any) -> contract.PinMeasurement:
        self.asked.append(request)
        return contract.PinMeasurement(
            pin_id=request.pin_id, measured=True, pulses=2, high_width_min_us=1500, periods=1
        )

    def ReadEvents(self, request: Any, context: Any) -> contract.EventBatch:
        change = contract.PwmChange(pwm_id=1, enabled=True, duty=0.5, period_ns=50_000)
        return contract.EventBatch(events=[contract.Event(sim_us=20_000, pwm=change)])


@pytest.fixture
def servicer() -> PwmServicer:
    return PwmServicer()


@pytest.fixture
def inspector(servicer: PwmServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_the_capabilities_are_named_without_their_prefix_and_unknown_ones_are_left_out(
    inspector: GrpcInspector,
) -> None:
    assert inspector.describe().capabilities == ("pwm", "pin_measure")


def test_an_output_comes_with_its_state_and_the_server_s_texts(inspector: GrpcInspector) -> None:
    (motor,) = inspector.read_pwms().outputs

    assert (motor.name, motor.enabled, motor.duty, motor.frequency_hz) == (
        "MOTOR",
        True,
        0.375,
        20_000.0,
    )
    assert (motor.alignment, motor.polarity, motor.text) == (
        "center",
        "active low",
        "20.0 kHz · 37.5 % · center",
    )


def test_a_pwm_is_measured_over_the_stretch_asked_for(
    inspector: GrpcInspector, servicer: PwmServicer
) -> None:
    measured = inspector.measure_pwm(1, 10_000, 40_000)

    assert (servicer.asked[0].from_us, servicer.asked[0].to_us) == (10_000, 40_000)
    assert (measured.duty_min, measured.duty_max, measured.on_us) == (0.375, 0.5, 30_000)
    assert measured.duty_text == "41.7 % (37.5 % – 50.0 %)"


def test_an_output_the_server_does_not_have_is_a_refusal_with_its_sentence(
    inspector: GrpcInspector,
) -> None:
    with pytest.raises(SimulationRefusedError, match="no PWM output 9"):
        inspector.measure_pwm(9, 0, 1000)


def test_a_pin_is_measured_by_its_number(inspector: GrpcInspector, servicer: PwmServicer) -> None:
    measured = inspector.measure_pin(1, 0, 40_000)

    assert servicer.asked[0].pin_id == 1
    assert (measured.pulses, measured.high_width_min_us, measured.periods) == (2, 1500, 1)


def test_a_change_of_a_pwm_on_the_stream_becomes_a_pwm_change(inspector: GrpcInspector) -> None:
    (change,) = inspector.read_events(epoch=1, from_event_seq=0).pwm_changes

    assert (change.pwm_id, change.sim_us, change.enabled, change.duty) == (1, 20_000, True, 0.5)
