# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class RwCardType(Enum):
    """
    List of rewritable card type accepted by Evolis printers.
    """

    def from_int(n : int):
        try:
            return RwCardType(n)
        except ValueError:
            return RwCardType.UNKNOWN

    UNKNOWN = -1
    MBLACK = 0
    MBLUE = 1
    CUSTOM_FRONT = 2
    CUSTOM_DUPLEX = 3
