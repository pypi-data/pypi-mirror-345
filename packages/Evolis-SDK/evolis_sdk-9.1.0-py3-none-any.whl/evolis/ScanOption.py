# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class ScanOption(Enum):
    """
    Scan option values.
    """

    WIDTH = 0
    """
    Card width in millimeters.
    """

    HEIGHT = 1
    """
    Card height in millimeters.
    """

    DPI = 2
    """
    By default scan is 600 DPI. See `evolis_dpi_t`.
    """

    CARD_OFFSET = 3
    """
    Default value is 155. Should be between 90 and 220.
    """

    CARD_LENGTH = 4
    """
    Default value is 1200 (CR80 cards).
    """

    CARD_SPEED = 5
    """
    Depends of DPI. For 600 DPI a good value is between 150 and 350.
    """

