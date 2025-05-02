from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ModelLoadRequest(_message.Message):
    __slots__ = ("repo", "model_name", "weights_enum")
    REPO_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_ENUM_FIELD_NUMBER: _ClassVar[int]
    repo: str
    model_name: str
    weights_enum: str
    def __init__(self, repo: _Optional[str] = ..., model_name: _Optional[str] = ..., weights_enum: _Optional[str] = ...) -> None: ...

class ModelLoadResponse(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...
