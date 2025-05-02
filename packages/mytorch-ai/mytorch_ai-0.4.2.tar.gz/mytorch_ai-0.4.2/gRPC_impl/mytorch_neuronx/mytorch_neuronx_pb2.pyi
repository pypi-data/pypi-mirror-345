from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TraceRequest(_message.Message):
    __slots__ = ("model_uuid", "tensor_uuid_tuple")
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    TENSOR_UUID_TUPLE_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    tensor_uuid_tuple: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, model_uuid: _Optional[str] = ..., tensor_uuid_tuple: _Optional[_Iterable[str]] = ...) -> None: ...

class TraceResponse(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...
