from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BookInfo(_message.Message):
    __slots__ = ("book_id", "title", "author")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    book_id: str
    title: str
    author: str
    def __init__(self, book_id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ("book_id",)
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: str
    def __init__(self, book_id: _Optional[str] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("book_id", "title", "author")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    book_id: str
    title: str
    author: str
    def __init__(self, book_id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
