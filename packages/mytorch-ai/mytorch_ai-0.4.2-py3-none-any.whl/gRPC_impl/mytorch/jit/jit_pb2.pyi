from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ModelIDandTensorID(_message.Message):
    __slots__ = ("model_uuid", "tensor_uuid")
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    tensor_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ..., tensor_uuid: _Optional[str] = ...) -> None: ...

class SaveRequest(_message.Message):
    __slots__ = ("model_uuid", "path")
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    path: str
    def __init__(self, model_uuid: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...
