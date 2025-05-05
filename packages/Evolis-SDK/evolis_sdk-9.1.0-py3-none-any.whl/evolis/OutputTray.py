# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class OutputTray(Enum):
    """
    The following card exit are available for Evolis printers.
    Some of the exits are not valid for all printers. See notes below for details.
    """

    def from_int(n:int):
        try:
            return OutputTray(n)
        except ValueError:
            return OutputTray.STANDARD

    STANDARD = 1
    """
    Eject the card in the standard output tray (receptacle).
    Supported by :
        - Avansia
        - Zenius
        - Primacy, Primacy 2
        - KC200, KC200B
        - KM500B, KM2000B
        - Agilia, Excelio
        - KC Prime
    
    For Avansia printers the standard exit is the left side of the printer.
    """

    STANDARDSTANDBY = 2
    """
    Supported by Avansia printers only. If set, the printer will wait for
    ejection command (see `evolis_eject()`) at the end of print.
    """

    MANUAL = 4
    """
    Card by card ejection mode.
    Supported by :
        - Agilia, Excelio
        - Elypso
        - Zenius
        - KC Essential
    """

    ERROR = 8
    """
    Card will be ejected in the rejection tray.
    Supported by :
        - Agilia, Excelio
        - Avansia
        - Elypso
        - KC200
        - KM500B
        - KM2000B.
        - Primacy
        - Zenius
        - KC Prime
    
    With Avansia printers, the standard rejection tray is the right side.
    """

    ERRORSTANDBY = 16
    """
    Supported by Avansia printers only. If set, the printer will wait for
    ejection command (see `evolis_eject()`) at the end of print.
    """

    EJECT = 32
    """
    Eject the card without waiting.
    Supported by :
        - Zenius
        - Elypso
        - KC Essential
    """

    BEZEL = 64
    """
    Eject the card through the bezel.
    Supported by :
        - KC200B
        - KM500B, KM2000B
        - KC Prime, KC Max
    """

    ERRORSLOT = 128
    """
    Eject the card through the lower reject slot.
    Supported by :
        - KC200, KC200B
        - KM500B, KM2000B
        - KC Essential, KC Prime, KC Max
    """

    LOCKED = 256
    """
    Eject the card to the locked box.
    Supported by Primacys with locking system.
    """

