from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerStatus(_message.Message):
    __slots__ = ("server_name", "server_ip", "server_port", "server_status")
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_IP_FIELD_NUMBER: _ClassVar[int]
    SERVER_PORT_FIELD_NUMBER: _ClassVar[int]
    SERVER_STATUS_FIELD_NUMBER: _ClassVar[int]
    server_name: str
    server_ip: str
    server_port: int
    server_status: str
    def __init__(self, server_name: _Optional[str] = ..., server_ip: _Optional[str] = ..., server_port: _Optional[int] = ..., server_status: _Optional[str] = ...) -> None: ...

class GpuInfoList(_message.Message):
    __slots__ = ("gpu_dicts",)
    GPU_DICTS_FIELD_NUMBER: _ClassVar[int]
    gpu_dicts: _containers.RepeatedCompositeFieldContainer[_shared_msg_types_pb2.StringDictionary]
    def __init__(self, gpu_dicts: _Optional[_Iterable[_Union[_shared_msg_types_pb2.StringDictionary, _Mapping]]] = ...) -> None: ...
