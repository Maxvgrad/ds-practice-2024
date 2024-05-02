from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BookInfo(_message.Message):
    __slots__ = ("title", "stock", "version")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    title: str
    stock: int
    version: int
    def __init__(self, title: _Optional[str] = ..., stock: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("title", "stock", "version")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    title: str
    stock: int
    version: int
    def __init__(self, title: _Optional[str] = ..., stock: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
