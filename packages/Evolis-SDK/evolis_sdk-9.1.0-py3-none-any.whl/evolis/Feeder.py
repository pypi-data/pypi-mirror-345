# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class Feeder(Enum):
    """
    The enumeration is used to configure feeder of KC Max printers.
    """

    def from_int(n:int):
        """
        Create a Feeder enum from integer.

        Parameters
        ----------
        n: int
            Value to convert to Feeder.

        Returns
        -------
        Feeder:
            The converted value.
        """
        try:
            f = Feeder(n)
        except ValueError:
            f = Feeder.UNKNOWN
        return f

    UNKNOWN = 0
    """
    Unknown feeder.
    """

    A = 1
    """
    Feeder A, KC Max printers only.
    """

    B = 2
    """
    Feeder B, KC Max printers only.
    """

    C = 3
    """
    Feeder C, KC Max printers only.
    """

    D = 4
    """
    Feeder D, KC Max printers only.
    """

