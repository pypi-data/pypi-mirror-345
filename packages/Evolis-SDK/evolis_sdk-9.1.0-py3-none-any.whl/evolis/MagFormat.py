# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class MagFormat(Enum):
    """
    Magnetic formats values.
    """

    @staticmethod
    def from_int(v: int):
        try:
            return MagFormat(v)
        except TypeError:
            return MagFormat.UNKNOWN

    UNKNOWN = 0

    ISO1 = 1 # Accepts alphanumeric characters, see ISO/IEC-7811 for details.

    ISO2 = 2 # Accepts numeric characters, see ISO/IEC-7811 for details.

    ISO3 = 3 # Accepts numeric characters, see ISO/IEC-7811 for details.

    SIPASS = 4

    CUSTOM2 = 5

    JIS2 = 6

    CUSTOM4 = 7
