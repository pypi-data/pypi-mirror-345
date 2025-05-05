from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SVCControlMode(_message.Message):
    __slots__ = ()
    class Enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[SVCControlMode.Enum]
        reactivePower: _ClassVar[SVCControlMode.Enum]
        voltage: _ClassVar[SVCControlMode.Enum]
    UNKNOWN: SVCControlMode.Enum
    reactivePower: SVCControlMode.Enum
    voltage: SVCControlMode.Enum
    def __init__(self) -> None: ...
