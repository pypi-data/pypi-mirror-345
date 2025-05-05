# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from evolis.LaminatorMode import LaminatorMode


class _CLaminatorInfo(ctypes.Structure):
    _fields_ = [
        ("fwVersion", ctypes.c_char * 16),
        ("serialNumber", ctypes.c_char * 16),
        ("cpuSerialNumber", ctypes.c_char * 16),
        ("zone", ctypes.c_char * 16),
        ("isStandAlone", ctypes.c_bool),
        ("nbLaminatedSides", ctypes.c_int),
        ("nbInsertedCards", ctypes.c_int),
        ("mode", ctypes.c_int),
        ("isFirstPatchFront", ctypes.c_bool),
        ("defaultFrontSpeed", ctypes.c_int),
        ("defaultBackSpeed", ctypes.c_int),
        ("defaultTemperature", ctypes.c_int),
        ("frontSpeedCfg", ctypes.c_int),
        ("backSpeedCfg", ctypes.c_int),
        ("frontTemperatureCfg", ctypes.c_int),
        ("backTemperatureCfg", ctypes.c_int),
    ]


class LaminatorInfo:
    def __init__(self, c_laminator_info: _CLaminatorInfo):
        self.fwVersion = str(c_laminator_info.fwVersion, "ascii")
        self.serialNumber = str(c_laminator_info.serialNumber, "ascii")
        self.cpuSerialNumber = str(c_laminator_info.cpuSerialNumber, "ascii")
        self.zone = str(c_laminator_info.zone, "ascii")
        self.isStandAlone = bool(c_laminator_info.isStandAlone)
        self.nbLaminatedSides = int(c_laminator_info.nbLaminatedSides)
        self.nbInsertedCards = int(c_laminator_info.nbInsertedCards)
        self.mode = LaminatorMode.from_int(c_laminator_info.mode)
        self.isFirstPatchFront = bool(c_laminator_info.isFirstPatchFront)
        self.defaultFrontSpeed = int(c_laminator_info.defaultFrontSpeed)
        self.defaultBackSpeed = int(c_laminator_info.defaultBackSpeed)
        self.defaultTemperature = int(c_laminator_info.defaultTemperature)
        self.frontSpeedCfg = int(c_laminator_info.frontSpeedCfg)
        self.backSpeedCfg = int(c_laminator_info.backSpeedCfg)
        self.frontTemperatureCfg = int(c_laminator_info.frontTemperatureCfg)
        self.backTemperatureCfg = int(c_laminator_info.backTemperatureCfg)
