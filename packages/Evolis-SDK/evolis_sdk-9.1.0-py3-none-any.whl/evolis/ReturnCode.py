# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class ReturnCode(Enum):
    """
    Return code values.
    """

    def from_int(n:int):
        """
        Create a ReturnCode enum from integer.

        Parameters
        ----------
        n: int
            Value to convert to ReturnCode.

        Returns
        -------
        ReturnCode:
            The converted value.
        """
        rc = ReturnCode.OK
        if n < 0:
            try:
                rc = ReturnCode(n)
            except ValueError:
                rc = ReturnCode.EUNDEFINED
        return rc

    OK = 0
    """ Everything is good. """

    EUNDEFINED = -1
    """ Error code when an undefined error occurs. """

    EUNSUPPORTED = -5
    """ Error code when the library or printer does not support requested feature. """

    EPARAMS = -6
    """ Invalid params given to the API. """

    ETIMEOUT = -7
    """ A timeout occured during function call. """

    SESSION_ETIMEOUT = -10
    """ Printer reservation have expired. """

    SESSION_EBUSY = -11
    """ Printer in use, session detected. """

    SESSION_DISABLED = -12
    """ Session management is disabled. See evolis_set_session_management(). """

    SESSION_FAILED = -13
    """ An error was encountered while trying to reserve the printer """

    SESSION_ENABLED = -14
    """ This operation is not available when the session management is on. See evolis_set_session_management(). """

    PRINT_EDATA = -20
    """ Bad input data, check images and settings. """

    PRINT_NEEDACTION = -21
    """ Printer not ready to print. Cover open ? Feeder ? """

    PRINT_EMECHANICAL = -22
    """ Mechanical error happened while printing. """

    PRINT_WAITCARDINSERT = -23
    """ Avansia only """

    PRINT_WAITCARDEJECT = -24
    """ Avansia only """

    PRINT_EUNKNOWNRIBBON = -25
    """ Missing GRibbonType setting. """

    PRINT_ENOIMAGE = -26
    """ No image given. """

    PRINT_WSETTING = -27
    """ Settings were imported from the driver, and at least one could not be read """

    LAM_ENOCOM = -40
    """ The laminator module is missing or can't communicate with the printer """

    LAM_EDEVICE = -41
    """ The device is not a laminator module """

    LAM_ERROR = -42
    """ The lamination module indicated an error """

    LAM_EVALUE = -43
    """ The value used or returned by the lamination module doesn't match the expected format """

    MAG_ERROR = -50
    """ Error reading or writing magnetic data. """

    MAG_EDATA = -51
    """ The data that you are trying to write on the magnetic track is not valid. """

    MAG_EBLANK = -52
    """ Magnetic track is blank. """

    PRINTER_ENOCOM = -60
    """ Printer offline. """

    PRINTER_EREPLY = -61
    """ Printer reply contains "ERR". """

    PRINTER_EOTHER = -62
    """ macOS only. USB printer in use by other software. """

    PRINTER_EBUSY = -63
    """ macOS only. CUPS is printing. """

    PRINTER_NOSTATUS = -64
    """ Status disabled on the printer. """

    SVC_ENOCOM = -10000
    """ Failed to communicate with the service """

    SVC_EREPLY = -10001
    """ Invalid service reply """

    SVC_ERROR = -10002
    """ The service indicated an error """

    SVC_EDATA = -10003
    """ The input data could not be sent to the service """

    SVC_NO_EVENT = -10004
    """ There is no active event for the printer """

    SVC_EEVENT = -10005
    """ The selected event is not active for the printer """

    SVC_EACTION = -10006
    """ The selected action is not active for current printer event """

    HTTP_REPLY_NOT_OK = -20000
    """ A reply was received with an HTTP error code (internal usage) """

    HTTP_EREQUEST_ERROR = -20001
    """ The HTTP request is invalid """

    HTTP_EREPLY_FORMAT = -20002
    """ The received data didn't match the expected format """

    HTTP_ERROR = -20500
    """ An unexpected HTTP communication error occured """

