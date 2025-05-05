# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes

from warnings import warn

from evolis.CardFace import CardFace
from evolis.Connection import _instr
from evolis.Connection import _outstr
from evolis.Connection import Connection
from evolis.Evolis import Evolis
from evolis.ReturnCode import ReturnCode
from evolis.SettingKey import SettingKey
from evolis.RibbonType import RibbonType
from evolis.RwCardType import RwCardType


class PrintSession:
    @staticmethod
    def print_test_card(co: Connection, type: int = 0) -> bool:
        """
        Start printing a test card.
        For Evolis printers, accepted types of tests are :
            - 0: "St" command (dual side test card).
            - 1: "Stt" command (single side test card).
        For Avansia printers, accepted types of tests are :
            - 0: "Test U" (dual side).
            - 1: "Test X" (single side).
            - 2: "Test Y" (single side).

        Parameters
        ----------
        co: Connection
            The device's connection object.

        type: int
            A value corresponding to the desired type of test.
        """
        res = Evolis.wrapper.evolis_print_test_card(co.get_context(), type)
        rc = ReturnCode.from_int(res)
        return rc == ReturnCode.OK

    def __init__(self, connection: Connection, *args, **kwargs):
        """
        Initialize a new printing session. A printing session contains graphics
        (images, text, barcode) and print forced settings.
        By default the session configuration is detected from the printer but
        a specific ribbon or rw configuration can be specified with a
        RibbonType or RwCardType parameter.
        The configuration type can be explicitly
        with ribbon=<RibbonType> or rwCard=<RwCardType>

        - `PrintSession(co) # Automatic configuration`
        - `PrintSession(co, RibbonType.YMCKO) # YMCKO configuration`
        - `PrintSession(connection=co, ribbon=RibbonType.YMCKO) # same with explicit naming `
        - `PrintSession(co, rwCard=RwCardType.MBLACK)`

        Parameters
        ----------
        connection: Connection
            Connection on which we want to perform printing.

        *args and **kwargs:
            RibbonType or RwCardType
        """
        if connection is None:
            raise TypeError("PrintSession.__init__(): 'connection' argument is not valid.")
        self.__context = connection.get_context()
        self.__last_error = ReturnCode.OK

        ribbon = kwargs.get("ribbon")
        rwCard = kwargs.get("rwCard")
        if args:
            ribbon_or_rw = args[0]
            if type(ribbon_or_rw) is RibbonType:
                ribbon = ribbon_or_rw
            elif type(ribbon_or_rw) is RwCardType:
                rwCard = ribbon_or_rw
            else:
                raise ValueError(f"Invalid parameter type {type(ribbon_or_rw)}")

        if ribbon is not None:
            self.init_with_ribbon(ribbon)
        elif rwCard is not None:
            self.init_with_rw_card(rwCard)

    def init(self) -> bool:
        """
        Initialize a new printing context. A printing context contains graphics
        (images, text, barcode) and print settings.

        Note: A print context is initialized implicitly for any call to a print
        function if no print context has been opened.

        When you call that function everything is reset: graphics are removed and
        the printing settings are reset to default.

        The following settings will be read from the printer:
        - GPrintingMode: the printer will stay in D2T2 (ribbon) or RW mode unless the
          setting is explicitly changed, even if a ribbon is inserted or removed
        - GRwCard: the printer will use the same type of RW card until that setting is changed
        - GRibbonType: the setting will either be set to the detected ribbon type, or to the
          previous ribbon configuration if detection fails.

        All other settings will be set to a default value according to the printer model
        and the three settings above.

        Note: initializing this way will automatically apply a working configuration
        but is the slowest because it requires exchanging information with the printer
        For a more advanced, but faster initialization see the other init* functions.

        Returns
        -------
        bool
            True on success, false otherwise (need to check `get_last_error()`).
        """
        self.__last_error = ReturnCode.from_int(Evolis.wrapper.evolis_print_init(self.__context))
        return self.__last_error == ReturnCode.OK

    def init_with_ribbon(self, ribbonType: RibbonType) -> bool:
        """
        Initialize a printing context with a given ribbon type to avoid
        communication with the printer.

        This function works the same as `init()`, except no data is
        exchanged with the printer during initialization and the following
        settings are set :
        - GPrintingMode is set to D2T2 (ribbon)
        - GRibbonType is set to the chosen ribbon

        The ribbon can be set to UnknownRibbon to be defined later with
        `set_setting()` but the print execution will fail if the ribbon is not
        set.

        Parameters
        ----------
        ribbonType: RibbonType
            Ribbon type to use to configure printing context.

        Returns
        -------
        bool
            True on success, false otherwise (need to check `get_last_error()`).
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_init_with_ribbon(self.__context, ribbonType.value)
        )
        return self.__last_error == ReturnCode.OK

    def init_with_rw_card(self, ct: RwCardType) -> bool:
        """
        Initialize a printing context with a given rw card type to avoid
        communication with the printer.

        This function works the same as evolis_print_init, except no data is
        exchanged with the printer during initialization and the following settings
        are set :
        - GPrintingMode is set to RW_2IN1
        - GRwCard is set to the chosen type

        Parameters
        ----------
        ct: RwCardType
            Card type to use to configure printing context.

        Returns
        -------
        bool
            True on success, false otherwise (need to check `get_last_error()`).
        """
        self.__last_error = ReturnCode.from_int(Evolis.wrapper.evolis_print_init_with_rw_card(self.__context, ct.value))
        return self.__last_error == ReturnCode.OK

    def init_from_driver_settings(self) -> bool:
        """
        Initialize a context with settings from the driver

        This function works the same as `init()`, except all settings
        are imported from the driver.

        Returns
        -------
        bool
            True on success, false otherwise (need to check `get_last_error()`).
        """
        self.__last_error = rc = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_init_from_driver_settings(self.__context)
        )
        return self.__last_error == ReturnCode.OK

    def set_image(self, card_face: CardFace, path: str) -> bool:
        """
        Set the image path to print. Setting a back bitmap also will impact the value
        of the "Duplex" and "GDuplexType" settings.
        If not defined, "GDuplexType" will be set to the ribbon's default.

        Parameters
        ----------
        path: str
            The path of the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_imagep(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_image_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the image buffer to print. Setting a back bitmap also will impact the value
        of the "Duplex" and "GDuplexType" settings.
        If not defined, "GDuplexType" will be set to the ribbon's default.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.
        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_imageb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def set_black(self, card_face: CardFace, path: str) -> bool:
        """
        Set the bitmap image data to print using the black panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The black panel is controlled through the BBlackManagement and FBlackManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        path: str
            The path of the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_blackp(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_black_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the bitmap image data to print using the black panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The black panel is controlled through the BBlackManagement and FBlackManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_blackb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def set_overlay(self, card_face: CardFace, path: str) -> bool:
        """
        Set the bitmap image data to print using the overlay panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The overlay panel is controlled through the BOverlayManagement and FOverlayManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        path: str
            The path of the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_overlayp(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_overlay_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the bitmap image data to print using the overlay panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The overlay panel is controlled through the BOverlayManagement and FOverlayManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_overlayb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def set_second_overlay(self, card_face: CardFace, path: str) -> bool:
        """
        Set the bitmap image data to print using the second overlay panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The second overlay panel is controlled through the BSecondOverlayManagement and FSecondOverlayManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        path: str
            The path of the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_second_overlayp(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_second_overlay_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the bitmap image data to print using the second overlay panel only.
        The given image must be 1 bit per pixel (1 bit depth).

        The second overlay panel is controlled through the BSecondOverlayManagement and FSecondOverlayManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_second_overlayb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def set_rw_areas(self, card_face: CardFace, path: str) -> bool:
        """
        Set the bitmap image data as a definition of the rewritable areas.
        The given image must be 1 bit per pixel (1 bit depth). A value of 1 indicates
        a rewritable pixel.

        The rewrite area is controlled through the FRwManagement and BRwManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        path: str
            The path of the areas definition image.

        card_face: CardFace
            The face of the card impacted by the areas.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_rw_areasp(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_rw_areas_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the bitmap image data to print using the second overlay panel only.
        The given image must be 1 bit per pixel (1 bit depth). A value of 1 indicates
        a rewritable pixel.

        The rewrite area is controlled through the FRwManagement and BRwManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_rw_areasb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def set_silver(self, card_face: CardFace, path: str) -> bool:
        """
        Set the bitmap image data to print in silver (Avansia Connection only).
        The given image must be 1 bit per pixel (1 bit depth).

        The silver panel is controlled through the BSilverManagement and FSilverManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        path: str
            The path of the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_silverp(self.__context, card_face.value, _instr(path))
        )
        return self.__last_error == ReturnCode.OK

    def set_silver_buffer(self, card_face: CardFace, buffer: bytearray) -> bool:
        """
        Set the bitmap image data to print in silver (Avansia Connection only).
        The given image must be 1 bit per pixel (1 bit depth).

        The silver panel is controlled through the BSilverManagement and FSilverManagement settings.
        This means that this function will fail if the required setting is not
        available for the selected printer.

        Parameters
        ----------
        buffer: bytearray
            Array of bytes that containing the image to print.

        card_face: CardFace
            The face of the card to print the image to.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = ReturnCode.from_int(
            Evolis.wrapper.evolis_print_set_silverb(self.__context, card_face.value, buffer, len(buffer))
        )
        return self.__last_error == ReturnCode.OK

    def get_forced_setting_count(self) -> int:
        """
        Get the forced setting count.
        It can be used to enumerate forced settings of the current print session.

        Returns
        -------
        int
            Returns the number of forced settings.
        """
        self.__last_error = ReturnCode.OK
        return Evolis.wrapper.evolis_print_get_forced_setting_count(self.__context)

    def get_forced_setting_key(self, index: int) -> str:
        """
        Get the forced setting key at a specified index.

        Parameters
        ----------
        index: int
            The index of the forced setting.

        Returns
        -------
        str
            Returns the forced setting name or None if not found.
        """
        self.__last_error = ReturnCode.OK
        return _outstr(Evolis.wrapper.evolis_print_get_forced_setting_key(self.__context, index))

    def get_forced_setting(self, key: str) -> str:
        """
        Get printing forced settings

        Parameters
        ----------
        key: str
            The name of the forced setting.

        Returns
        -------
        str
            Returns the forced setting value or None if not found.
        """
        s = ctypes.c_char_p()
        ps = ctypes.POINTER(ctypes.c_char_p)(s)

        if Evolis.wrapper.evolis_print_get_forced_setting(self.__context, _instr(key), ps):
            self.__last_error = ReturnCode.OK
            return _outstr(s.value)
        else:
            self.__last_error == ReturnCode.EUNDEFINED
            return None

    def set_forced_setting(self, key: str, value: str) -> None:
        """
        Set printing forced settings.

        Parameters
        ----------
        key: str
            forced setting name.

        value: str
            forced setting value.
        """
        self.__last_error = ReturnCode.OK
        Evolis.wrapper.evolis_print_set_forced_setting(self.__context, _instr(key), _instr(value))

    def remove_forced_setting(self, key: str) -> bool:
        """
        Remove the specified printing forced setting.

        Parameters
        ----------
        key: str
            The name of the forced setting.

        Returns
        -------
        bool
            Returns true if successful, false otherwise.
        """
        self.__last_error = ReturnCode.OK
        return Evolis.wrapper.evolis_print_remove_forced_setting(self.__context, _instr(key))

    def export_config(self, path: str, sep: str = "=") -> bool:
        """
        Exports the print configuration. This configuration is generated
        from the content of a print session, with the settings updated to
        match the available resources (images and color profile)

        Forced settings always stay unchanged in the export, even if they
        make the configuration invalid.

        Parameters
        ----------
        path: str
            The file that should be written to.

        sep: str
            The separator between a key and the corresponding value.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        path = _instr(path)
        sep = ctypes.c_char(_instr(sep))
        self.__last_error = ReturnCode.OK
        return Evolis.wrapper.evolis_print_export_config(self.__context, path, sep)

    def get_setting_count(self) -> int:
        """
        Those settings are translated into a configuration for the printer.
        This conversion may imply updating settings to match the provided resources
        (eg: enable Duplex printing automatically if Back images are present)
        Settings may be overwritten by forced settings, which are not counted
        by this function

        Returns
        -------
        int
            Returns the settings count if successful.
        """
        self.__last_error = ReturnCode.OK
        return Evolis.wrapper.evolis_print_get_setting_count(self.__context)

    def get_setting_key(self, index: int) -> SettingKey:
        """
        Get the setting at the given index.
        Setting are ordered by key, so inserting a new setting may change
        the index of already present settings.

        Parameters
        ----------
        index: int
            The index of the key.

        Returns
        -------
        SettingKey
            Returns a SettingKey if successful.
        """
        self.__last_error = ReturnCode.OK
        return SettingKey.from_int(Evolis.wrapper.evolis_print_get_setting_key(self.__context, index))

    def is_setting_valid(self, key: SettingKey) -> bool:
        """
        Indicates if a setting is valid for the print session.

        Parameters
        ----------
        key: SettingKey
            The setting to be checked.

        Returns
        -------
        bool
            Returns true if the setting is valid, false otherwise.
        """
        self.__last_error = ReturnCode.OK
        return Evolis.wrapper.evolis_print_is_setting_valid(self.__context, key.value)

    def get_setting(self, key: SettingKey) -> str:
        """
        Get printing settings.

        Parameters
        ----------
        key: SettingKey
            The setting to get.

        Returns
        -------
        str:
            Returns the string value of the setting.
        """
        s = ctypes.c_char_p()
        ps = ctypes.POINTER(ctypes.c_char_p)(s)

        if Evolis.wrapper.evolis_print_get_setting(self.__context, key.value, ps):
            self.__last_error = ReturnCode.OK
            return _outstr(s.value)
        else:
            self.__last_error == ReturnCode.EUNDEFINED
            return None

    def get_int_setting(self, key: SettingKey) -> int:
        """
        Get printing settings.

        Parameters
        ----------
        key: SettingKey
            The setting to get.

        Returns
        -------
        int
            Returns the integer value of the setting.
        """
        i = ctypes.c_int(0)
        pi = ctypes.byref(i)

        if Evolis.wrapper.evolis_print_get_int_setting(self.__context, key.value, pi):
            self.__last_error = ReturnCode.OK
            return i.value
        else:
            self.__last_error = ReturnCode.EUNDEFINED
            return None

    def get_bool_setting(self, key: SettingKey) -> bool:
        """
        Get printing settings.

        Parameters
        ----------
        key: SettingKey
            The setting to get.

        Returns
        -------
        int
            Returns the boolean value of the setting.
        """
        b = ctypes.c_bool(False)
        pb = ctypes.byref(b)

        if Evolis.wrapper.evolis_print_get_bool_setting(self.__context, key.value, pb):
            self.__last_error = ReturnCode.OK
            return b.value
        else:
            self.__last_error = ReturnCode.EUNDEFINED
            return None

    def set_setting(self, key: SettingKey, value: str) -> bool:
        """
        Sets a setting's value for the printing session. The setting is only
        set if it is valid for the session

        Parameters
        ----------
        key: SettingKey
            The setting to set.

        value: str
            The string value of the setting.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        return Evolis.wrapper.evolis_print_set_setting(self.__context, key.value, _instr(value))

    def set_int_setting(self, key: SettingKey, value: int) -> bool:
        """
        Sets a setting's value for the printing session. The setting is only
        set if it is valid for the session

        Parameters
        ----------
        key: SettingKey
            The setting to set.

        value: int
            The integer value of the setting.

        Returns
        -------
        bool:
            True on success, false otherwise.
        """
        return Evolis.wrapper.evolis_print_set_int_setting(self.__context, key.value, value)

    def set_bool_setting(self, key: SettingKey, value: bool) -> bool:
        """
        Sets a setting's value for the printing session. The setting is only
        set if it is valid for the session

        Parameters
        ----------
        key: SettingKey
            The setting to set.

        value: bool
            The boolean value of the setting.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        return Evolis.wrapper.evolis_print_set_bool_setting(self.__context, key.value, value)

    def remove_setting(self, key: SettingKey) -> bool:
        """
        Remove printing setting.

        Parameters
        ----------
        key: SettingKey
            The setting to remove.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        return Evolis.wrapper.evolis_print_remove_setting(self.__context, key.value)

    def set_auto_eject(self, value: bool) -> bool:
        """
        Set the value of the post-print auto-ejection setting.

        Parameters
        ----------
        value: bool
            False to disable card ejection at end of print, True by default.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        return Evolis.wrapper.evolis_print_set_auto_eject(self.__context, value)

    def get_auto_eject(self) -> bool:
        """
        Get the value of the post-print auto-ejection setting.

        Returns
        -------
        bool
            True if post-print ejection is enabled, False otherwise.
        """
        return Evolis.wrapper.evolis_print_get_auto_eject(self.__context)

    def print(self, timeout: int = Evolis.PRINT_TIMEOUT) -> ReturnCode:
        """
        Starts a printing job.

        Parameters
        ----------
        timeout: int
            Print timeout expressed in milliseconds.

        Returns
        -------
        ReturnCode:
            A code describing the print state.
        """
        self.__last_error = ReturnCode.from_int(Evolis.wrapper.evolis_print_exect(self.__context, timeout))
        return self.__last_error

    def print_to_file(self, path: str) -> ReturnCode:
        """
        Generates the PRN and writes it to path.

        Parameters
        ----------
        path: str
            The path of the file will be created if it does not exist, or the
            file will be overwritten.

        Returns
        -------
        ReturnCode:
            A code describing the print state.
        """
        self.__last_error = ReturnCode.from_int(Evolis.wrapper.evolis_print_to_file(self.__context, _instr(path)))
        return self.__last_error

    def clear_mechanical_errors(self) -> bool:
        """
        Sometimes a mechanical error happens while printing. In this case, the
        printer will not accept any other job.
        Calling this method will help you reset the printer in a ready state.

        Returns
        -------
        bool
            True on success, false otherwise.
        """
        self.__last_error = rc = ReturnCode.from_int(Evolis.wrapper.evolis_clear_mechanical_errors(self.__context))
        return self.__last_error == ReturnCode.OK

    def get_last_error(self) -> ReturnCode:
        """
        Get error generated by last method call.

        Returns
        -------
        ReturnCode:
            The last error occurred.
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

    def get_option_count(self) -> int:
        warn("This method is deprecated, use get_forced_setting_count instead", DeprecationWarning)
        return self.get_forced_setting_count()

    def get_option_key(self, index: int) -> str:
        warn("This method is deprecated, use get_forced_setting instead", DeprecationWarning)
        return self.get_forced_setting_key(index)

    def get_option(self, key: str) -> str:
        warn("This method is deprecated, use get_forced_setting instead", DeprecationWarning)
        return self.get_forced_setting(key)

    def set_option(self, key: str, value: str) -> None:
        warn("This method is deprecated, use set_forced_setting instead", DeprecationWarning)
        return self.set_forced_setting(key, value)

    def remove_option(self, key: str) -> bool:
        warn("This method is deprecated, use remove_forced_setting instead", DeprecationWarning)
        return self.remove_forced_setting(key)

    def export_options(self, path: str, sep: str = "=") -> bool:
        warn("This method is deprecated, use export_config instead", DeprecationWarning)
        return self.export_config(path, sep)
