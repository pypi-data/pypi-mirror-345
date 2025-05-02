from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SerializedStateDict(_message.Message):
    __slots__ = ("entries",)
    class EntriesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _shared_msg_types_pb2.SerializedTensorData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_shared_msg_types_pb2.SerializedTensorData, _Mapping]] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.MessageMap[str, _shared_msg_types_pb2.SerializedTensorData]
    def __init__(self, entries: _Optional[_Mapping[str, _shared_msg_types_pb2.SerializedTensorData]] = ...) -> None: ...

class NNLayer(_message.Message):
    __slots__ = ("type", "params")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    type: str
    params: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[str] = ..., params: _Optional[_Iterable[str]] = ...) -> None: ...

class NNLayers(_message.Message):
    __slots__ = ("layers",)
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    layers: _containers.RepeatedCompositeFieldContainer[NNLayer]
    def __init__(self, layers: _Optional[_Iterable[_Union[NNLayer, _Mapping]]] = ...) -> None: ...

class ForwardPassRequest(_message.Message):
    __slots__ = ("module_uuid", "tensor_uuid")
    MODULE_UUID_FIELD_NUMBER: _ClassVar[int]
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    module_uuid: str
    tensor_uuid: str
    def __init__(self, module_uuid: _Optional[str] = ..., tensor_uuid: _Optional[str] = ...) -> None: ...
