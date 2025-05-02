from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TensorStreamingRequest(_message.Message):
    __slots__ = ("method", "uuid", "two_tensors", "tensor_and_dim", "reshape_request", "slice_request")
    METHOD_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    TWO_TENSORS_FIELD_NUMBER: _ClassVar[int]
    TENSOR_AND_DIM_FIELD_NUMBER: _ClassVar[int]
    RESHAPE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SLICE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    method: str
    uuid: _shared_msg_types_pb2.UUID
    two_tensors: _shared_msg_types_pb2.TwoTensorIDs
    tensor_and_dim: _shared_msg_types_pb2.TensorIDAndDim
    reshape_request: _shared_msg_types_pb2.ReshapeRequest
    slice_request: SliceRequest
    def __init__(self, method: _Optional[str] = ..., uuid: _Optional[_Union[_shared_msg_types_pb2.UUID, _Mapping]] = ..., two_tensors: _Optional[_Union[_shared_msg_types_pb2.TwoTensorIDs, _Mapping]] = ..., tensor_and_dim: _Optional[_Union[_shared_msg_types_pb2.TensorIDAndDim, _Mapping]] = ..., reshape_request: _Optional[_Union[_shared_msg_types_pb2.ReshapeRequest, _Mapping]] = ..., slice_request: _Optional[_Union[SliceRequest, _Mapping]] = ...) -> None: ...

class TensorStreamingResponse(_message.Message):
    __slots__ = ("tensor", "float_value", "tensor_shape", "tensor_dtype")
    TENSOR_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    TENSOR_SHAPE_FIELD_NUMBER: _ClassVar[int]
    TENSOR_DTYPE_FIELD_NUMBER: _ClassVar[int]
    tensor: _shared_msg_types_pb2.GrpcTensor
    float_value: _shared_msg_types_pb2.FloatValue
    tensor_shape: _shared_msg_types_pb2.TensorShape
    tensor_dtype: _shared_msg_types_pb2.Dtype
    def __init__(self, tensor: _Optional[_Union[_shared_msg_types_pb2.GrpcTensor, _Mapping]] = ..., float_value: _Optional[_Union[_shared_msg_types_pb2.FloatValue, _Mapping]] = ..., tensor_shape: _Optional[_Union[_shared_msg_types_pb2.TensorShape, _Mapping]] = ..., tensor_dtype: _Optional[_Union[_shared_msg_types_pb2.Dtype, _Mapping]] = ...) -> None: ...

class TensorSlice(_message.Message):
    __slots__ = ("start", "stop", "step")
    START_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    start: int
    stop: int
    step: int
    def __init__(self, start: _Optional[int] = ..., stop: _Optional[int] = ..., step: _Optional[int] = ...) -> None: ...

class SliceRequest(_message.Message):
    __slots__ = ("tensor_uuid", "slices")
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    SLICES_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    slices: _containers.RepeatedCompositeFieldContainer[TensorSlice]
    def __init__(self, tensor_uuid: _Optional[str] = ..., slices: _Optional[_Iterable[_Union[TensorSlice, _Mapping]]] = ...) -> None: ...
