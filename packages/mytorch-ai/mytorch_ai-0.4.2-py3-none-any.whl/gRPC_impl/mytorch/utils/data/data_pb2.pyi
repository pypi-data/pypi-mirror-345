from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcSubset(_message.Message):
    __slots__ = ("uuid", "dataset_length")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DATASET_LENGTH_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    dataset_length: int
    def __init__(self, uuid: _Optional[str] = ..., dataset_length: _Optional[int] = ...) -> None: ...

class GrpcDataLoader(_message.Message):
    __slots__ = ("uuid", "dataset_length", "batch_size")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DATASET_LENGTH_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    dataset_length: int
    batch_size: int
    def __init__(self, uuid: _Optional[str] = ..., dataset_length: _Optional[int] = ..., batch_size: _Optional[int] = ...) -> None: ...

class DataLoaderBatchResponse(_message.Message):
    __slots__ = ("inputs_tensor", "targets_tensor", "is_last_batch", "out_of_bounds")
    INPUTS_TENSOR_FIELD_NUMBER: _ClassVar[int]
    TARGETS_TENSOR_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_BATCH_FIELD_NUMBER: _ClassVar[int]
    OUT_OF_BOUNDS_FIELD_NUMBER: _ClassVar[int]
    inputs_tensor: _shared_msg_types_pb2.GrpcTensor
    targets_tensor: _shared_msg_types_pb2.GrpcTensor
    is_last_batch: bool
    out_of_bounds: bool
    def __init__(self, inputs_tensor: _Optional[_Union[_shared_msg_types_pb2.GrpcTensor, _Mapping]] = ..., targets_tensor: _Optional[_Union[_shared_msg_types_pb2.GrpcTensor, _Mapping]] = ..., is_last_batch: bool = ..., out_of_bounds: bool = ...) -> None: ...

class CreateSubsetRequest(_message.Message):
    __slots__ = ("dataset_uuid", "indices")
    DATASET_UUID_FIELD_NUMBER: _ClassVar[int]
    INDICES_FIELD_NUMBER: _ClassVar[int]
    dataset_uuid: str
    indices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dataset_uuid: _Optional[str] = ..., indices: _Optional[_Iterable[int]] = ...) -> None: ...

class CreateDataLoaderRequest(_message.Message):
    __slots__ = ("dataset_uuid", "batch_size", "shuffle")
    DATASET_UUID_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    SHUFFLE_FIELD_NUMBER: _ClassVar[int]
    dataset_uuid: str
    batch_size: int
    shuffle: bool
    def __init__(self, dataset_uuid: _Optional[str] = ..., batch_size: _Optional[int] = ..., shuffle: bool = ...) -> None: ...

class GetNextBatchRequest(_message.Message):
    __slots__ = ("dataloader_uuid", "batch_index")
    DATALOADER_UUID_FIELD_NUMBER: _ClassVar[int]
    BATCH_INDEX_FIELD_NUMBER: _ClassVar[int]
    dataloader_uuid: str
    batch_index: int
    def __init__(self, dataloader_uuid: _Optional[str] = ..., batch_index: _Optional[int] = ...) -> None: ...
