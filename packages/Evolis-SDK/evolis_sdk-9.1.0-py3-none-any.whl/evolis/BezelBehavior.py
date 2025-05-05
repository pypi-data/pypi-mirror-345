# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class BezelBehavior(Enum):
    """
    References the bezel behaviors.
    """

    def from_int(n:int):
        """
        Create a BezelBehavior enum from integer.

        Parameters
        ----------
        n: int
            Value to convert to BezelBehavior.

        Returns
        -------
        BezelBehavior:
            The converted value.
        """
        try:
            bb = BezelBehavior(n)
        except ValueError:
            bb = BezelBehavior.UNKNOWN
        return bb

    UNKNOWN = 0
    """
    Unknown BEZEL behavior.
    """

    REJECT = 1
    """
    Card is ejected to the error tray if not taken.
    """

    INSERT = 2
    """
    Card is re-inserted if not taken.
    """

    DONOTHING = 3
    """
    Card stays in the BEZEL if not taken.
    """

