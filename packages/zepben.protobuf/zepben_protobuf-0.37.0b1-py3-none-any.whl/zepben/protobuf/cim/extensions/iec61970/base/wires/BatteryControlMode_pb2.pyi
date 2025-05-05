from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class BatteryControlMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[BatteryControlMode]
    peakShaveDischarge: _ClassVar[BatteryControlMode]
    currentPeakShaveDischarge: _ClassVar[BatteryControlMode]
    following: _ClassVar[BatteryControlMode]
    support: _ClassVar[BatteryControlMode]
    schedule: _ClassVar[BatteryControlMode]
    peakShaveCharge: _ClassVar[BatteryControlMode]
    currentPeakShaveCharge: _ClassVar[BatteryControlMode]
    time: _ClassVar[BatteryControlMode]
    profile: _ClassVar[BatteryControlMode]
UNKNOWN: BatteryControlMode
peakShaveDischarge: BatteryControlMode
currentPeakShaveDischarge: BatteryControlMode
following: BatteryControlMode
support: BatteryControlMode
schedule: BatteryControlMode
peakShaveCharge: BatteryControlMode
currentPeakShaveCharge: BatteryControlMode
time: BatteryControlMode
profile: BatteryControlMode
