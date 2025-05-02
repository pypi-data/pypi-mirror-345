from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GrpcImageFolder(_message.Message):
    __slots__ = ("uuid", "image_uuids", "labels", "classes")
    UUID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_UUIDS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CLASSES_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    image_uuids: _containers.RepeatedScalarFieldContainer[str]
    labels: _containers.RepeatedScalarFieldContainer[int]
    classes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uuid: _Optional[str] = ..., image_uuids: _Optional[_Iterable[str]] = ..., labels: _Optional[_Iterable[int]] = ..., classes: _Optional[_Iterable[str]] = ...) -> None: ...

class GrpcCIFAR10(_message.Message):
    __slots__ = ("uuid", "dataset_length", "classes")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DATASET_LENGTH_FIELD_NUMBER: _ClassVar[int]
    CLASSES_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    dataset_length: int
    classes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uuid: _Optional[str] = ..., dataset_length: _Optional[int] = ..., classes: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateImageFolderRequest(_message.Message):
    __slots__ = ("relative_datapath", "transform_uuid")
    RELATIVE_DATAPATH_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_UUID_FIELD_NUMBER: _ClassVar[int]
    relative_datapath: str
    transform_uuid: str
    def __init__(self, relative_datapath: _Optional[str] = ..., transform_uuid: _Optional[str] = ...) -> None: ...

class CreateCIFAR10Request(_message.Message):
    __slots__ = ("root", "train", "download", "transform_uuid")
    ROOT_FIELD_NUMBER: _ClassVar[int]
    TRAIN_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_UUID_FIELD_NUMBER: _ClassVar[int]
    root: str
    train: bool
    download: bool
    transform_uuid: str
    def __init__(self, root: _Optional[str] = ..., train: bool = ..., download: bool = ..., transform_uuid: _Optional[str] = ...) -> None: ...
