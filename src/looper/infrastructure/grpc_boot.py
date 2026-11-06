"""The bootloader's calls over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.boot_port import BootInspector
from looper.domain.model import Image, PartitionHeader
from looper.infrastructure import boot_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

EMPTY = contract.Empty()


class GrpcBootCalls(BootInspector):
    """Images, partition headers and writing an image, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    @staticmethod
    def _taken(ack: contract.Ack) -> None:
        raise NotImplementedError

    def read_images(self) -> tuple[Image, ...]:
        """Every image of the project in every variant."""
        return boot_translation.images_of(self._call(self._stub.ObserveImages, EMPTY))

    def read_headers(self) -> dict[str, PartitionHeader]:
        """What each partition holds, by name."""
        view = self._call(self._stub.ObserveFlash, contract.FlashRequest())
        return boot_translation.headers_of(view)

    def write_image(self, partition: str, image: str) -> None:
        """Erase a partition and write a built image into it."""
        target = contract.PartitionOffset(name=partition)
        request = contract.FlashWrite(partition=target, image=image)
        self._taken(self._call(self._stub.WriteFlash, request))

    def write_image_file(self, partition: str, path: str) -> None:
        """Erase a partition and write an image file into it."""
        target = contract.PartitionOffset(name=partition)
        request = contract.FlashWrite(partition=target, image_file=path)
        self._taken(self._call(self._stub.WriteFlash, request))
