from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class fromPretrained_request(_message.Message):
    __slots__ = ("pretrained_model_name_or_path", "model_args", "kwargs")
    class KwargsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _shared_msg_types_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_shared_msg_types_pb2.Value, _Mapping]] = ...) -> None: ...
    PRETRAINED_MODEL_NAME_OR_PATH_FIELD_NUMBER: _ClassVar[int]
    MODEL_ARGS_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    pretrained_model_name_or_path: str
    model_args: _containers.RepeatedScalarFieldContainer[str]
    kwargs: _containers.MessageMap[str, _shared_msg_types_pb2.Value]
    def __init__(self, pretrained_model_name_or_path: _Optional[str] = ..., model_args: _Optional[_Iterable[str]] = ..., kwargs: _Optional[_Mapping[str, _shared_msg_types_pb2.Value]] = ...) -> None: ...

class fromPretrained_response(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...

class generate_request(_message.Message):
    __slots__ = ("model_uuid", "kwargs")
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    kwargs: _containers.RepeatedCompositeFieldContainer[_shared_msg_types_pb2.keyValuePair]
    def __init__(self, model_uuid: _Optional[str] = ..., kwargs: _Optional[_Iterable[_Union[_shared_msg_types_pb2.keyValuePair, _Mapping]]] = ...) -> None: ...

class generate_response(_message.Message):
    __slots__ = ("tensor_uuid",)
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    tensor_uuid: str
    def __init__(self, tensor_uuid: _Optional[str] = ...) -> None: ...
