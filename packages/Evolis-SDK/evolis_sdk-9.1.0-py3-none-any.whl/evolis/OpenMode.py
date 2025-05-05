# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class OpenMode(Enum):
    """
    List of the different possible open modes.
    """

    def from_int(n:int):
        try:
            return OpenMode(n)
        except ValueError:
            return OpenMode.AUTO

    AUTO = 0
    """
    Automatically determines which other mode should be used
    """

    DIRECT = 1
    """
    Direct communication with the printer
    """

    SUPERVISED = 2
    """
    The communications with the printer will go through the Evolis Supervision Service
    """

