# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
import sys

from evolis.BezelBehavior import BezelBehavior
from evolis.CardFace import CardFace
from evolis.CardPos import CardPos
from evolis.CleaningInfo import _CCleaningInfo
from evolis.CleaningInfo import CleaningInfo
from evolis.Device import Device
from evolis.OpenMode import OpenMode
from evolis.ErrorManagement import ErrorManagement
from evolis.Evolis import Evolis
from evolis.Feeder import Feeder
from evolis.InputTray import InputTray
from evolis.LaminatorFilmInfo import _CLaminatorFilmInfo
from evolis.LaminatorFilmInfo import LaminatorFilmInfo
from evolis.LaminatorIndex import LaminatorIndex
from evolis.LaminatorInfo import _CLaminatorInfo
from evolis.LaminatorInfo import LaminatorInfo
from evolis.LaminatorMode import LaminatorMode
from evolis.OutputTray import OutputTray
from evolis.PrinterInfo import _CPrinterInfo
from evolis.PrinterInfo import PrinterInfo
from evolis.ReturnCode import ReturnCode
from evolis.RibbonInfo import _CRibbonInfo
from evolis.RibbonInfo import RibbonInfo
from evolis.State import State
from evolis.Status import _CStatus
from evolis.Status import Status
from evolis.ServiceAction import ServiceAction

from typing import Optional, Tuple, List


def _inbuf(data):
    if type(data) == str:
        return data.encode("utf8")
    elif type(data) == bytearray:
        return bytes(data)
    return data


def _instr(data):
    return data.encode("utf8")


def _outstr(data):
    return data.decode("utf8")


class Connection:
    __DEFAULT_TIMEOUT = 30000  # 30s
    __DEFAULT_WAIT_TIMEOUT = 5000  # 5s

    def __init__(self, printer=None, mode: OpenMode = OpenMode.AUTO) -> None:
        """
        Create a printer connection.

        Parameters
        ----------
        printer
            Optionnal, can either be a string designating the printer to use or a
            Device instance.

        mode: OpenMode
            The way to connect to the printer.
        """
        self.__context = None
        self.__last_error = ReturnCode.OK
        if isinstance(printer, str):
            self.open(printer, mode)
        elif isinstance(printer, Device):
            self.open_device(printer, mode)

    def __del__(self) -> None:
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def get_context(self) -> ctypes.c_void_p:
        """
        Returns the internal evolis_t* context.

        Returns
        -------
        ctypes.c_void_p
            Pointer holding the Connection context.
        """
        return self.__context

    def get_last_error(self) -> ReturnCode:
        """
        Returns
        -------
        ReturnCode
            Returns the last error code encountered.
        """
        return self.__last_error

    def set_last_error(self, return_code: ReturnCode) -> None:
        """
        Force the value of the last error.

        Reserved for test purposes.

        Parameters
        ----------
        return_code
            The return code to force
        """
        self.__last_error = return_code

    def open(self, name: str, mode: OpenMode = OpenMode.AUTO) -> bool:
        """
        Open a connection to an Evolis device.

        Parameters
        ----------
        name: str
            The name of the printer to connect with.

        mode: OpenMode
            The way to connect to the printer.

        Returns
        -------
        bool
            True if connection to printer is open, false otherwise.
        """
        if self.__context is None:
            self.__context = Evolis.wrapper.evolis_open_with_mode(name.encode("utf-8"), mode.value)
            return self.__context is not None
        return False

    def open_device(self, device: Device, mode: OpenMode = OpenMode.AUTO):
        """
        Open a connection to an Evolis device.
        This variant allows you to use a Device object instead of the printer
        name.

        Parameters
        ----------
        device: Device
            The device to connect to.

        mode: OpenMode
            The way to connect to the printer.

        Returns
        -------
        bool
            True if connection to printer is open, false otherwise.
        """
        return self.open(device.name, mode)

    def get_open_mode(self) -> Optional[OpenMode]:
        """
        Return the mode of communication used with the printer.

        Returns
        -------
        OpenMode
            On success, returns a OpenMode object. On failure, returns None.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_open_mode(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return OpenMode.from_int(out.value)
        return None

    def is_open(self) -> bool:
        """
        Returns
        -------
        bool
            True if connection to printer is open, false otherwise.
        """
        print("'is_open()' is deprecated. Please use 'get_state()' instead.", file=sys.stderr)
        return self.__context is not None

    def close(self):
        """
        Close a connection established to an Evolis printer.
        """
        Evolis.wrapper.evolis_close(self.__context)
        self.__context = None
        self.__last_error = ReturnCode.OK

    def read(self, size: int = 1024, timeout_ms: int = __DEFAULT_TIMEOUT) -> Optional[bytearray]:
        """
        Read raw data from printer.
        Please note that this method always fails on supervised mode.

        Parameters
        ----------
        size: int
            The buffer size to use.

        timeout_ms: int
            Specify a maximum duration, in milliseconds, for the function to
            wait for a response from the printer.

        Returns
        -------
        bytearray
            Byte array containing buffer received from printer. Returns None on error and sets.
        """
        out = ctypes.create_string_buffer(size)
        n = Evolis.wrapper.evolis_readt(self.__context, out, size, timeout_ms)
        self.__last_error = ReturnCode.from_int(n)
        if n > 0:
            return bytearray(out.raw[:n])
        return None

    def write(self, data, timeout_ms: int = __DEFAULT_TIMEOUT) -> bool:
        """
        Write raw data to the printer.

        Parameters
        ----------
        data: bytearray
            Data to write to the printer.

        timeout_ms: int
            Specify a maximum duration, in milliseconds, for the function to
            wait for a response from the printer.

        Returns
        -------
        bool
            True on success, false otherwise. A call to get_last_error() can
            help in case of error.
        """
        d = _inbuf(data)
        n = Evolis.wrapper.evolis_writet(self.__context, d, len(d), timeout_ms)
        self.__last_error = ReturnCode.from_int(n)
        if n > 0:
            self.__last_error = ReturnCode.OK
            return True
        return False

    def send_command(self, cmd: str, reply_size: int = 1024, timeout_ms: int = __DEFAULT_TIMEOUT) -> Optional[str]:
        """
        Send a command to the printer and return its result.

        Parameters
        ----------
        cmd: str
            The command to send to the printer.

        reply_size: int
            The maximum size of the printer reply.

        timeout_ms: int
            Max duration in milliseconds that we should wait for the printer to
            answer

        Returns
        -------
        str
            Printer reply on success, None otherwise.
            See get_last_error() method to have detail on the error.
        """
        out = ctypes.create_string_buffer(reply_size)
        d = _inbuf(cmd)
        n = Evolis.wrapper.evolis_commandt(self.__context, d, len(d), out, reply_size, timeout_ms)
        self.__last_error = ReturnCode.from_int(n)
        if n > 0:
            return _outstr(out.raw[:n])
        return None

    def get_input_tray(self) -> Optional[InputTray]:
        """
        Get printer's  currently configured input tray.

        Returns
        -------
        InputTray
            On success, returns a InputTray object. On failure, returns None.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_input_tray(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return InputTray.from_int(out.value)
        return None

    def set_input_tray(self, tray: InputTray) -> bool:
        """
        Configure which tray should be used as an input.
        The following card entries are available for Evolis printers.
        Some entries are not valid for all printers.

        Parameters
        ----------
        tray: InputTray
            Specify which tray to use as an input tray.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_set_input_tray(self.__context, tray.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_output_tray(self) -> Optional[OutputTray]:
        """
        Get printer's  currently configured output tray.

        Returns
        -------
        OutputTray
            On success, returns a OutputTray object. On failure, returns None.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_output_tray(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return OutputTray.from_int(out.value)
        return None

    def set_output_tray(self, tray: OutputTray) -> bool:
        """
        Configure which tray should be used as an output.
        The following card entries are available for Evolis printers.
        Some entries are not valid for all printers.

        Parameters
        ----------
        tray: OutputTray
            Specify which tray to use as an output tray.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_set_output_tray(self.__context, tray.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_error_tray(self) -> Optional[OutputTray]:
        """
        Get printer's  currently configured error tray.

        Returns
        -------
        OutputTray
            On success, returns a OutputTray object. On failure, returns None.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_error_tray(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return OutputTray.from_int(out.value)
        return None

    def set_error_tray(self, tray: OutputTray) -> bool:
        """
        Configure which tray should be used as an error tray.

        Parameters
        ----------
        tray: OutputTray
            Specify which tray to use as an error tray.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_set_error_tray(self.__context, tray.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_card_pos(self, card_pos: CardPos) -> bool:
        """
        Set the card position in the printer.

        Parameters
        ----------
        card_pos:CardPos
            Indicates the position of the card.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_set_card_pos(self.__context, card_pos.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def insert_card(self) -> bool:
        """
        Helper function for inserting a card (uses set_card_pos()).

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_insert(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def eject_card(self) -> bool:
        """
        Helper function for ejecting a card (uses set_card_pos()).

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_eject(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def reject_card(self) -> bool:
        """
        Helper function for ejecting a card to error slot (uses set_card_pos()).

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_reject(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def firmware_update(self, path: str, timeout_ms: int = 0) -> bool:
        """
        Update the printer's firmware with the provided file path.

        Parameters
        ----------
        path: str
            Path to the firmware file.

        timeout_ms: int
            Specify a maximum duration, in milliseconds, for the function to
            wait for the update to end.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_firmware_updatet(self.__context, _inbuf(path), timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def firmware_update_with_buffer(self, data, timeout_ms: int = 0) -> bool:
        """
        Update the printer's firmware with the provided buffer.

        Parameters
        ----------
        data:
            Must contain the firmware update data.

        timeout_ms: int
            Specify a maximum duration, in milliseconds, for the function to
            wait for the update to end.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        d = _inbuf(data)
        rc = Evolis.wrapper.evolis_firmware_updatebt(self.__context, d, len(data), timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def reset(self, timeout_secs: int = 0) -> bool:
        """
        Software reset of the printer.
        The function returns when the printer switches back to ready state.

        Parameters
        ----------
        timeout_secs: int
           Max duration in seconds that we should wait for the printer to restart.

        Returns
        -------
        bool
            True if printer was reset and is ready, false otherwise.
        """
        timeouted = ctypes.c_bool(False)
        rc = Evolis.wrapper.evolis_reset(self.__context, timeout_secs, ctypes.byref(timeouted))
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def reserve(self, session: int = 0, wait_ms: int = __DEFAULT_WAIT_TIMEOUT) -> bool:
        """
        Can be used to reserve a session on the printer. When a printer is
        reserved :
         - No one else can reserve the printer.
         - No one else can start a printing job.
         - The LCD screen is not available.

        To get the actual session id, please call get_status() to retrieve an
        object containing current session id.

        Parameters
        ----------
        session: int
             Desired session id. The returned session id may be different.

        wait_ms: int
            If printer is busy, wait, at most, for waitMs milliseconds.

        Returns
        -------
        bool
            True if succeeded, false otherwise.
        """
        sid = Evolis.wrapper.evolis_reserve(self.__context, session, wait_ms)
        self.__last_error = ReturnCode.from_int(sid)
        if sid == 0:
            self.__last_error = ReturnCode.SESSION_EBUSY
        return self.__last_error == ReturnCode.OK

    def release(self) -> bool:
        """
        Release a reserved session. Calling 'close()' also release the printer
        reservation.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_release(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_session_management(self) -> bool:
        """
        Get session management setting for current connection. Its value is
        true by default but is forced to false on following contexts : Quantum
        printers, Android USB (all printers).

        Returns
        -------
        bool
            False if session management is off, True otherwise.
        """
        rc = Evolis.wrapper.evolis_get_session_management(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_session_management(self, sm: bool) -> None:
        """
        Set session management for current connection. Its value is true by default.

        Session management ensure the user that only one person at a time is using
        the printer. When a session is taken by someone, nobody else can communicate
        with printer. In case of 45s of inactivity, the session is released.
        Disabling session management is not recommended, it should be made only if
        you exactly know what you are doing.

        Parameters
        ----------
        sm: bool
            Indicates the state of the printer's session management.
            False if session management is off, True otherwise.
        """
        Evolis.wrapper.evolis_set_session_management(self.__context, sm)
        self.__last_error = ReturnCode.OK

    def get_error_management(self) -> Optional[ErrorManagement]:
        """
        Get error management mode of the printer. Error modes are :

        - Printer:
          The printer manages by itself errors.

        - Software:
          Errors are handled by the software using the printer (you).

        - Supervised:
          Errors are handled by the Evolis Premium Suite service.

        Returns
        -------
        ErrorManagement
            On success, returns an ErrorManagement object. On failure, returns None.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_error_management(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        return ErrorManagement.from_int(out.value)

    def set_error_management(self, em: ErrorManagement) -> bool:
        """
        Set error management mode of the printer. It's only possible to set PRINTER or SOFTWARE modes
        because the SUPERVISED mode can only be set by the Evolis Premium Suite service.

        It's allowed to change the value even if the current mode is SUPERVISED,
        but it is not recommended because you will not be able to restore it.

        Parameters
        ----------
        em:ErrorManagement
            Specify the error management behaviour of the printer.

        Returns
        -------
        bool
            Indicating if the function succeeded or not.
        """
        rc = Evolis.wrapper.evolis_set_error_management(self.__context, em.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_status(self) -> Optional[Status]:
        """
        Get the current status (flags) of the printer. This method doesn't work
        with Avansia printers.

        Returns
        -------
        Status
            Status object on success, None otherwise.
            See get_last_error() method to have detail on the error.
        """
        c_status = _CStatus()
        rc = Evolis.wrapper.evolis_status(self.__context, ctypes.byref(c_status))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return Status(c_status)
        return None

    def enable_status(self) -> bool:
        """
        Enables the status fields in the printer's replies.

        Returns
        -------
        bool
            True if status have been enabled with success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_status_enable(self.__context)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def send_status_request(self) -> Optional[Status]:
        """
        Send a command to get the status of the printer.

        Returns
        -------
        Status
            Status object on success, None otherwise.
            See get_last_error() method to have detail on the error.
        """
        c_status = _CStatus()
        rc = Evolis.wrapper.evolis_status_send_request(self.__context, ctypes.byref(c_status))
        self.__last_error = ReturnCode.from_int(rc)
        if rc == 0:
            return Status(c_status)
        return None

    def get_state(self) -> State:
        """
        Get printer state. State is generated from multiple input data,
        including printer flags.

        Returns
        -------
        State
            State object describing the printer's current state.
            See get_last_error() method to have detail on the error.
        """
        c_major = ctypes.c_int(0)
        c_minor = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_state(self.__context, ctypes.byref(c_major), ctypes.byref(c_minor))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return State.from_int(c_major.value, c_minor.value)
        return State(State.Major.OFF, State.Minor.PRINTER_UNKNOWN)

    def get_info(self) -> Optional[PrinterInfo]:
        """
        Get printer information.

        Returns
        -------
        PrinterInfo
            On success, returns a PrinterInfo object. On failure, returns None.
        """
        c_printer_info = _CPrinterInfo()
        rc = Evolis.wrapper.evolis_get_info(self.__context, ctypes.byref(c_printer_info))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error is ReturnCode.OK:
            return PrinterInfo(c_printer_info)
        return None

    def get_ribbon_info(self) -> Optional[RibbonInfo]:
        """
        Gets the ribbon information. Currently, Avansia printers are not supported
        by this function.

        Returns
        -------
        RibbonInfo
            On success, returns a RibbonInfo object. On failure, returns None.
        """
        c_ribbon_info = _CRibbonInfo()
        rc = Evolis.wrapper.evolis_get_ribbon(self.__context, ctypes.byref(c_ribbon_info))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return RibbonInfo(c_ribbon_info)
        return None

    def get_retransfer_film_info(self) -> Optional[RibbonInfo]:
        """
        Gets the retransfer film information. Currently, Avansia printers are not supported
        by this function.

        Returns
        -------
        RibbonInfo
            On success, returns a RibbonInfo object. On failure, returns None.
        """
        c_ribbon_info = _CRibbonInfo()
        rc = Evolis.wrapper.evolis_get_retransfer_film(self.__context, ctypes.byref(c_ribbon_info))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return RibbonInfo(c_ribbon_info)
        return None

    def get_cleaning_info(self) -> Optional[CleaningInfo]:
        """
        Get printer's cleaning information.

        Returns
        -------
        CleaningInfo
            On success, returns a CleaningInfo object. On failure, returns None.
        """
        c_cleaning_info = _CCleaningInfo()
        rc = Evolis.wrapper.evolis_get_cleaning(self.__context, ctypes.byref(c_cleaning_info))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return CleaningInfo(c_cleaning_info)
        return None

    def get_bezel_behavior(self) -> Optional[BezelBehavior]:
        """
        Get BEZEL behavior.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Returns
        -------
        BezelBehavior
            Returns a `BezelBehavior` value. Returns `BezelBehavior.UNKNOWN` on error.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_bezel_get_behavior(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        return BezelBehavior.from_int(out.value)

    def set_bezel_behavior(self, bb: BezelBehavior) -> bool:
        """
        The BEZEL can be configured to re-insert or reject the card after a
        pre-defined delay. It can also be configured to do nothing : i.e. keep the
        card in the BEZEL.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Parameters
        ----------
        bb:BezelBehavior
            Action to trigger when BEZEL delay expire.

        Returns
        -------
        bool
            Returns true on success.
            See value of `get_last_error()` if false is returned.
        """
        rc = Evolis.wrapper.evolis_bezel_set_behavior(self.__context, bb.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_bezel_delay(self) -> int:
        """
        Retrieve BEZEL delay. The delay is the number of seconds to wait before
        triggering the BEZEL action.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Returns
        -------
        int
            Returns the BEZEL delay in seconds.
            If `0` is returned please check `get_last_error()` method.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_bezel_get_delay(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return out.value
        return 0

    def set_bezel_delay(self, seconds: int) -> bool:
        """
        Configure BEZEL delay after which the action is
        executed.

        The delay is expressed in seconds.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Returns `ReturnCode.EPARAMS` if an invalid delay is given.

        Parameters
        ----------
        seconds:int
            Number of seconds to wait before triggering bezel action.

        Returns
        -------
        bool
            Returns true on success.
            See value of `get_last_error()` if false is returned.
        """
        rc = Evolis.wrapper.evolis_bezel_set_delay(self.__context, seconds)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_bezel_offset(self) -> int:
        """
        Get the ejection length, in millimeters, of the card.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Returns
        -------
        int
            Returns the BEZEL offset in millimeters.
            If `0` is returned please check `get_last_error()` method.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_bezel_get_offset(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error == ReturnCode.OK:
            return out.value
        return 0

    def set_bezel_offset(self, mm: int) -> bool:
        """
        Set the ejection length, in millimeters, of the card.
        The ejection length value must be within the range of 17 to 68 millimeters.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        a BEZEL.

        Returns `ReturnCode.EPARAMS` if an invalid delay is given.

        Parameters
        ----------
        mm:int
            The ejection length to set (expressed in millimeters).

        Returns
        -------
        bool
            Returns true on success.
            See value of `get_last_error()` if false is returned.
        """
        rc = Evolis.wrapper.evolis_bezel_set_offset(self.__context, mm)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_feeder(self) -> Optional[Feeder]:
        """
        Get selected feeder for printer.
        Should only be used on a KC Max (aka K24) printer.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        multiple feeders (LIPI).

        Returns
        -------
        Feeder
            Returns a `Feeder` value. Returns `Feeder.UNKNOWN` on error.
        """
        out = ctypes.c_int(0)
        rc = Evolis.wrapper.evolis_get_feeder(self.__context, ctypes.byref(out))
        self.__last_error = ReturnCode.from_int(rc)
        return Feeder.from_int(out.value)

    def set_feeder(self, f: Feeder) -> bool:
        """
        Set printer feeder to use for next card insertion.
        Should only be used on a KC Max (aka K24) printer.

        Once the feeder is configured, printer status are updated
        to match the feeder state. For example, if the feeder is
        empty, the WAR_FEEDER_EMPTY flag is raised.

        Returns `ReturnCode.EUNSUPPORTED` if the printer doesn't have
        multiple feeders (LIPI).

        Parameters
        ----------
        f:Feeder
            The feeder to use.

        Returns
        -------
        bool
            Returns true on success.
            See value of `get_last_error()` if false is returned.
        """
        rc = Evolis.wrapper.evolis_set_feeder(self.__context, f.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def is_laminator_valid(self, index: LaminatorIndex, timeout_ms: int = __DEFAULT_TIMEOUT) -> bool:
        """
        Indicates whether the laminator index corresponds to a valid laminator.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to check.

        timeout_ms:int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            Returns true if the laminator index corresonds to a valid laminator.
            See value of `get_last_error()` if false is returned.
        """
        rc = Evolis.wrapper.evolis_laminator_is_validt(self.__context, index.value, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_laminator_info(self, index: LaminatorIndex, timeout_ms: int = __DEFAULT_TIMEOUT) -> Optional[LaminatorInfo]:
        """
        Get laminator information.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to check.

        timeout_ms:int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        LaminatorInfo
            On success, returns a LaminatorInfo object. On failure, returns None.
        """
        c_laminator_info = _CLaminatorInfo()
        rc = Evolis.wrapper.evolis_laminator_infot(
            self.__context, index.value, ctypes.byref(c_laminator_info), timeout_ms
        )
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error is ReturnCode.OK:
            return LaminatorInfo(c_laminator_info)
        return None

    def get_laminator_film_info(
        self, index: LaminatorIndex, timeout_ms: int = __DEFAULT_TIMEOUT
    ) -> Optional[LaminatorFilmInfo]:
        """
        Get laminator film information.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to check.

        timeout_ms:int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        LaminatorFilmInfo
            On success, returns a LaminatorFilmInfo object. On failure, returns None.
        """
        c_laminator_film_info = _CLaminatorFilmInfo()
        rc = Evolis.wrapper.evolis_laminator_filmt(
            self.__context, index.value, ctypes.byref(c_laminator_film_info), timeout_ms
        )
        self.__last_error = ReturnCode.from_int(rc)
        if self.__last_error is ReturnCode.OK:
            return LaminatorFilmInfo(c_laminator_film_info)
        return None

    def is_parallel_mode_enabled(self, timeout_ms: int = __DEFAULT_TIMEOUT) -> bool:
        """
        Indicates whether the parallel mode is enabled for lamination.

        Parameters
        ----------
        timeout_ms:int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            Returns true if a new printing job can be started while a card is being laminated.
            See value of `get_last_error()` if false is returned.
        """
        c_is_enabled = ctypes.c_bool()
        rc = Evolis.wrapper.evolis_laminator_is_parallel_mode_enabledt(
            self.__context, ctypes.byref(c_is_enabled), timeout_ms
        )
        self.__last_error = ReturnCode.from_int(rc)
        return bool(c_is_enabled)

    def enable_parallel_mode(self, enable: bool, timeout_ms: int = __DEFAULT_TIMEOUT) -> bool:
        """
        Enables or disables the parallel mode for lamination.

        Parameters
        ----------
        enable:bool
            Indicates the new state for the parallel mode.
            True to enable, false to disable.

        timeout_ms:int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_laminator_enable_parallel_modet(self.__context, enable, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_laminator_speed_cfg(
        self, index: LaminatorIndex, face: CardFace, value: int, timeout_ms: int = __DEFAULT_TIMEOUT
    ) -> bool:
        """
        Set the lamination speed for a given card side.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to configure.

        face:CardFace
            The card side to configure.

        value:int
            The new speed value in the [1,20] range.

        timeout_ms: int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_laminator_set_speed_cfgt(self.__context, index.value, face.value, value, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_laminator_temp_cfg(
        self, index: LaminatorIndex, face: CardFace, value: int, timeout_ms: int = __DEFAULT_TIMEOUT
    ) -> bool:
        """
        Set the lamination temperature for a given card side.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to configure.

        face:CardFace
            The card side to configure.

        value:int
            The new temperature value in the [1,20] range.

        timeout_ms: int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_laminator_set_temp_cfgt(self.__context, index.value, face.value, value, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_laminator_mode(
        self, index: LaminatorIndex, mode: LaminatorMode, timeout_ms: int = __DEFAULT_TIMEOUT
    ) -> bool:
        """
        Set the lamination mode.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to configure.

        mode:LaminatorMode
            The new laminator mode to set.

        timeout_ms: int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_laminator_set_modet(self.__context, index.value, mode.value, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def set_laminator_first_patch(
        self, index: LaminatorIndex, front: bool, timeout_ms: int = __DEFAULT_TIMEOUT
    ) -> bool:
        """
        Set on which card side to apply the first lamination patch.

        Parameters
        ----------
        index:LaminatorIndex
            The lamination module to configure.

        front:bool
            If `true` the first patch will be applied on the front,
            otherwise it will be applied on the back.

        timeout_ms: int
            Maximum time in milliseconds to wait for printer response.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        rc = Evolis.wrapper.evolis_laminator_set_first_patcht(self.__context, index.value, front, timeout_ms)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK

    def get_event(self) -> Optional[Tuple[str, List[ServiceAction]]]:
        """
        Get the current event for a printer

        Returns
        -------
        (str, set[serviceAction])
            The name of the ongoing event, and the associated available actions
        """
        event_name = ctypes.create_string_buffer(64)
        n = Evolis.wrapper.evolis_service_get_printer_event(self.__context, event_name, 64)
        self.__last_error = ReturnCode.from_int(n)

        if n >= 0:
            actions = list()
            for action in ServiceAction:
                if action is not ServiceAction.NONE and Evolis.wrapper.evolis_service_is_action_available(
                    n, action.value
                ):
                    actions.append(action)

            return _outstr(event_name.value), actions
        return None

    def set_event(self, event_name: str, action: ServiceAction) -> bool:
        """
        Sends a reply to an active event

        Parameters
        ----------
        event_name:str
            The name of the targeted event, received from `get_event`

        action: ServiceAction
            The action to send as a reply

        Returns
        -------
        bool
            True if the action was successfully applied
        """
        rc = Evolis.wrapper.evolis_service_set_printer_event(self.__context, _instr(event_name), action.value)
        self.__last_error = ReturnCode.from_int(rc)
        return self.__last_error == ReturnCode.OK
