# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from evolis.LaminatorFilmType import LaminatorFilmType


class _CLaminatorFilmInfo(ctypes.Structure):
    _fields_ = [
        ("description", ctypes.c_char * 64),
        ("zone", ctypes.c_char * 8),
        ("type", ctypes.c_int),
        ("productCode", ctypes.c_char * 32),
        ("capacity", ctypes.c_int),
        ("remaining", ctypes.c_int),
        ("buildDate", ctypes.c_char * 32),
        ("serialNumber", ctypes.c_char * 32),
        ("internalCode", ctypes.c_char * 32),
        ("batchNumber", ctypes.c_char * 32),
    ]


class LaminatorFilmInfo:
    def __init__(self, c_laminator_film_info: _CLaminatorFilmInfo):
        self.description = str(c_laminator_film_info.description, "ascii")
        self.zone = str(c_laminator_film_info.zone, "ascii")
        self.type = LaminatorFilmType.from_int(c_laminator_film_info.type)
        self.productCode = str(c_laminator_film_info.productCode, "ascii")
        self.capacity = int(c_laminator_film_info.capacity)
        self.remaining = int(c_laminator_film_info.remaining)
        self.buildDate = str(c_laminator_film_info.buildDate, "ascii")
        self.serialNumber = str(c_laminator_film_info.serialNumber, "ascii")
        self.internalCode = str(c_laminator_film_info.internalCode, "ascii")
        self.batchNumber = str(c_laminator_film_info.batchNumber, "ascii")
