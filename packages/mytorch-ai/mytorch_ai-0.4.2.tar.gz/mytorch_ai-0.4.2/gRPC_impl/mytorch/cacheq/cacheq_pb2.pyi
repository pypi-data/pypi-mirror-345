from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KeyValuePair(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ClientInfo(_message.Message):
    __slots__ = ("key_value_pairs",)
    KEY_VALUE_PAIRS_FIELD_NUMBER: _ClassVar[int]
    key_value_pairs: _containers.RepeatedCompositeFieldContainer[KeyValuePair]
    def __init__(self, key_value_pairs: _Optional[_Iterable[_Union[KeyValuePair, _Mapping]]] = ...) -> None: ...
