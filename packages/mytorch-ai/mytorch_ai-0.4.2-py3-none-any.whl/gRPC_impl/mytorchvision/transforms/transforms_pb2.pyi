from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcTransform(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class CreateCenterCropTransformRequest(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    def __init__(self, size: _Optional[int] = ...) -> None: ...

class CreateResizeTransformRequest(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: int
    def __init__(self, size: _Optional[int] = ...) -> None: ...

class CreateNormalizeTransformRequest(_message.Message):
    __slots__ = ("mean", "std")
    MEAN_FIELD_NUMBER: _ClassVar[int]
    STD_FIELD_NUMBER: _ClassVar[int]
    mean: _containers.RepeatedScalarFieldContainer[float]
    std: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, mean: _Optional[_Iterable[float]] = ..., std: _Optional[_Iterable[float]] = ...) -> None: ...

class CreateComposeTransformRequest(_message.Message):
    __slots__ = ("component_transform_uuid",)
    COMPONENT_TRANSFORM_UUID_FIELD_NUMBER: _ClassVar[int]
    component_transform_uuid: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, component_transform_uuid: _Optional[_Iterable[str]] = ...) -> None: ...
