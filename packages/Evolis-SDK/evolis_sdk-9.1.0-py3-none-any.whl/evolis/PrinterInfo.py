# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from evolis.Type import Type
from evolis.Mark import Mark
from evolis.Model import Model


class _CPrinterInfo(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 128),
        ("type", ctypes.c_int),
        ("mark", ctypes.c_int),
        ("markName", ctypes.c_char * 32),
        ("model", ctypes.c_int),
        ("modelName", ctypes.c_char * 32),
        ("modelId", ctypes.c_int),
        ("fwVersion", ctypes.c_char * 16),
        ("serialNumber", ctypes.c_char * 16),
        ("printHeadKitNumber", ctypes.c_char * 16),
        ("zone", ctypes.c_char * 16),
        ("hasFlip", ctypes.c_bool),
        ("hasEthernet", ctypes.c_bool),
        ("hasWifi", ctypes.c_bool),
        ("hasLaminator", ctypes.c_bool),
        ("hasLaminator2", ctypes.c_bool),
        ("hasMagEnc", ctypes.c_bool),
        ("hasJisMagEnc", ctypes.c_bool),
        ("hasSmartEnc", ctypes.c_bool),
        ("hasContactLessEnc", ctypes.c_bool),
        ("hasLcd", ctypes.c_bool),
        ("hasKineclipse", ctypes.c_bool),
        ("hasLock", ctypes.c_bool),
        ("hasScanner", ctypes.c_bool),
        ("insertionCaps", ctypes.c_int),
        ("ejectionCaps", ctypes.c_int),
        ("rejectionCaps", ctypes.c_int),
        ("lcdFwVersion", ctypes.c_char * 16),
        ("lcdGraphVersion", ctypes.c_char * 16),
        ("scannerFwVersion", ctypes.c_char * 64),
    ]


class PrinterInfo:
    def __init__(self, c_printer_info: _CPrinterInfo):
        self.name = str(c_printer_info.name, "ascii")
        self.type = Type.from_int(c_printer_info.type)
        self.mark = Mark.from_int(c_printer_info.mark)
        self.markName = str(c_printer_info.markName, "ascii")
        self.model = Model.from_int(c_printer_info.model)
        self.modelName = str(c_printer_info.modelName, "ascii")
        self.modelId = int(c_printer_info.modelId)
        self.fwVersion = str(c_printer_info.fwVersion, "ascii")
        self.serialNumber = str(c_printer_info.serialNumber, "ascii")
        self.printHeadKitNumber = str(c_printer_info.printHeadKitNumber, "ascii")
        self.zone = str(c_printer_info.zone, "ascii")
        self.hasFlip = bool(c_printer_info.hasFlip)
        self.hasEthernet = bool(c_printer_info.hasEthernet)
        self.hasWifi = bool(c_printer_info.hasWifi)
        self.hasLaminator = bool(c_printer_info.hasLaminator)
        self.hasLaminator2 = bool(c_printer_info.hasLaminator2)
        self.hasMagEnc = bool(c_printer_info.hasMagEnc)
        self.hasJisMagEnc = bool(c_printer_info.hasJisMagEnc)
        self.hasSmartEnc = bool(c_printer_info.hasSmartEnc)
        self.hasContactLessEnc = bool(c_printer_info.hasContactLessEnc)
        self.hasLcd = bool(c_printer_info.hasLcd)
        self.hasKineclipse = bool(c_printer_info.hasKineclipse)
        self.hasLock = bool(c_printer_info.hasLock)
        self.hasScanner = bool(c_printer_info.hasScanner)
        self.insertionCaps = int(c_printer_info.insertionCaps)
        self.ejectionCaps = int(c_printer_info.ejectionCaps)
        self.rejectionCaps = int(c_printer_info.rejectionCaps)
        self.lcdFwVersion = str(c_printer_info.lcdFwVersion, "ascii")
        self.lcdGraphVersion = str(c_printer_info.lcdGraphVersion, "ascii")
        self.scannerFwVersion = str(c_printer_info.scannerFwVersion, "ascii")
