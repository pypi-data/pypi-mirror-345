from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateResidualBlockRequest(_message.Message):
    __slots__ = ("in_channels", "out_channels", "stride", "downample_model_uuid")
    IN_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    OUT_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    STRIDE_FIELD_NUMBER: _ClassVar[int]
    DOWNAMPLE_MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    in_channels: int
    out_channels: int
    stride: int
    downample_model_uuid: str
    def __init__(self, in_channels: _Optional[int] = ..., out_channels: _Optional[int] = ..., stride: _Optional[int] = ..., downample_model_uuid: _Optional[str] = ...) -> None: ...

class CreateResidualBlockResponse(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...

class CreateResNetModelRequest(_message.Message):
    __slots__ = ("num_classes", "layers")
    NUM_CLASSES_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    num_classes: int
    layers: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, num_classes: _Optional[int] = ..., layers: _Optional[_Iterable[int]] = ...) -> None: ...

class CreateResNetModelResponse(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...
