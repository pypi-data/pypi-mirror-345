# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class Mark(Enum):
    """
    References the mark of the printer.
    """

    def from_int(v:int):
        try:
            return Mark(v)
        except ValueError:
            return Mark.INVALID

    INVALID = 0
    Evolis = 1
    Edikio = 3
    BadgePass = 4
    ID_Maker = 5
    Durable = 6
    Plasco = 7
    Identisys = 8
    Bodno = 9
    BRAVO = 10
    ATC = 11
