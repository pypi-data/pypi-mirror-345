# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class LaminatorMode(Enum):
    """
    Laminator index values.
    """

    def from_int(n:int):
        try:
            return LaminatorMode(n)
        except ValueError:
            return LaminatorMode.UNKNOWN

    UNKNOWN = 0
    EJECT = 1
    FRONT = 2
    BACK = 3
    FRONT_BACK = 4
    BACK_FRONT = 5
    FRONT_FLIP = 6
    BACK_FLIP = 7
