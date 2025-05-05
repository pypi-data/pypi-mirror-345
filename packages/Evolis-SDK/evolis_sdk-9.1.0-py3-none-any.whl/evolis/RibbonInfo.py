# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from evolis.RibbonType import RibbonType


class _CRibbonInfo(ctypes.Structure):
    _fields_ = [
        ("description", ctypes.c_char * 64),
        ("zone", ctypes.c_char * 8),
        ("type", ctypes.c_int),
        ("capacity", ctypes.c_int),
        ("remaining", ctypes.c_int),
        ("progress", ctypes.c_int),
        ("productCode", ctypes.c_char * 16),
        ("batchNumber", ctypes.c_uint32),
        ("buildAt", ctypes.c_char * 24),
        ("serialNumber", ctypes.c_char * 24),
        ("internalCode", ctypes.c_char * 24),
    ]


class RibbonInfo:
    def __init__(self, c_ribbon_info: _CRibbonInfo):
        self.description = str(c_ribbon_info.description, "ascii")
        self.zone = str(c_ribbon_info.zone, "ascii")
        self.type = RibbonType.from_int(c_ribbon_info.type)
        self.capacity = int(c_ribbon_info.capacity)
        self.remaining = int(c_ribbon_info.remaining)
        self.progress = int(c_ribbon_info.progress)
        self.productCode = str(c_ribbon_info.productCode, "ascii")
        self.batchNumber = int(c_ribbon_info.batchNumber)
        self.buildAt = str(c_ribbon_info.buildAt, "ascii")
        self.serialNumber = str(c_ribbon_info.serialNumber, "ascii")
        self.internalCode = str(c_ribbon_info.internalCode, "ascii")
