from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OptimizerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SGD: _ClassVar[OptimizerType]
    ADAM: _ClassVar[OptimizerType]
    ADAGRAD: _ClassVar[OptimizerType]
    RMSPROP: _ClassVar[OptimizerType]
    ADAMAX: _ClassVar[OptimizerType]
    ADAMW: _ClassVar[OptimizerType]
    ADAMAXW: _ClassVar[OptimizerType]
    ADAGRADW: _ClassVar[OptimizerType]
    RMSPROPW: _ClassVar[OptimizerType]
SGD: OptimizerType
ADAM: OptimizerType
ADAGRAD: OptimizerType
RMSPROP: OptimizerType
ADAMAX: OptimizerType
ADAMW: OptimizerType
ADAMAXW: OptimizerType
ADAGRADW: OptimizerType
RMSPROPW: OptimizerType

class CreateSGDOptimizerRequest(_message.Message):
    __slots__ = ("generator_uuid", "learning_rate", "momentum")
    GENERATOR_UUID_FIELD_NUMBER: _ClassVar[int]
    LEARNING_RATE_FIELD_NUMBER: _ClassVar[int]
    MOMENTUM_FIELD_NUMBER: _ClassVar[int]
    generator_uuid: str
    learning_rate: float
    momentum: float
    def __init__(self, generator_uuid: _Optional[str] = ..., learning_rate: _Optional[float] = ..., momentum: _Optional[float] = ...) -> None: ...
