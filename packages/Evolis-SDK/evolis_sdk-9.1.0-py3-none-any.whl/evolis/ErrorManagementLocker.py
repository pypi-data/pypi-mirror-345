# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import evolis


class ErrorManagementLocker:
    """
    ErrorManagementLocker is used to lock the error management system of the
    printer to `ErrorManagement.SOFTWARE`.

    The error management is updated only if configured to
    ErrorManagement.PRINTER.

    ErrorManagementLocker was designed to be used with the "with" statement :

    ```python
    with ErrorManagementLocker(co):
        # This code block will be executed with error management configured
        # to one of ErrorManagement.SOFTWARE or ErrorManagement.SUPERVISED.
        #
        # The original error management setting is restored when leaving
        # block.
    ```
    """

    def __init__(self, connection: evolis.Connection):
        """
        Constructor of ErrorManagementLocker.

        Attributes
        ----------
        connection: evolis.Connection
            The connection object to use.
        """
        if connection is None:
            raise TypeError("PrintSession.__init__(): 'connection' argument is not valid.")
        self.__co = connection
        self.__em = None

    def __enter__(self):
        self.__em = self.__co.get_error_management()
        if self.__em != None:
            if self.__em == evolis.ErrorManagement.PRINTER:
                self.__co.set_error_management(evolis.ErrorManagement.SOFTWARE)

    def __exit__(self, *args):
        if self.__em == evolis.ErrorManagement.PRINTER:
            self.__co.set_error_management(self.__em)
