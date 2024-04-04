from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PassTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PassTokenResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStateTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStateTokenResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: str
    def __init__(self, state: _Optional[str] = ...) -> None: ...
