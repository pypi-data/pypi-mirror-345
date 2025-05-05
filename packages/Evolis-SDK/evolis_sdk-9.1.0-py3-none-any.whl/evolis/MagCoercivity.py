# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class MagCoercivity(Enum):
    """
    Magnetic coercivity values.
    """

    @staticmethod
    def from_int(v: int):
        try:
            return MagCoercivity(v)
        except TypeError:
            return MagCoercivity.AUTO

    PRINTER = ord('p')
    """
    Use printer setting.
    """

    AUTO = ord('a')
    """
    Automatic mode, the printer will find the coercivity alone.
    """

    LOCO = ord('l')
    """
    Low coercivity cards.
    """

    HICO = ord('h')
    """
    High coercivity cards.
    """

