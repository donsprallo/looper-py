"""The contract's interrupt events and the recording request, as the library reads and asks them."""

from __future__ import annotations

from looper.domain.model.event_recording import EventRecording
from looper.infrastructure import interrupt_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def test_an_isr_in_summary_is_its_entry_and_its_leaving() -> None:
    ran = contract.InterruptEvent(
        source_id=2, kind=contract.INTERRUPT_EVENT_RAN, latency_us=4, duration_us=10
    )
    pending = contract.InterruptEvent(source_id=1, kind=contract.INTERRUPT_EVENT_PENDING)
    page = contract.EventBatch(
        events=[
            contract.Event(sim_us=100, interrupt=ran),
            contract.Event(sim_us=120, interrupt=pending),
        ]
    )

    marks = interrupt_translation.marks_of(page)

    assert [(mark.kind, mark.sim_us, mark.source_id) for mark in marks] == [
        ("entered", 90, 2),
        ("left", 100, 2),
        ("pending", 120, 1),
    ]
    assert marks[0].latency_us == 4


def test_the_recording_is_asked_by_name_with_the_contract_s_modes() -> None:
    recording = EventRecording(
        interrupts={"*": "summary"}, dma={"SPI1_RX": "detailed"}, interrupt_ring=8, at_least=True
    )

    request = interrupt_translation.recording_request(recording)

    assert [(one.name, one.mode) for one in request.sources] == [
        ("*", contract.EVENT_RECORDING_SUMMARY)
    ]
    assert [(one.name, one.mode) for one in request.channels] == [
        ("SPI1_RX", contract.EVENT_RECORDING_DETAILED)
    ]
    assert (request.interrupt_ring, request.dma_ring, request.at_least) == (8, 0, True)
