# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class InputTray(Enum):
    """
    Configure which tray should be used as an input.
    Some entries are not valid for all printers. See notes below for details.
    """

    def from_int(n:int):
        try:
            return InputTray(n)
        except ValueError:
            return InputTray.FEEDER

    FEEDER = 1
    """
    The card insertion will be made with the cards feeder.
    Supported by :
        - Avansia
        - Zenius
        - Primacy, Primacy 2
        - Agilia, Excelio
        - KC200, KC200B
        - KM500B, KM2000B
        - KC Prime, 
    """

    MANUAL = 2
    """
    The card insertion will be made card by card.
    Supported by :
        - Zenius
        - Primacy, Primacy 2
        - Elypso
        - Agilia, Excelio
        - KC Essential
    """

    MANUALANDCMD = 4
    """
    The card insertion will be made card by card but will be triggered when
    a insertion command is received by the printer.
    Supported by :
        - Avansia
        - Zenius
        - Primacy, Primacy 2
        - Elypso
        - Agilia, Excelio
        - KC200, KC200B
        - KM500B, KM2000B
        - KC Essential, KC Prime, KC Max
    
    To use this with Avansia printers, you will have to call `evolis_insert()`
    during the printing process in order to trigger the card insertion.
    @see avansia_print_status()
    """

    BEZEL = 8
    """
    The card insertion will be made from printer's bezel.
    Supported by :
        - KC200B
        - KM500B, KM2000B
        - KC Essential, KC Prime, KC Max
    """

    BOTH = 16
    """
    The card insertion can be made from to ways :
        - MANUAL/FEEDER :
          Concerned printers : Zenius, Agilia, Excelio, KC Prime, KC Max.
          Card inserted like MANUAL (card-by-card). If no card
          present, card is taken from FEEDER.
        - BEZEL/FEEDER :
          Concerned printers : KC200B, KM500B, KM2000B, KC Essential.
          Card inserted from BEZEL. If no card present, card is
          taken from FEEDER.
    """

    NOFEEDER = 32
    """
    Only available for customized printers without any feeder.
    """

    REAR = 64
    """
    Insert card from standard card output.
    Supported by :
        - Agilia, Excelio
        - KC Essential, KC Prime, KC Max
    """

