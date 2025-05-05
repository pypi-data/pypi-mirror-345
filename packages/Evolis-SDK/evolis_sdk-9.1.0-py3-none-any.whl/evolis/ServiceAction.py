# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class ServiceAction(Enum):
    """
    Actions that may be applied in response to a printer event
    """

    @staticmethod
    def from_int(v: int):
        try:
            return ServiceAction(v)
        except ValueError:
            return ServiceAction.Unknown

    NONE = 0
    """
    NONE
    """

    OK = 1
    """
    OK
    Accept the proposed action
    """

    RETRY = 2
    """
    RETRY
    Retry the ongoing operation
    """

    CANCEL = 4
    """
    CANCEL
    Cancel the ongoing operation
    """

