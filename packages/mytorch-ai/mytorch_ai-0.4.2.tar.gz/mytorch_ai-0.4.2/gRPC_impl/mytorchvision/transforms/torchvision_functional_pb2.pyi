from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ResizeRequest(_message.Message):
    __slots__ = ("tensor_uuid", "size")
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    size: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, tensor_uuid: _Optional[str] = ..., size: _Optional[_Iterable[int]] = ...) -> None: ...
