# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from evolis.Mark import Mark
from evolis.Model import Model


class _CDevice(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 128),
        ("name", ctypes.c_char * 256),
        ("displayName", ctypes.c_char * 256),
        ("uri", ctypes.c_char * 512),
        ("mark", ctypes.c_int),
        ("model", ctypes.c_int),
        ("isSupervised", ctypes.c_bool),
        ("isOnline", ctypes.c_bool),
        ("link", ctypes.c_int),
        ("driverVersion", ctypes.c_char * 128),
    ]


class Device:
    def __init__(self, device: _CDevice) -> None:
        self.id = str(device.id, "ascii")
        self.name = str(device.name, "ascii")
        self.displayName = str(device.displayName, "ascii")
        self.uri = str(device.uri, "ascii")
        self.mark = Mark.from_int(device.mark)
        self.model = Model.from_int(device.model)
        self.isSupervised = bool(device.isSupervised)
        self.isOnline = bool(device.isOnline)
        # self.link = device.link
        self.driverVersion = str(device.driverVersion, "ascii")
