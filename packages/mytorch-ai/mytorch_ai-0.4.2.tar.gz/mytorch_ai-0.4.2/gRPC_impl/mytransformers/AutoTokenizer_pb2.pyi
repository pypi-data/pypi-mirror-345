from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class tokenizer_from_pretrained_request(_message.Message):
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

class tokenizer_from_pretrained_response(_message.Message):
    __slots__ = ("tokenizer_uuid", "eos_token")
    TOKENIZER_UUID_FIELD_NUMBER: _ClassVar[int]
    EOS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    tokenizer_uuid: str
    eos_token: str
    def __init__(self, tokenizer_uuid: _Optional[str] = ..., eos_token: _Optional[str] = ...) -> None: ...
