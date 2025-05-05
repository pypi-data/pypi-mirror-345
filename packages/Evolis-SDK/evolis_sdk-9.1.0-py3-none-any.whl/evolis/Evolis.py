# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes
from typing import List

from evolis.Device import _CDevice
from evolis.Device import Device
from evolis.LogLevel import LogLevel


class Evolis:

    TIMEOUT = 30000
    """
    30s, printer communication timeout.
    """

    PRINT_TIMEOUT = 5 * 60000
    """
    Default timeout value of a print job.
    """

    SESSION_FREE = 0
    """
    Value of session when printer is available.
    """

    SESSION_MANAGE = 1
    """
    Session taken by evoservice.
    """

    SESSION_PRINT = 2
    """
    Session taken when printing.
    """

    SESSION_UI = 3
    """
    Session taken by evomanager.
    """

    SESSION_WAIT = 5000
    """
    5s, a good value to use to reserve the printer.
    """

    SESSION_TIMEOUT = 45
    """
    45s, timeout after which the printer release a session.
    """

    wrapper = None

    @staticmethod
    def set_library_path(path: str) -> None:
        from evolis.CleaningInfo import _CCleaningInfo
        from evolis.LaminatorInfo import _CLaminatorInfo
        from evolis.LaminatorFilmInfo import _CLaminatorFilmInfo
        from evolis.MagSession import _CMagTracks
        from evolis.PrinterInfo import _CPrinterInfo
        from evolis.RibbonInfo import _CRibbonInfo
        from evolis.Status import _CStatus

        # See https://docs.python.org/3/library/ctypes.html#fundamental-data-types.
        Evolis.wrapper = ctypes.CDLL(path)

        Evolis.wrapper.evolis_bezel_get_behavior.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_bezel_get_behavior.restype = ctypes.c_int

        Evolis.wrapper.evolis_bezel_get_delay.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_bezel_get_delay.restype = ctypes.c_int

        Evolis.wrapper.evolis_bezel_get_offset.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_bezel_get_offset.restype = ctypes.c_int

        Evolis.wrapper.evolis_bezel_set_behavior.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_bezel_set_behavior.restype = ctypes.c_int

        Evolis.wrapper.evolis_bezel_set_delay.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_bezel_set_delay.restype = ctypes.c_int

        Evolis.wrapper.evolis_bezel_set_offset.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_bezel_set_offset.restype = ctypes.c_int

        Evolis.wrapper.evolis_clear_mechanical_errors.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_clear_mechanical_errors.restype = ctypes.c_int

        Evolis.wrapper.evolis_close.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_close.restype = None

        Evolis.wrapper.evolis_commandt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
        Evolis.wrapper.evolis_commandt.restype = ctypes.c_int

        Evolis.wrapper.evolis_eject.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_eject.restype = ctypes.c_int

        Evolis.wrapper.evolis_firmware_update.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        Evolis.wrapper.evolis_firmware_update.restype = ctypes.c_int

        Evolis.wrapper.evolis_firmware_updateb.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        Evolis.wrapper.evolis_firmware_updateb.restype = ctypes.c_int

        Evolis.wrapper.evolis_firmware_updatebt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
        Evolis.wrapper.evolis_firmware_updatebt.restype = ctypes.c_int

        Evolis.wrapper.evolis_firmware_updatet.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_firmware_updatet.restype = ctypes.c_int

        Evolis.wrapper.evolis_free_devices.argtypes = [ctypes.POINTER(_CDevice)]
        Evolis.wrapper.evolis_free_devices.restype = None

        Evolis.wrapper.evolis_get_cleaning.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CCleaningInfo)]
        Evolis.wrapper.evolis_get_cleaning.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_error_management.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_error_management.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_error_tray.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_error_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_feeder.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_feeder.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CPrinterInfo)]
        Evolis.wrapper.evolis_get_info.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_input_tray.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_input_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_open_mode.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_open_mode.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_output_tray.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_output_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_retransfer_film.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CRibbonInfo)]
        Evolis.wrapper.evolis_get_retransfer_film.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_ribbon.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CRibbonInfo)]
        Evolis.wrapper.evolis_get_ribbon.restype = ctypes.c_int

        Evolis.wrapper.evolis_get_session_management.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_get_session_management.restype = ctypes.c_bool

        Evolis.wrapper.evolis_get_state.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_get_state.restype = ctypes.c_int

        Evolis.wrapper.evolis_insert.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_insert.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_enable_parallel_mode.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        Evolis.wrapper.evolis_laminator_enable_parallel_mode.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_enable_parallel_modet.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_enable_parallel_modet.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_film.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_CLaminatorFilmInfo)]
        Evolis.wrapper.evolis_laminator_film.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_filmt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_CLaminatorFilmInfo), ctypes.c_int]
        Evolis.wrapper.evolis_laminator_filmt.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_info.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_CLaminatorInfo)]
        Evolis.wrapper.evolis_laminator_info.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_infot.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_CLaminatorInfo), ctypes.c_int]
        Evolis.wrapper.evolis_laminator_infot.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_is_parallel_mode_enabled.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        Evolis.wrapper.evolis_laminator_is_parallel_mode_enabled.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_is_parallel_mode_enabledt.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool), ctypes.c_int]
        Evolis.wrapper.evolis_laminator_is_parallel_mode_enabledt.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_is_valid.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_is_valid.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_is_validt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_is_validt.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_first_patch.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]
        Evolis.wrapper.evolis_laminator_set_first_patch.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_first_patcht.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_set_first_patcht.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_mode.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_set_mode.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_modet.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_set_modet.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_speed_cfg.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint16]
        Evolis.wrapper.evolis_laminator_set_speed_cfg.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_speed_cfgt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint16, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_set_speed_cfgt.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_temp_cfg.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint16]
        Evolis.wrapper.evolis_laminator_set_temp_cfg.restype = ctypes.c_int

        Evolis.wrapper.evolis_laminator_set_temp_cfgt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint16, ctypes.c_int]
        Evolis.wrapper.evolis_laminator_set_temp_cfgt.restype = ctypes.c_int

        Evolis.wrapper.evolis_log_set_console.argtypes = [ctypes.c_bool]
        Evolis.wrapper.evolis_log_set_console.restype = None

        Evolis.wrapper.evolis_log_set_level.argtypes = [ctypes.c_int]
        Evolis.wrapper.evolis_log_set_level.restype = None

        Evolis.wrapper.evolis_log_set_path.argtypes = [ctypes.c_char_p]
        Evolis.wrapper.evolis_log_set_path.restype = None

        Evolis.wrapper.evolis_mag_init.argtypes = [ctypes.POINTER(_CMagTracks)]
        Evolis.wrapper.evolis_mag_init.restype = None

        Evolis.wrapper.evolis_mag_read.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CMagTracks)]
        Evolis.wrapper.evolis_mag_read.restype = ctypes.c_int

        Evolis.wrapper.evolis_mag_read_tracks.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CMagTracks), ctypes.c_bool, ctypes.c_bool, ctypes.c_bool]
        Evolis.wrapper.evolis_mag_read_tracks.restype = ctypes.c_int

        Evolis.wrapper.evolis_mag_write.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CMagTracks)]
        Evolis.wrapper.evolis_mag_write.restype = ctypes.c_int

        Evolis.wrapper.evolis_open.argtypes = [ctypes.c_char_p]
        Evolis.wrapper.evolis_open.restype = ctypes.c_void_p

        Evolis.wrapper.evolis_open_with_mode.argtypes = [ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_open_with_mode.restype = ctypes.c_void_p

        Evolis.wrapper.evolis_print_exect.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_exect.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_export_config.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char]
        Evolis.wrapper.evolis_print_export_config.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_auto_eject.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_get_auto_eject.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_bool_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_bool)]
        Evolis.wrapper.evolis_print_get_bool_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_forced_setting.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        Evolis.wrapper.evolis_print_get_forced_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_forced_setting_count.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_get_forced_setting_count.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_get_int_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_print_get_int_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_prn_size.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_get_prn_size.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_get_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
        Evolis.wrapper.evolis_print_get_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_get_setting_count.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_get_setting_count.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_get_setting_key.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_get_setting_key.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_init.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_init.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_init_from_driver_settings.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_print_init_from_driver_settings.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_init_with_ribbon.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_init_with_ribbon.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_init_with_rw_card.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_init_with_rw_card.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_is_setting_valid.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_is_setting_valid.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_remove_forced_setting.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_remove_forced_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_remove_setting.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_remove_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_set_auto_eject.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        Evolis.wrapper.evolis_print_set_auto_eject.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_set_blackp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_blackp.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_bool_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]
        Evolis.wrapper.evolis_print_set_bool_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_set_forced_setting.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_forced_setting.restype = None

        Evolis.wrapper.evolis_print_set_imagep.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_imagep.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_int_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_int_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_set_overlayp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_overlayp.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_prnlog.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_prnlog.restype = None

        Evolis.wrapper.evolis_print_set_rw_areasp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_rw_areasp.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_second_overlayp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_second_overlayp.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_setting.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_setting.restype = ctypes.c_bool

        Evolis.wrapper.evolis_print_set_silverp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_set_silverp.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_test_card.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_test_card.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_to_buffer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        Evolis.wrapper.evolis_print_to_buffer.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_to_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        Evolis.wrapper.evolis_print_to_file.restype = ctypes.c_int

        Evolis.wrapper.evolis_readt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
        Evolis.wrapper.evolis_readt.restype = ctypes.c_int

        Evolis.wrapper.evolis_reject.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_reject.restype = ctypes.c_int

        Evolis.wrapper.evolis_release.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_release.restype = ctypes.c_int

        Evolis.wrapper.evolis_reserve.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_reserve.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_acquire.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_scan_acquire.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_command.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
        Evolis.wrapper.evolis_scan_command.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_firmware_update.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        Evolis.wrapper.evolis_scan_firmware_update.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_get_image.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_scan_get_image.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_get_library_path.argtypes = []
        Evolis.wrapper.evolis_scan_get_library_path.restype = ctypes.c_char_p

        Evolis.wrapper.evolis_scan_get_option.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_scan_get_option.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_init.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_scan_init.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_save_image.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_scan_save_image.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_set_library_path.argtypes = [ctypes.c_char_p]
        Evolis.wrapper.evolis_scan_set_library_path.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_set_option.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_scan_set_option.restype = ctypes.c_int

        Evolis.wrapper.evolis_service_get_printer_event.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        Evolis.wrapper.evolis_service_get_printer_event.restype = ctypes.c_int

        Evolis.wrapper.evolis_service_is_action_available.argtypes = [ctypes.c_int, ctypes.c_int]
        Evolis.wrapper.evolis_service_is_action_available.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_is_running.argtypes = []
        Evolis.wrapper.evolis_service_is_running.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_restart.argtypes = []
        Evolis.wrapper.evolis_service_restart.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_select.argtypes = [ctypes.c_int]
        Evolis.wrapper.evolis_service_select.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_select_with_url.argtypes = [ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_service_select_with_url.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_set_printer_event.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_service_set_printer_event.restype = ctypes.c_int

        Evolis.wrapper.evolis_service_start.argtypes = []
        Evolis.wrapper.evolis_service_start.restype = ctypes.c_bool

        Evolis.wrapper.evolis_service_stop.argtypes = []
        Evolis.wrapper.evolis_service_stop.restype = ctypes.c_bool

        Evolis.wrapper.evolis_set_card_pos.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_card_pos.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_error_management.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_error_management.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_error_tray.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_error_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_feeder.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_feeder.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_input_tray.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_input_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_output_tray.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_set_output_tray.restype = ctypes.c_int

        Evolis.wrapper.evolis_set_session_management.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        Evolis.wrapper.evolis_set_session_management.restype = None

        Evolis.wrapper.evolis_status.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CStatus)]
        Evolis.wrapper.evolis_status.restype = ctypes.c_int

        Evolis.wrapper.evolis_status_enable.argtypes = [ctypes.c_void_p]
        Evolis.wrapper.evolis_status_enable.restype = ctypes.c_int

        Evolis.wrapper.evolis_status_is_on.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_cfg.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_cfg.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_err.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_err.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_ex1.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_ex1.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_ex2.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_ex2.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_ex3.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_ex3.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_inf.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_inf.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_is_on_war.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_int]
        Evolis.wrapper.evolis_status_is_on_war.restype = ctypes.c_bool

        Evolis.wrapper.evolis_status_send_request.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CStatus)]
        Evolis.wrapper.evolis_status_send_request.restype = ctypes.c_int

        Evolis.wrapper.evolis_status_to_string.argtypes = [ctypes.POINTER(_CStatus), ctypes.c_char_p, ctypes.c_size_t]
        Evolis.wrapper.evolis_status_to_string.restype = ctypes.c_size_t

        Evolis.wrapper.evolis_version.argtypes = []
        Evolis.wrapper.evolis_version.restype = ctypes.c_char_p

        Evolis.wrapper.evolis_writet.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
        Evolis.wrapper.evolis_writet.restype = ctypes.c_int


        #
        # Hard coded wrappers :
        #

        Evolis.wrapper.evolis_get_devices.argtypes = [ctypes.POINTER(ctypes.POINTER(_CDevice)), ctypes.c_int]
        Evolis.wrapper.evolis_get_devices.restype = ctypes.c_int

        Evolis.wrapper.evolis_mag_set_track.argtypes = [ctypes.POINTER(_CMagTracks), ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        Evolis.wrapper.evolis_mag_set_track.restype = None

        Evolis.wrapper.evolis_print_get_forced_setting_key.argtypes = [ctypes.c_void_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_get_forced_setting_key.restype = ctypes.c_char_p

        Evolis.wrapper.evolis_print_set_blackb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_blackb.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_imageb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_imageb.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_overlayb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_overlayb.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_silverb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_silverb.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_second_overlayb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_second_overlayb.restype = ctypes.c_int

        Evolis.wrapper.evolis_print_set_rw_areasb.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        Evolis.wrapper.evolis_print_set_rw_areasb.restype = ctypes.c_int

        Evolis.wrapper.evolis_reset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_bool)]
        Evolis.wrapper.evolis_reset.restype = ctypes.c_int

        Evolis.wrapper.evolis_scan_get_image.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        Evolis.wrapper.evolis_scan_get_image.restype = ctypes.c_int

    @staticmethod
    def get_version() -> str:
        """
        Returns underlying library version.

        Results
        --------
        str:
            A string describing libevolis version.
        """
        return str(Evolis.wrapper.evolis_version(), "ascii")

    @staticmethod
    def set_log_level(level: LogLevel) -> None:
        """
        Configure the global log level of underlying library.

        Parameters
        --------
        level: LogLevel
            The level to set.
        """
        Evolis.wrapper.evolis_log_set_level(level.value)

    @staticmethod
    def set_log_path(path: str) -> None:
        """
        Can be used to set log output to a file.

        Parameters
        --------
        path: str
            The file where log messages are sent.
        """
        Evolis.wrapper.evolis_log_set_path(path.encode())

    @staticmethod
    def set_console_output(on: bool) -> None:
        """
        If true, log messages are sent to `std::clog` (or LogCat on Android).

        Parameters
        --------
        on: bool
            True to enable, false otherwise.
        """
        Evolis.wrapper.evolis_log_set_console(on)

    @staticmethod
    def get_devices() -> List[Device]:
        """
        Returns a list of Evolis devices installed on the system.
        On Android, USB devices can be listed with this function.

        Returns
        --------
        list[Device]
            An array containing list of devices.
        """
        c_device = ctypes.POINTER(_CDevice)()
        result = []
        rc = Evolis.wrapper.evolis_get_devices(ctypes.byref(c_device), 0)
        if rc > 0:
            for i in range(rc):
                result.append(Device(c_device[i]))
            Evolis.wrapper.evolis_free_devices(c_device)
        return result
