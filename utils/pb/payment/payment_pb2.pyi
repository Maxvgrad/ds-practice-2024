from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutePaymentResponse(_message.Message):
    __slots__ = ("payment_id",)
    PAYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    payment_id: int
    def __init__(self, payment_id: _Optional[int] = ...) -> None: ...

class ExecutePaymentRequest(_message.Message):
    __slots__ = ("payment_details",)
    PAYMENT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    payment_details: PaymentDetails
    def __init__(self, payment_details: _Optional[_Union[PaymentDetails, _Mapping]] = ...) -> None: ...

class PaymentDetails(_message.Message):
    __slots__ = ("number", "expiration_date", "cvv")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    CVV_FIELD_NUMBER: _ClassVar[int]
    number: str
    expiration_date: str
    cvv: str
    def __init__(self, number: _Optional[str] = ..., expiration_date: _Optional[str] = ..., cvv: _Optional[str] = ...) -> None: ...
