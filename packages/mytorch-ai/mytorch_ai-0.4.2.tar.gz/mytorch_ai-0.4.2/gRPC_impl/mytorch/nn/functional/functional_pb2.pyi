from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SoftmaxRequest(_message.Message):
    __slots__ = ("tensor_uuid", "dim")
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    DIM_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    dim: int
    def __init__(self, tensor_uuid: _Optional[str] = ..., dim: _Optional[int] = ...) -> None: ...
