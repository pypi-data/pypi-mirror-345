from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class EndDeviceFunctionKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[EndDeviceFunctionKind]
    autonomousDst: _ClassVar[EndDeviceFunctionKind]
    demandResponse: _ClassVar[EndDeviceFunctionKind]
    electricMetering: _ClassVar[EndDeviceFunctionKind]
    metrology: _ClassVar[EndDeviceFunctionKind]
    onRequestRead: _ClassVar[EndDeviceFunctionKind]
    outageHistory: _ClassVar[EndDeviceFunctionKind]
    relaysProgramming: _ClassVar[EndDeviceFunctionKind]
    reverseFlow: _ClassVar[EndDeviceFunctionKind]
UNKNOWN: EndDeviceFunctionKind
autonomousDst: EndDeviceFunctionKind
demandResponse: EndDeviceFunctionKind
electricMetering: EndDeviceFunctionKind
metrology: EndDeviceFunctionKind
onRequestRead: EndDeviceFunctionKind
outageHistory: EndDeviceFunctionKind
relaysProgramming: EndDeviceFunctionKind
reverseFlow: EndDeviceFunctionKind
