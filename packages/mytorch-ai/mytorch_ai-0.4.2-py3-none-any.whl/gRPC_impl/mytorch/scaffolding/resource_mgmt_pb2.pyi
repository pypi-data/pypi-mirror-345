from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceRequest(_message.Message):
    __slots__ = ("auth_token", "client_ip", "server_id", "max_time")
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CLIENT_IP_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_TIME_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    client_ip: str
    server_id: str
    max_time: int
    def __init__(self, auth_token: _Optional[str] = ..., client_ip: _Optional[str] = ..., server_id: _Optional[str] = ..., max_time: _Optional[int] = ...) -> None: ...

class ResourceRequestResponse(_message.Message):
    __slots__ = ("access_token", "additional_info", "resource_id", "resource_ip", "resource_port", "resource_name", "lease_time", "mytorch_version", "resource_info")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_INFO_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IP_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_PORT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    LEASE_TIME_FIELD_NUMBER: _ClassVar[int]
    MYTORCH_VERSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_INFO_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    additional_info: str
    resource_id: str
    resource_ip: str
    resource_port: int
    resource_name: str
    lease_time: int
    mytorch_version: str
    resource_info: str
    def __init__(self, access_token: _Optional[str] = ..., additional_info: _Optional[str] = ..., resource_id: _Optional[str] = ..., resource_ip: _Optional[str] = ..., resource_port: _Optional[int] = ..., resource_name: _Optional[str] = ..., lease_time: _Optional[int] = ..., mytorch_version: _Optional[str] = ..., resource_info: _Optional[str] = ...) -> None: ...
