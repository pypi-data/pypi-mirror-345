# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes


class _CCleaningInfo(ctypes.Structure):
    _fields_ = [
        ("totalCardCount", ctypes.c_int),
        ("cardCount", ctypes.c_int),
        ("cardCountBeforeWarning", ctypes.c_int),
        ("cardCountBeforeWarrantyLost", ctypes.c_int),
        ("cardCountAtLastCleaning", ctypes.c_int),
        ("regularCleaningCount", ctypes.c_int),
        ("advancedCleaningCount", ctypes.c_int),
        ("printHeadUnderWarranty", ctypes.c_bool),
        ("warningThreshold", ctypes.c_int),
        ("warrantyLostThreshold", ctypes.c_int),
    ]


class CleaningInfo:
    def __init__(self, c_cleaning_info: _CCleaningInfo):
        self.totalCardCount = int(c_cleaning_info.totalCardCount)
        self.cardCount = int(c_cleaning_info.cardCount)
        self.cardCountBeforeWarning = int(c_cleaning_info.cardCountBeforeWarning)
        self.cardCountBeforeWarrantyLost = int(c_cleaning_info.cardCountBeforeWarrantyLost)
        self.cardCountAtLastCleaning = int(c_cleaning_info.cardCountAtLastCleaning)
        self.regularCleaningCount = int(c_cleaning_info.regularCleaningCount)
        self.advancedCleaningCount = int(c_cleaning_info.advancedCleaningCount)
        self.printHeadUnderWarranty = bool(c_cleaning_info.printHeadUnderWarranty)
        self.warningThreshold = int(c_cleaning_info.warningThreshold)
        self.warrantyLostThreshold = int(c_cleaning_info.warrantyLostThreshold)
