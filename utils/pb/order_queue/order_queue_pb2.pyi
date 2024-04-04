from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DequeueOrderResponse(_message.Message):
    __slots__ = ("order_id", "order_type", "payload")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    order_type: str
    payload: str
    def __init__(self, order_id: _Optional[int] = ..., order_type: _Optional[str] = ..., payload: _Optional[str] = ...) -> None: ...

class DequeueOrderRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EnqueueOrderResponse(_message.Message):
    __slots__ = ("order_id", "is_success")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    is_success: bool
    def __init__(self, order_id: _Optional[int] = ..., is_success: bool = ...) -> None: ...

class EnqueueOrderRequest(_message.Message):
    __slots__ = ("priority", "order_id", "order_type", "payload")
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    priority: int
    order_id: int
    order_type: str
    payload: str
    def __init__(self, priority: _Optional[int] = ..., order_id: _Optional[int] = ..., order_type: _Optional[str] = ..., payload: _Optional[str] = ...) -> None: ...
