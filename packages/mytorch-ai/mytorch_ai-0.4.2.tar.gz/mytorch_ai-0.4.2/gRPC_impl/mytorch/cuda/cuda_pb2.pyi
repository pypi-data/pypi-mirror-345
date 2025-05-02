from gRPC_impl import shared_msg_types_pb2 as _shared_msg_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class is_available_request(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class is_available_response(_message.Message):
    __slots__ = ("is_available",)
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    is_available: bool
    def __init__(self, is_available: bool = ...) -> None: ...

class empty_cache_request(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class empty_cache_response(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class memory_allocated_request(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class memory_allocated_response(_message.Message):
    __slots__ = ("memory_allocated",)
    MEMORY_ALLOCATED_FIELD_NUMBER: _ClassVar[int]
    memory_allocated: int
    def __init__(self, memory_allocated: _Optional[int] = ...) -> None: ...

class memory_reserved_request(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class memory_reserved_response(_message.Message):
    __slots__ = ("memory_reserved",)
    MEMORY_RESERVED_FIELD_NUMBER: _ClassVar[int]
    memory_reserved: int
    def __init__(self, memory_reserved: _Optional[int] = ...) -> None: ...

class get_device_properties_request(_message.Message):
    __slots__ = ("device_str", "device_int")
    DEVICE_STR_FIELD_NUMBER: _ClassVar[int]
    DEVICE_INT_FIELD_NUMBER: _ClassVar[int]
    device_str: str
    device_int: int
    def __init__(self, device_str: _Optional[str] = ..., device_int: _Optional[int] = ...) -> None: ...

class get_device_properties_response(_message.Message):
    __slots__ = ("name", "total_memory", "available_memory", "allocated_memory", "reserved_memory", "max_memory_allocated", "max_memory_reserved", "multi_processor_count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MEMORY_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_MEMORY_FIELD_NUMBER: _ClassVar[int]
    ALLOCATED_MEMORY_FIELD_NUMBER: _ClassVar[int]
    RESERVED_MEMORY_FIELD_NUMBER: _ClassVar[int]
    MAX_MEMORY_ALLOCATED_FIELD_NUMBER: _ClassVar[int]
    MAX_MEMORY_RESERVED_FIELD_NUMBER: _ClassVar[int]
    MULTI_PROCESSOR_COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    total_memory: int
    available_memory: int
    allocated_memory: int
    reserved_memory: int
    max_memory_allocated: int
    max_memory_reserved: int
    multi_processor_count: int
    def __init__(self, name: _Optional[str] = ..., total_memory: _Optional[int] = ..., available_memory: _Optional[int] = ..., allocated_memory: _Optional[int] = ..., reserved_memory: _Optional[int] = ..., max_memory_allocated: _Optional[int] = ..., max_memory_reserved: _Optional[int] = ..., multi_processor_count: _Optional[int] = ...) -> None: ...
