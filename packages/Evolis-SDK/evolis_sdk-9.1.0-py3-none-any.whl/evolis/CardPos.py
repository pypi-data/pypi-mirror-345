# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class CardPos(Enum):
    """
    References the card position.
    """

    INSERT = 0
    """
    Insert a card in the printer.
    
    For Avansia printers, the insert is made inside a printing job when the
    return status of `avansia_print_restult()` is `AVANSIA_PR_STANDBY_INS`.
    """

    INSERTBACK = 1
    """
    Insert card from back side. Move it to
    default position.
    """

    INSERTEJECT = 2
    """
    Insert then eject a card from the printer.
    """

    EJECT = 3
    """
    Eject the card from the printer.
    
    For Avansia printers, the eject is made inside a printing job when the
    return status of `avansia_print_result()` is `AVANSIA_PR_STANDBY_EJE`.
    """

    REJECT = 4
    """
    Reject the card from the printer.
    
    TODO
    For Avansia printers, the insert is made inside a printing job when the
    return status is STANDBY. TODO Terminer la doc en fonction du retour de print_exec().
    """

    CONTACT = 5
    """
    Move the card to the smart station.
    The card is inserted if none in the printer.
    """

    CONTACTLESS = 6
    """
    Move the card to the contact station.
    The card is inserted if none in the printer.
    """

    SCAN = 7
    """
    Move the card in order to scan it (below the contact station).
    The card is inserted if none in the printer.
    """

