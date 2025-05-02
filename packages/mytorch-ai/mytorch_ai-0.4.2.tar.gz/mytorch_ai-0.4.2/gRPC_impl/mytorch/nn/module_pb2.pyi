from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from gRPC_impl.mytorch.nn import nn_msg_types_pb2 as _nn_msg_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModuleToDeviceRequest(_message.Message):
    __slots__ = ("uuid", "device")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    device: str
    def __init__(self, uuid: _Optional[str] = ..., device: _Optional[str] = ...) -> None: ...

class Parameters(_message.Message):
    __slots__ = ("generator_uuid",)
    GENERATOR_UUID_FIELD_NUMBER: _ClassVar[int]
    generator_uuid: str
    def __init__(self, generator_uuid: _Optional[str] = ...) -> None: ...

class half_request(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class half_response(_message.Message):
    __slots__ = ("empty",)
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    empty: _shared_msg_types_pb2.Empty
    def __init__(self, empty: _Optional[_Union[_shared_msg_types_pb2.Empty, _Mapping]] = ...) -> None: ...
