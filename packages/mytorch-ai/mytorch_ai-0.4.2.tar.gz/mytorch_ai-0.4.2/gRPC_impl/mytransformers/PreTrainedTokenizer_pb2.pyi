from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class tokenizer_method_arg_pair(_message.Message):
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

class encode_plus_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "text", "kwargs")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    text: str
    kwargs: _containers.RepeatedCompositeFieldContainer[tokenizer_method_arg_pair]
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., text: _Optional[str] = ..., kwargs: _Optional[_Iterable[_Union[tokenizer_method_arg_pair, _Mapping]]] = ...) -> None: ...

class tokenizer_key_uuid_pair(_message.Message):
    __slots__ = ("key", "tensor_uuid")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    key: str
    tensor_uuid: str
    def __init__(self, key: _Optional[str] = ..., tensor_uuid: _Optional[str] = ...) -> None: ...

class encode_plus_response(_message.Message):
    __slots__ = ("encoding_uuid", "data")
    ENCODING_UUID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    encoding_uuid: str
    data: _containers.RepeatedCompositeFieldContainer[tokenizer_key_uuid_pair]
    def __init__(self, encoding_uuid: _Optional[str] = ..., data: _Optional[_Iterable[_Union[tokenizer_key_uuid_pair, _Mapping]]] = ...) -> None: ...

class set_pad_token_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "pad_token")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    PAD_TOKEN_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    pad_token: str
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., pad_token: _Optional[str] = ...) -> None: ...

class set_pad_token_response(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class decode_request(_message.Message):
    __slots__ = ("tokenizer_uuid", "input_tensor_uuid", "kwargs")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    INPUT_TENSOR_UUID_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    input_tensor_uuid: str
    kwargs: _containers.RepeatedCompositeFieldContainer[tokenizer_method_arg_pair]
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., input_tensor_uuid: _Optional[str] = ..., kwargs: _Optional[_Iterable[_Union[tokenizer_method_arg_pair, _Mapping]]] = ...) -> None: ...

class decode_response(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...
