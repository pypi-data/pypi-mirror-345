from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LossFunctionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MSE: _ClassVar[LossFunctionType]
    L1: _ClassVar[LossFunctionType]
    CrossEntropy: _ClassVar[LossFunctionType]
    NLL: _ClassVar[LossFunctionType]
    PoissonNLL: _ClassVar[LossFunctionType]
    KLDiv: _ClassVar[LossFunctionType]
    BCE: _ClassVar[LossFunctionType]
    MarginRanking: _ClassVar[LossFunctionType]
    Hinge: _ClassVar[LossFunctionType]
    MultiLabelMargin: _ClassVar[LossFunctionType]
    SmoothL1: _ClassVar[LossFunctionType]
    SoftMargin: _ClassVar[LossFunctionType]
    MultiLabelSoftMargin: _ClassVar[LossFunctionType]
    CosineEmbedding: _ClassVar[LossFunctionType]
    MultiMargin: _ClassVar[LossFunctionType]
    TripletMargin: _ClassVar[LossFunctionType]
MSE: LossFunctionType
L1: LossFunctionType
CrossEntropy: LossFunctionType
NLL: LossFunctionType
PoissonNLL: LossFunctionType
KLDiv: LossFunctionType
BCE: LossFunctionType
MarginRanking: LossFunctionType
Hinge: LossFunctionType
MultiLabelMargin: LossFunctionType
SmoothL1: LossFunctionType
SoftMargin: LossFunctionType
MultiLabelSoftMargin: LossFunctionType
CosineEmbedding: LossFunctionType
MultiMargin: LossFunctionType
TripletMargin: LossFunctionType

class LossFunctionRequest(_message.Message):
    __slots__ = ("loss_function_type",)
    LOSS_FUNCTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    loss_function_type: LossFunctionType
    def __init__(self, loss_function_type: _Optional[_Union[LossFunctionType, str]] = ...) -> None: ...

class RunLossFunctionRequest(_message.Message):
    __slots__ = ("loss_function_uuid", "input_uuid", "target_uuid")
    LOSS_FUNCTION_UUID_FIELD_NUMBER: _ClassVar[int]
    INPUT_UUID_FIELD_NUMBER: _ClassVar[int]
    TARGET_UUID_FIELD_NUMBER: _ClassVar[int]
    loss_function_uuid: str
    input_uuid: str
    target_uuid: str
    def __init__(self, loss_function_uuid: _Optional[str] = ..., input_uuid: _Optional[str] = ..., target_uuid: _Optional[str] = ...) -> None: ...
