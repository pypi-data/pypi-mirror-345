from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class encodePlus_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "text", "kwargs")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    text: str
    kwargs: _containers.RepeatedCompositeFieldContainer[_shared_msg_types_pb2.keyValuePair]
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., text: _Optional[str] = ..., kwargs: _Optional[_Iterable[_Union[_shared_msg_types_pb2.keyValuePair, _Mapping]]] = ...) -> None: ...

class tokenizer_key_uuid_pair(_message.Message):
    __slots__ = ("key", "tensor_uuid")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    key: str
    tensor_uuid: str
    def __init__(self, key: _Optional[str] = ..., tensor_uuid: _Optional[str] = ...) -> None: ...

class encodePlus_response(_message.Message):
    __slots__ = ("encoding_uuid", "data")
    ENCODING_UUID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    encoding_uuid: str
    data: _containers.RepeatedCompositeFieldContainer[tokenizer_key_uuid_pair]
    def __init__(self, encoding_uuid: _Optional[str] = ..., data: _Optional[_Iterable[_Union[tokenizer_key_uuid_pair, _Mapping]]] = ...) -> None: ...

class setPadToken_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "pad_token")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    PAD_TOKEN_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    pad_token: str
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., pad_token: _Optional[str] = ...) -> None: ...

class setPadToken_response(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class decode_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "input_tensor_uuid", "kwargs")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    INPUT_TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    input_tensor_uuid: str
    kwargs: _containers.RepeatedCompositeFieldContainer[_shared_msg_types_pb2.keyValuePair]
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., input_tensor_uuid: _Optional[str] = ..., kwargs: _Optional[_Iterable[_Union[_shared_msg_types_pb2.keyValuePair, _Mapping]]] = ...) -> None: ...

class decode_response(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class tokenizerFromPretrained_request(_message.Message):
    __slots__ = ("pretrained_model_name_or_path", "inputs", "kwargs")
    class KwargsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PRETRAINED_MODEL_NAME_OR_PATH_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    pretrained_model_name_or_path: str
    inputs: _containers.RepeatedScalarFieldContainer[str]
    kwargs: _containers.ScalarMap[str, str]
    def __init__(self, pretrained_model_name_or_path: _Optional[str] = ..., inputs: _Optional[_Iterable[str]] = ..., kwargs: _Optional[_Mapping[str, str]] = ...) -> None: ...

class tokenizerFromPretrained_response(_message.Message):
    __slots__ = ("tokenizer_uuid", "special_tokens")
    class SpecialTokensEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    special_tokens: _containers.ScalarMap[str, str]
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., special_tokens: _Optional[_Mapping[str, str]] = ...) -> None: ...
