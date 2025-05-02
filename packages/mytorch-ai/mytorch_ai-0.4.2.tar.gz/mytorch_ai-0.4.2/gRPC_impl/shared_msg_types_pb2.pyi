from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SerializedTensorObject(_message.Message):
    __slots__ = ("serialized_tensor",)
    SERIALIZED_TENSOR_FIELD_NUMBER: _ClassVar[int]
    serialized_tensor: bytes
    def __init__(self, serialized_tensor: _Optional[bytes] = ...) -> None: ...

class SerializedNumpyArray(_message.Message):
    __slots__ = ("data", "shape", "dtype")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    shape: _containers.RepeatedScalarFieldContainer[int]
    dtype: str
    def __init__(self, data: _Optional[bytes] = ..., shape: _Optional[_Iterable[int]] = ..., dtype: _Optional[str] = ...) -> None: ...

class SerializedTensorData(_message.Message):
    __slots__ = ("data", "shape", "dtype")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    shape: _containers.RepeatedScalarFieldContainer[int]
    dtype: str
    def __init__(self, data: _Optional[bytes] = ..., shape: _Optional[_Iterable[int]] = ..., dtype: _Optional[str] = ...) -> None: ...

class IntegerValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class FloatValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class StringValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class StringPair(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ReshapeRequest(_message.Message):
    __slots__ = ("tensor_uuid", "shape")
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    shape: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, tensor_uuid: _Optional[str] = ..., shape: _Optional[_Iterable[int]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BooleanValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class StringDictionary(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.ScalarMap[str, str]
    def __init__(self, items: _Optional[_Mapping[str, str]] = ...) -> None: ...

class keyValuePair(_message.Message):
    __slots__ = ("key", "string_value", "int_value", "float_value", "bool_value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    string_value: str
    int_value: int
    float_value: float
    bool_value: bool
    def __init__(self, key: _Optional[str] = ..., string_value: _Optional[str] = ..., int_value: _Optional[int] = ..., float_value: _Optional[float] = ..., bool_value: bool = ...) -> None: ...

class UUID(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class Dtype(_message.Message):
    __slots__ = ("dtype",)
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    dtype: str
    def __init__(self, dtype: _Optional[str] = ...) -> None: ...

class TensorIDAndDim(_message.Message):
    __slots__ = ("tensor_uuid", "dim")
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    DIM_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    dim: int
    def __init__(self, tensor_uuid: _Optional[str] = ..., dim: _Optional[int] = ...) -> None: ...

class TensorIDsAndDim(_message.Message):
    __slots__ = ("tensor_uuids", "dim")
    TENSOR_UUIDS_FIELD_NUMBER: _ClassVar[int]
    DIM_FIELD_NUMBER: _ClassVar[int]
    tensor_uuids: _containers.RepeatedScalarFieldContainer[str]
    dim: int
    def __init__(self, tensor_uuids: _Optional[_Iterable[str]] = ..., dim: _Optional[int] = ...) -> None: ...

class TwoTensorIDs(_message.Message):
    __slots__ = ("tensor1_uuid", "tensor2_uuid")
    TENSOR1_UUID_FIELD_NUMBER: _ClassVar[int]
    TENSOR2_UUID_FIELD_NUMBER: _ClassVar[int]
    tensor1_uuid: str
    tensor2_uuid: str
    def __init__(self, tensor1_uuid: _Optional[str] = ..., tensor2_uuid: _Optional[str] = ...) -> None: ...

class TensorShape(_message.Message):
    __slots__ = ("shape",)
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    shape: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, shape: _Optional[_Iterable[int]] = ...) -> None: ...

class GrpcTensor(_message.Message):
    __slots__ = ("uuid", "shape", "dtype")
    UUID_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    shape: _containers.RepeatedScalarFieldContainer[int]
    dtype: str
    def __init__(self, uuid: _Optional[str] = ..., shape: _Optional[_Iterable[int]] = ..., dtype: _Optional[str] = ...) -> None: ...

class NamedTensor(_message.Message):
    __slots__ = ("name", "tensor")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TENSOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    tensor: GrpcTensor
    def __init__(self, name: _Optional[str] = ..., tensor: _Optional[_Union[GrpcTensor, _Mapping]] = ...) -> None: ...

class TwoGrpcTensors(_message.Message):
    __slots__ = ("tensor1", "tensor2")
    TENSOR1_FIELD_NUMBER: _ClassVar[int]
    TENSOR2_FIELD_NUMBER: _ClassVar[int]
    tensor1: GrpcTensor
    tensor2: GrpcTensor
    def __init__(self, tensor1: _Optional[_Union[GrpcTensor, _Mapping]] = ..., tensor2: _Optional[_Union[GrpcTensor, _Mapping]] = ...) -> None: ...

class MultipleGrpcTensors(_message.Message):
    __slots__ = ("tensors",)
    TENSORS_FIELD_NUMBER: _ClassVar[int]
    tensors: _containers.RepeatedCompositeFieldContainer[GrpcTensor]
    def __init__(self, tensors: _Optional[_Iterable[_Union[GrpcTensor, _Mapping]]] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("string_value", "int_value", "float_value", "bool_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    int_value: int
    float_value: float
    bool_value: bool
    def __init__(self, string_value: _Optional[str] = ..., int_value: _Optional[int] = ..., float_value: _Optional[float] = ..., bool_value: bool = ...) -> None: ...

class FileChunk(_message.Message):
    __slots__ = ("filename", "chunk_data", "chunk_index", "is_last_chunk")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_CHUNK_FIELD_NUMBER: _ClassVar[int]
    filename: str
    chunk_data: bytes
    chunk_index: int
    is_last_chunk: bool
    def __init__(self, filename: _Optional[str] = ..., chunk_data: _Optional[bytes] = ..., chunk_index: _Optional[int] = ..., is_last_chunk: bool = ...) -> None: ...

class JsonRequest(_message.Message):
    __slots__ = ("json_payload",)
    JSON_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    json_payload: str
    def __init__(self, json_payload: _Optional[str] = ...) -> None: ...

class JsonResponse(_message.Message):
    __slots__ = ("json_payload",)
    JSON_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    json_payload: str
    def __init__(self, json_payload: _Optional[str] = ...) -> None: ...
