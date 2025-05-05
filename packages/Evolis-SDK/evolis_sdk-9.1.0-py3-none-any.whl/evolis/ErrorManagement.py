# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class ErrorManagement(Enum):
    """
    List of error management modes of the printer.
    """

    def from_int(n:int):
        try:
            return ErrorManagement(n)
        except ValueError:
            return ErrorManagement.UNKNOWN

    UNKNOWN = -1
    """
    Unknown error management.
    """

    PRINTER = 0
    """
    Means that the printer manages errors.
    """

    SOFTWARE = 2
    """
    Let the software using the printer manage errors.
    """

    SUPERVISED = 38
    """
    Means that the printer is supervised by the Evolis Premium Suite.
    This value can't be set. It can only be read.
    """

