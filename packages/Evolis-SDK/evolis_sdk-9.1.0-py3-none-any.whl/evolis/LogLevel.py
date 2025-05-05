# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class LogLevel(Enum):
    """
    Log level values.
    """

    TRACE = 0
    """
    Show ERROR, WARNING, INFO, DEBUG, TRACE messages.
    """

    DEBUG = 1
    """
    Show ERROR, WARNING, INFO, DEBUG messages.
    """

    INFO = 2
    """
    Show ERROR, WARNING, INFO messages.
    """

    WARNING = 3
    """
    Show ERROR, WARNING messages.
    """

    ERROR = 4
    """
    Show ERROR messages.
    """

