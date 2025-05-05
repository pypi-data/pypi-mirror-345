# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class Type(Enum):
    """
    List device's possible types.
    """

    @staticmethod
    def from_int(v: int):
        try:
            return Type(v)
        except ValueError:
            return Type.AUTO

    AUTO = 0
    EVOLIS = 1
    AVANSIA = 2
