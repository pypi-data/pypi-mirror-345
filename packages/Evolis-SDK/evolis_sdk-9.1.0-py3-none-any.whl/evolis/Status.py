# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import ctypes

from enum import Enum
from evolis.Evolis import Evolis

from warnings import warn

class _CStatus(ctypes.Structure):
    _fields_ = [
        ("config", ctypes.c_uint32),
        ("information", ctypes.c_uint32),
        ("warning", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
        ("exts", ctypes.c_uint32 * 4),
        ("session", ctypes.c_uint16),
    ]

class Status:
    """
    Printer status flags.
    """

    class Flag(Enum):
        CFG_X01 = 0
        """Raised for Primacy, KC200B, KC200, Issengo, KC Prime, KC Essential, KC max"""

        CFG_X02 = 1
        """Raised for Zenius"""

        CFG_R02 = 2
        """Raised for Agilia"""

        CFG_X04 = 3
        """Raised for Elypso"""

        CFG_EXTENSION_1 = 4
        """Extension 1 is used"""

        CFG_S01 = 5
        """Raised for Badgy, Apteo"""

        CFG_X07 = 6
        """Not used"""

        CFG_KC200 = 7
        """Raised for KC200B, KC200"""

        CFG_WIFI = 8
        """WiFi option is detected"""

        CFG_ETHERNET = 9
        """Ethernet option is detected"""

        CFG_USB_OVER_IP = 10
        """USB over IP option is set"""

        CFG_FLIP = 11
        """Flip-over option is detected"""

        CFG_CONTACTLESS = 12
        """Contactless option is detected"""

        CFG_SMART = 13
        """Smart option is detected"""

        CFG_MAGNETIC = 14
        """Magnetic option is detected"""

        CFG_REWRITE = 15
        """Rewrite mode is activated"""

        CFG_FEED_MANUALLY = 16
        """Card feeding is configured as manual"""

        CFG_FEED_BY_CDE = 17
        """Card feeding is set as manual once the feeding command is received"""

        CFG_FEED_BY_FEEDER = 18
        """Card feeding is configured as feeder"""

        CFG_EJECT_REVERSE = 19
        """Card ejection goes to manual feeder"""

        CFG_FEED_CDE_REVERSE = 20
        """Card insertion is set to the rear of the printer"""

        CFG_EXTENDED_RESOLUTION = 21
        """Extended resolution supported (600DPI, 1200DPI)"""

        CFG_LCD = 22
        """LCD option detected"""

        CFG_LOCK = 23
        """Locking system detected"""

        CFG_OEM = 24
        """Raised for rebranded products"""

        CFG_JIS_MAG_HEAD = 25
        """JIS magnetic option detected"""

        CFG_REJECT_SLOT = 26
        """Reject slot enabled"""

        CFG_IO_EXT = 27
        """IO extender detected"""

        CFG_MONO_ONLY = 28
        """Monochrome only printing authorized"""

        CFG_KC100 = 29
        """Raised for KC100"""

        CFG_KINE = 30
        """Kineclipse option is available"""

        CFG_WIFI_ENA = 31
        """WiFi option is activated"""

        CFG_EXTENSION_2 = 32
        """Extension 2 is used"""

        CFG_KIOSK = 33
        """Raised for KM500B, KM2000B"""

        CFG_QUANTUM = 34
        """Raised for Quantum"""

        CFG_SECURION = 35
        """Raised for Securion"""

        CFG_DUALYS = 36
        """Raised for Dualys"""

        CFG_PEBBLE = 37
        """Raised for Pebble"""

        CFG_SCANNER = 38
        """Scanner option is detected"""

        CFG_MEM_LAMINATION_MODULE_2 = 39
        """Printer has previously seen 2 lamination modules simultaneously"""

        CFG_SEICO_FEEDER = 40
        """Seico feeder configured"""

        CFG_KYTRONIC_FEEDER = 41
        """Kytronics feeder configured"""

        CFG_HOPPER = 42
        """Not used"""

        CFG_LAMINATOR = 43
        """Lamination module detected"""

        CFG_BEZEL = 44
        """Bezel option installed"""

        CFG_EXTENSION_3 = 45
        """Extension 3 is used"""

        CFG_LAMINATION_MODULE_2 = 46
        """Second lamination module detected"""

        CFG_EXTENSION_4 = 47
        """Extension 4 is used"""

        CFG_BRIDGE = 48
        """Configuration for bridge module"""

        CFG_INDENTING = 49
        """Configuration for indenting module"""

        INF_CLAIM = 50
        """Raised when EPS printing"""

        INF_CARD_HOPPER = 51
        """Card present at the hopper"""

        INF_CARD_FEEDER = 52
        """Card present in the feeder"""

        INF_CARD_FLIP = 53
        """Card present in the flip-over"""

        INF_CARD_CONTACTLESS = 54
        """Card present in contactless card station"""

        INF_CARD_SMART = 55
        """Card present in smart card station"""

        INF_CARD_PRINT = 56
        """Card present in printing position"""

        INF_CARD_EJECT = 57
        """Card present in eject position"""

        INF_PRINTER_MASTER = 58
        """Error management is set to 'printer'"""

        INF_PCSVC_LOCKED = 59
        """The EPS is supervising the printer"""

        INF_SLEEP_MODE = 60
        """Printer is in sleep mode"""

        INF_UNKNOWN_RIBBON = 61
        """Installed ribbon is unknown/unreadable"""

        INF_RIBBON_LOW = 62
        """Remaining ribbon is below low limit"""

        INF_CLEANING_MANDATORY = 63
        """Cleaning is mandatory"""

        INF_CLEANING = 64
        """Cleaning is recommended"""

        INF_RESET = 65
        """Printer has just rebooted"""

        INF_CLEAN_OUTWARRANTY = 66
        """Warranty lost, cleaning has not been done in time"""

        INF_CLEAN_LAST_OUTWARRANTY = 67
        """Cleaning is mandatory, next card printed will lose the warranty"""

        INF_CLEAN_2ND_PASS = 68
        """Cleaning sequence requires the second cleaning card"""

        INF_READY_FOR_CLEANING = 69
        """Printer ready for cleaning (ribbon has been removed and cover closed)"""

        INF_CLEANING_ADVANCED = 70
        """Advanced cleaning requested"""

        INF_WRONG_ZONE_RIBBON = 71
        """Installed ribbon has not the right zone"""

        INF_RIBBON_CHANGED = 72
        """Installed ribbon is different from the previous one"""

        INF_CLEANING_REQUIRED = 73
        """Cleaning is required"""

        INF_PRINTING_RUNNING = 74
        """Printing is in progress"""

        INF_ENCODING_RUNNING = 75
        """Encoding is in progress (smart, contactless or magnetic)"""

        INF_CLEANING_RUNNING = 76
        """Cleaning is in progress"""

        INF_WRONG_ZONE_ALERT = 77
        """Installed ribbon has wrong zone, there are only a few prints remaining before printing is blocked"""

        INF_WRONG_ZONE_EXPIRED = 78
        """Installed ribbon has wrong zone, printing is not allowed"""

        INF_SYNCH_PRINT_CENTER = 79
        """Raised by EPS during a pop-up"""

        INF_UPDATING_FIRMWARE = 80
        """Firmware is currently downloading"""

        INF_BUSY = 81
        """The printer is busy (printing, encoding)"""

        INF_NO_LAMINATION_TO_DO = 82
        """Lamination module is set to 'pass through' mode"""

        INF_LAMI_ALLOW_TO_INSERT = 83
        """Lamination module ready to insert card"""

        INF_LAMINATING_RUNNING = 84
        """Lamination process is running"""

        INF_CLEAN_REMINDER = 85
        """Reminder to clean the laminator"""

        INF_LAMI_TEMP_NOT_READY = 86
        """Lamination roller is heating up, but its temperature is currently too low for the lamination process"""

        INF_SYNCHRONOUS_MODE = 87
        """Lamination process is set to synchronous"""

        INF_LCD_BUT_ACK = 88
        """LCD pop up button acknowledged"""

        INF_LCD_BUT_OK = 89
        """LCD pop up OK button pressed"""

        INF_LCD_BUT_RETRY = 90
        """LCD pop up Retry button pressed"""

        INF_LCD_BUT_CANCEL = 91
        """LCD pop up Cancel button pressed"""

        INF_FEEDER_NEAR_EMPTY = 92
        """Feeder is near empty (low level sensor)"""

        INF_FEEDER1_EMPTY = 93
        """Feeder 1 is empty for KM2000B"""

        INF_FEEDER2_EMPTY = 94
        """Feeder 2 is empty for KM2000B"""

        INF_FEEDER3_EMPTY = 95
        """Feeder 3 is empty for KM2000B"""

        INF_FEEDER4_EMPTY = 96
        """Feeder 4 is empty for KM2000B"""

        INF_FEEDER1_NEAR_EMPTY = 97
        """Feeder 1 is near empty for KM2000B"""

        INF_FEEDER2_NEAR_EMPTY = 98
        """Feeder 2 is near empty for KM2000B"""

        INF_FEEDER3_NEAR_EMPTY = 99
        """Feeder 3 is near empty for KM2000B"""

        INF_FEEDER4_NEAR_EMPTY = 100
        """Feeder 4 is near empty for KM2000B"""

        INF_SA_PROCESSING = 101
        """Sensor adjustment is running"""

        INF_SCP_PROCESSING = 102
        """Cleaning sequence is running"""

        INF_OPT_PROCESSING = 103
        """Option activation is running (with activation key)"""

        INF_X08_PRINTER_UNLOCKED = 104
        """Lock system currently unlocked"""

        INF_X08_FEEDER_OPEN = 105
        """Feeder cover is open (used with locking system)"""

        INF_X08_EJECTBOX_FULL = 106
        """Locking system feeder eject box full"""

        INF_X08_PRINT_UNLOCKED = 107
        """Printing is currently unlocked, both mechanically and firmware-wise"""

        INF_LAMINATE_UNKNOWN = 108
        """Installed laminate film is unknown/unreadable"""

        INF_LAMINATE_LOW = 109
        """Laminate film is close to its end"""

        INF_LAMI_CARD = 110
        """Card present in the lamination module"""

        INF_LAMI_CLEANING_RUNNING = 111
        """Lamination module cleaning process is running"""

        INF_LAMI_UPDATING_FIRMWARE = 112
        """Lamination module firmware update is running"""

        INF_LAMI_READY_FOR_CLEANING = 113
        """Lamination module ready for cleaning (no laminate film and cover closed)"""

        INF_CARD_REAR = 114
        """Card present at the rear of the printer"""

        INF_CLEAR_UNKNOWN = 115
        """Installed clear ribbon is unknown"""

        INF_CLEAR_LOW = 116
        """Remaining clear ribbon is below the low limit"""

        INF_WRONG_ZONE_CLEAR = 117
        """Installed clear ribbon has not the right zone"""

        INF_CLEAR_CHANGED = 118
        """Installed clear ribbon is different from the previous one"""

        INF_WRONG_ZONE_CLEAR_ALERT = 119
        """Installed clear ribbon has wrong zone: only a few prints remaining before printing is blocked"""

        INF_WRONG_ZONE_CLEAR_EXPIRED = 120
        """Installed clear ribbon has wrong zone: printing not allowed"""

        INF_RETRANSFER_RUNNING = 121
        """Retransfer sequence is running"""

        INF_HEATING = 122
        """Printer is heating up"""

        INF_RX_COM_ALIVE = 123
        """Internal communication with Rx co-processor is alive"""

        INF_CARD_MAN_FEED = 124
        """Card present in the manual feeding module"""

        INF_HEAT_ROLLER_WORN_OUT = 125
        """Heat roller reached its maximum recommended of retransfers"""

        INF_ETH_CONF_CHANGED = 126
        """Ethernet configuration has been changed by the user from the LCD touchscreen"""

        INF_CARD_BRIDGE = 127
        """The card is located in the bridge module"""

        INF_CARD_INDENTING = 128
        """The card is located in the indenting module"""

        INF_BRIDGE_UPDATING_FIRMWARE = 129
        """Bridge module firmware update is running"""

        INF_CASSETTE_PRESENCE = 130
        """Internal K7 is inserted into feeder"""

        INF_FLASHDRIVE_COPY = 131
        """Printer log file copy in progress"""

        WAR_POWER_SUPPLY = 132
        """Power supply voltage is too low"""

        WAR_REMOVE_RIBBON = 133
        """Ribbon must be removed (in rewrite mode)"""

        WAR_RECEPTACLE_OPEN = 134
        """Not used"""

        WAR_REJECT_BOX_FULL = 135
        """Reject box is full"""

        WAR_CARD_ON_EJECT = 136
        """Card in eject position and has to be removed (in manual insertion mode)"""

        WAR_WAIT_CARD = 137
        """Printer is waiting for manual card insertion"""

        WAR_FEEDER_EMPTY = 138
        """Feeder is empty"""

        WAR_COOLING = 139
        """Print head temperature too high: cooling down"""

        WAR_HOPPER_FULL = 140
        """Printer hopper is full"""

        WAR_RIBBON_ENDED = 141
        """Installed ribbon reached its end"""

        WAR_PRINTER_LOCKED = 142
        """Printer is locked (used with locking system)"""

        WAR_COVER_OPEN = 143
        """Printer cover is opened"""

        WAR_NO_RIBBON = 144
        """No ribbon detected in the printer"""

        WAR_UNSUPPORTED_RIBBON = 145
        """Installed ribbon is not supported by the printer"""

        WAR_NO_CLEAR = 146
        """No clear ribbon installed"""

        WAR_CLEAR_END = 147
        """Clear ribbon reached its end"""

        WAR_CLEAR_UNSUPPORTED = 148
        """Installed clear ribbon is not supported by the printer"""

        WAR_REJECT_BOX_COVER_OPEN = 149
        """Reject box cover is open"""

        WAR_EPS_NO_AUTO = 150
        """For tagless ribbons, indicates to the EPS to not automatically set the ribbon"""

        WAR_FEEDER_OPEN = 151
        """Printer feeder is opened"""

        WAR_NO_LAMINATE = 152
        """No laminate film installed"""

        WAR_LAMI_COVER_OPEN = 153
        """Lamination module cover is open"""

        WAR_LAMINATE_END = 154
        """Laminate film reached its end"""

        WAR_LAMI_HOPPER_FULL = 155
        """Lamination module hopper is full"""

        WAR_LAMINATE_UNSUPPORTED = 156
        """Installed laminate film is not supported"""

        WAR_REJECT_BOX_ALMOST_FULL = 157
        """Reject box is almost full"""

        ERR_HEAD_TEMP = 158
        """Job interrupted because the print head temperature was too high"""

        ERR_NO_OPTION = 159
        """Requested option is not available"""

        ERR_FEEDER_ERROR = 160
        """Error while feeding a card"""

        ERR_RIBBON_ERROR = 161
        """Ribbon error during printing"""

        ERR_COVER_OPEN = 162
        """Job interrupted by an open cover"""

        ERR_MECHANICAL = 163
        """Mechanical error (card jam, ribbon jam, ...)"""

        ERR_REJECT_BOX_FULL = 164
        """Card sent to reject box but it was full"""

        ERR_BAD_RIBBON = 165
        """Job interrupted because the installed ribbon is not the one expected"""

        ERR_RIBBON_ENDED = 166
        """Job interrupted because the ribbon is finished"""

        ERR_HOPPER_FULL = 167
        """Card sent to hopper but it was full"""

        ERR_BLANK_TRACK = 168
        """No data on track after magnetic reading"""

        ERR_MAGNETIC_DATA = 169
        """Magnetic data is not matching the settings"""

        ERR_READ_MAGNETIC = 170
        """Corrupted/absent data on track after magnetic reading"""

        ERR_WRITE_MAGNETIC = 171
        """Corrupted/absent data on track after magnetic encoding"""

        ERR_FEATURE = 172
        """Job sent is not supported by the printer"""

        ERR_RET_TEMPERATURE = 173
        """Retransfer roller couldn't reach its operating temperature in time"""

        ERR_CLEAR_ERROR = 174
        """Clear ribbon error during printing"""

        ERR_CLEAR_ENDED = 175
        """Job interrupted because the clear ribbon is finished"""

        ERR_BAD_CLEAR = 176
        """Job interrupted because the installed clear ribbon is not the one expected"""

        ERR_REJECT_BOX_COVER_OPEN = 177
        """Card sent to reject box but its cover was open"""

        ERR_CARD_ON_EJECT = 178
        """Card in eject position was not removed in time (in manual insertion mode)"""

        ERR_NO_CARD_INSERTED = 179
        """No card was presented in time (in manual insertion mode)"""

        ERR_FEEDER_OPEN = 180
        """Job interrupted because the printer feeder is opened"""

        ERR_INTERNAL_PRINTER = 181
        """Internal error detected in in addition to ERR_MECHANICAL_ERROR"""

        ERR_LAMI_TEMPERATURE = 182
        """Job interrupted because the laminator temperature was too high"""

        ERR_LAMINATE = 183
        """Error on the laminate film"""

        ERR_LAMI_MECHANICAL = 184
        """Mechanical error on the lamination module (card jam, ribbon jam, ...)"""

        ERR_LAMINATE_END = 185
        """Job interrupted because the laminate film is finished"""

        ERR_LAMI_COVER_OPEN = 186
        """Job interrupted by an open lamination module cover"""

        RSV_WAR_0X20000000 = 187
        """Reserved flag WAR:0x20000000"""

        RSV_WAR_0X00800000 = 188
        """Reserved flag WAR:0x00800000"""

        RSV_WAR_0X00400000 = 189
        """Reserved flag WAR:0x00400000"""

        RSV_WAR_0X00004000 = 190
        """Reserved flag WAR:0x00004000"""

        RSV_WAR_0X00000080 = 191
        """Reserved flag WAR:0x00000080"""

        RSV_WAR_0X00000040 = 192
        """Reserved flag WAR:0x00000040"""

        RSV_WAR_0X00000020 = 193
        """Reserved flag WAR:0x00000020"""

        RSV_WAR_0X00000010 = 194
        """Reserved flag WAR:0x00000010"""

        RSV_WAR_0X00000008 = 195
        """Reserved flag WAR:0x00000008"""

        RSV_WAR_0X00000004 = 196
        """Reserved flag WAR:0x00000004"""

        RSV_WAR_0X00000002 = 197
        """Reserved flag WAR:0x00000002"""

        RSV_WAR_0X00000001 = 198
        """Reserved flag WAR:0x00000001"""

        RSV_ERR_0X80000000 = 199
        """Reserved flag ERR:0x80000000"""

        RSV_ERR_0X40000000 = 200
        """Reserved flag ERR:0x40000000"""

        RSV_ERR_0X00000020 = 201
        """Reserved flag ERR:0x00000020"""

        RSV_ERR_0X00000010 = 202
        """Reserved flag ERR:0x00000010"""

        RSV_ERR_0X00000008 = 203
        """Reserved flag ERR:0x00000008"""

        RSV_ERR_0X00000004 = 204
        """Reserved flag ERR:0x00000004"""

        RSV_ERR_0X00000002 = 205
        """Reserved flag ERR:0x00000002"""

        RSV_ERR_0X00000001 = 206
        """Reserved flag ERR:0x00000001"""

        RSV_EX3_0X01000000 = 207
        """Reserved flag EX3:0x01000000"""

        RSV_EX3_0X00800000 = 208
        """Reserved flag EX3:0x00800000"""

        RSV_EX3_0X00400000 = 209
        """Reserved flag EX3:0x00400000"""

        RSV_EX3_0X00200000 = 210
        """Reserved flag EX3:0x00200000"""

        RSV_EX3_0X00100000 = 211
        """Reserved flag EX3:0x00100000"""

        RSV_EX3_0X00080000 = 212
        """Reserved flag EX3:0x00080000"""

        RSV_EX3_0X00040000 = 213
        """Reserved flag EX3:0x00040000"""

        RSV_EX3_0X00020000 = 214
        """Reserved flag EX3:0x00020000"""

        RSV_EX3_0X00010000 = 215
        """Reserved flag EX3:0x00010000"""

        RSV_EX3_0X00008000 = 216
        """Reserved flag EX3:0x00008000"""

        RSV_EX3_0X00004000 = 217
        """Reserved flag EX3:0x00004000"""

        RSV_EX3_0X00002000 = 218
        """Reserved flag EX3:0x00002000"""

        RSV_EX3_0X00001000 = 219
        """Reserved flag EX3:0x00001000"""

        RSV_EX3_0X00000800 = 220
        """Reserved flag EX3:0x00000800"""

        RSV_EX3_0X00000400 = 221
        """Reserved flag EX3:0x00000400"""

        RSV_EX3_0X00000200 = 222
        """Reserved flag EX3:0x00000200"""

        RSV_EX3_0X00000100 = 223
        """Reserved flag EX3:0x00000100"""


    class CfgFlag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        CFG_X01 = 0
        CFG_X02 = 1
        CFG_R02 = 2
        CFG_X04 = 3
        CFG_EXTENSION_1 = 4
        CFG_S01 = 5
        CFG_X07 = 6
        CFG_KC200 = 7
        CFG_WIFI = 8
        CFG_ETHERNET = 9
        CFG_USB_OVER_IP = 10
        CFG_FLIP = 11
        CFG_CONTACTLESS = 12
        CFG_SMART = 13
        CFG_MAGNETIC = 14
        CFG_REWRITE = 15
        CFG_FEED_MANUALLY = 16
        CFG_FEED_BY_CDE = 17
        CFG_FEED_BY_FEEDER = 18
        CFG_EJECT_REVERSE = 19
        CFG_FEED_CDE_REVERSE = 20
        CFG_EXTENDED_RESOLUTION = 21
        CFG_LCD = 22
        CFG_LOCK = 23
        CFG_OEM = 24
        CFG_JIS_MAG_HEAD = 25
        CFG_REJECT_SLOT = 26
        CFG_IO_EXT = 27
        CFG_MONO_ONLY = 28
        CFG_KC100 = 29
        CFG_KINE = 30
        CFG_WIFI_ENA = 31


    class InfFlag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        INF_CLAIM = 50
        INF_CARD_HOPPER = 51
        INF_CARD_FEEDER = 52
        INF_CARD_FLIP = 53
        INF_CARD_CONTACTLESS = 54
        INF_CARD_SMART = 55
        INF_CARD_PRINT = 56
        INF_CARD_EJECT = 57
        INF_PRINTER_MASTER = 58
        INF_PCSVC_LOCKED = 59
        INF_SLEEP_MODE = 60
        INF_UNKNOWN_RIBBON = 61
        INF_RIBBON_LOW = 62
        INF_CLEANING_MANDATORY = 63
        INF_CLEANING = 64
        INF_RESET = 65
        INF_CLEAN_OUTWARRANTY = 66
        INF_CLEAN_LAST_OUTWARRANTY = 67
        INF_CLEAN_2ND_PASS = 68
        INF_READY_FOR_CLEANING = 69
        INF_CLEANING_ADVANCED = 70
        INF_WRONG_ZONE_RIBBON = 71
        INF_RIBBON_CHANGED = 72
        INF_CLEANING_REQUIRED = 73
        INF_PRINTING_RUNNING = 74
        INF_ENCODING_RUNNING = 75
        INF_CLEANING_RUNNING = 76
        INF_WRONG_ZONE_ALERT = 77
        INF_WRONG_ZONE_EXPIRED = 78
        INF_SYNCH_PRINT_CENTER = 79
        INF_UPDATING_FIRMWARE = 80
        INF_BUSY = 81


    class WarFlag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        WAR_POWER_SUPPLY = 132
        WAR_REMOVE_RIBBON = 133
        WAR_RECEPTACLE_OPEN = 134
        WAR_REJECT_BOX_FULL = 135
        WAR_CARD_ON_EJECT = 136
        WAR_WAIT_CARD = 137
        WAR_FEEDER_EMPTY = 138
        WAR_COOLING = 139
        WAR_HOPPER_FULL = 140
        WAR_RIBBON_ENDED = 141
        WAR_PRINTER_LOCKED = 142
        WAR_COVER_OPEN = 143
        WAR_NO_RIBBON = 144
        WAR_UNSUPPORTED_RIBBON = 145
        WAR_NO_CLEAR = 146
        WAR_CLEAR_END = 147
        WAR_CLEAR_UNSUPPORTED = 148
        WAR_REJECT_BOX_COVER_OPEN = 149
        WAR_EPS_NO_AUTO = 150
        WAR_FEEDER_OPEN = 151
        RSV_WAR_0X20000000 = 187
        RSV_WAR_0X00800000 = 188
        RSV_WAR_0X00400000 = 189
        RSV_WAR_0X00004000 = 190
        RSV_WAR_0X00000080 = 191
        RSV_WAR_0X00000040 = 192
        RSV_WAR_0X00000020 = 193
        RSV_WAR_0X00000010 = 194
        RSV_WAR_0X00000008 = 195
        RSV_WAR_0X00000004 = 196
        RSV_WAR_0X00000002 = 197
        RSV_WAR_0X00000001 = 198


    class ErrFlag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        ERR_HEAD_TEMP = 158
        ERR_NO_OPTION = 159
        ERR_FEEDER_ERROR = 160
        ERR_RIBBON_ERROR = 161
        ERR_COVER_OPEN = 162
        ERR_MECHANICAL = 163
        ERR_REJECT_BOX_FULL = 164
        ERR_BAD_RIBBON = 165
        ERR_RIBBON_ENDED = 166
        ERR_HOPPER_FULL = 167
        ERR_BLANK_TRACK = 168
        ERR_MAGNETIC_DATA = 169
        ERR_READ_MAGNETIC = 170
        ERR_WRITE_MAGNETIC = 171
        ERR_FEATURE = 172
        ERR_RET_TEMPERATURE = 173
        ERR_CLEAR_ERROR = 174
        ERR_CLEAR_ENDED = 175
        ERR_BAD_CLEAR = 176
        ERR_REJECT_BOX_COVER_OPEN = 177
        ERR_CARD_ON_EJECT = 178
        ERR_NO_CARD_INSERTED = 179
        ERR_FEEDER_OPEN = 180
        ERR_INTERNAL_PRINTER = 181
        RSV_ERR_0X80000000 = 199
        RSV_ERR_0X40000000 = 200
        RSV_ERR_0X00000020 = 201
        RSV_ERR_0X00000010 = 202
        RSV_ERR_0X00000008 = 203
        RSV_ERR_0X00000004 = 204
        RSV_ERR_0X00000002 = 205
        RSV_ERR_0X00000001 = 206


    class Ex1Flag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        EX1_CFG_EXTENSION_2 = 0x80000000,
        EX1_CFG_KIOSK = 0x40000000,
        EX1_CFG_QUANTUM = 0x20000000,
        EX1_CFG_SECURION = 0x10000000,
        EX1_CFG_DUALYS = 0x08000000,
        EX1_CFG_PEBBLE = 0x04000000,
        EX1_CFG_SCANNER = 0x02000000,
        EX1_CFG_MEM_LAMINATION_MODULE_2 = 0x01000000,
        EX1_INF_NO_LAMINATION_TO_DO = 0x00800000,
        EX1_CFG_SEICO_FEEDER = 0x00400000,
        EX1_CFG_KYTRONIC_FEEDER = 0x00200000,
        EX1_CFG_HOPPER = 0x00100000,
        EX1_CFG_LAMINATOR = 0x00080000,
        EX1_INF_LAMI_ALLOW_TO_INSERT = 0x00040000,
        EX1_INF_LAMINATING_RUNNING = 0x00020000,
        EX1_INF_CLEAN_REMINDER = 0x00010000,
        EX1_INF_LAMI_TEMP_NOT_READY = 0x00008000,
        EX1_INF_SYNCHRONOUS_MODE = 0x00004000,
        EX1_INF_LCD_BUT_ACK = 0x00002000,
        EX1_INF_LCD_BUT_OK = 0x00001000,
        EX1_INF_LCD_BUT_RETRY = 0x00000800,
        EX1_INF_LCD_BUT_CANCEL = 0x00000400,
        EX1_CFG_BEZEL = 0x00000200,
        EX1_INF_FEEDER_NEAR_EMPTY = 0x00000100,
        EX1_INF_FEEDER1_EMPTY = 0x00000080,
        EX1_INF_FEEDER2_EMPTY = 0x00000040,
        EX1_INF_FEEDER3_EMPTY = 0x00000020,
        EX1_INF_FEEDER4_EMPTY = 0x00000010,
        EX1_INF_FEEDER1_NEAR_EMPTY = 0x00000008,
        EX1_INF_FEEDER2_NEAR_EMPTY = 0x00000004,
        EX1_INF_FEEDER3_NEAR_EMPTY = 0x00000002,
        EX1_INF_FEEDER4_NEAR_EMPTY = 0x00000001;


    class Ex2Flag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        EX2_CFG_EXTENSION_3 = 0x80000000,
        EX2_INF_SA_PROCESSING = 0x40000000,
        EX2_INF_SCP_PROCESSING = 0x20000000,
        EX2_INF_OPT_PROCESSING = 0x10000000,
        EX2_INF_X08_PRINTER_UNLOCKED = 0x08000000,
        EX2_INF_X08_FEEDER_OPEN = 0x04000000,
        EX2_INF_X08_EJECTBOX_FULL = 0x02000000,
        EX2_INF_X08_PRINT_UNLOCKED = 0x01000000,
        EX2_CFG_LAMINATION_MODULE_2 = 0x00800000,
        EX2_INF_LAMINATE_UNKNOWN = 0x00400000,
        EX2_INF_LAMINATE_LOW = 0x00200000,
        EX2_INF_LAMI_CARD = 0x00100000,
        EX2_INF_LAMI_CLEANING_RUNNING = 0x00080000,
        EX2_INF_LAMI_UPDATING_FIRMWARE = 0x00040000,
        EX2_INF_LAMI_READY_FOR_CLEANING = 0x00020000,
        EX2_INF_CARD_REAR = 0x00010000,
        EX2_DEF_NO_LAMINATE = 0x00008000,
        EX2_DEF_LAMI_COVER_OPEN = 0x00004000,
        EX2_DEF_LAMINATE_END = 0x00002000,
        EX2_DEF_LAMI_HOPPER_FULL = 0x00001000,
        EX2_DEF_LAMINATE_UNSUPPORTED = 0x00000800,
        EX2_INF_CLEAR_UNKNOWN = 0x00000400,
        EX2_INF_CLEAR_LOW = 0x00000200,
        EX2_INF_WRONG_ZONE_CLEAR = 0x00000100,
        EX2_ERR_LAMI_TEMPERATURE = 0x00000080,
        EX2_ERR_LAMINATE = 0x00000040,
        EX2_ERR_LAMI_MECHANICAL = 0x00000020,
        EX2_ERR_LAMINATE_END = 0x00000010,
        EX2_ERR_LAMI_COVER_OPEN = 0x00000008,
        EX2_INF_CLEAR_CHANGED = 0x00000004,
        EX2_INF_WRONG_ZONE_CLEAR_ALERT = 0x00000002,
        EX2_INF_WRONG_ZONE_CLEAR_EXPIRED = 0x00000001;


    class Ex3Flag(Enum):
        """
        Deprecated, please use Status.Flag enum instead.
        """
        EX3_CFG_EXTENSION_4 = 0x80000000,
        EX3_INF_RETRANSFER_RUNNING = 0x40000000,
        EX3_INF_HEATING = 0x20000000,
        EX3_INF_RX_COM_ALIVE = 0x10000000,
        EX3_INF_CARD_MAN_FEED = 0x08000000,
        EX3_INF_HEAT_ROLLER_WORN_OUT = 0x04000000,
        EX3_INF_ETH_CONF_CHANGED = 0x02000000,
        EX3_RSV_EX3_0X01000000 = 0x01000000,
        EX3_RSV_EX3_0X00800000 = 0x00800000,
        EX3_RSV_EX3_0X00400000 = 0x00400000,
        EX3_RSV_EX3_0X00200000 = 0x00200000,
        EX3_RSV_EX3_0X00100000 = 0x00100000,
        EX3_RSV_EX3_0X00080000 = 0x00080000,
        EX3_RSV_EX3_0X00040000 = 0x00040000,
        EX3_RSV_EX3_0X00020000 = 0x00020000,
        EX3_RSV_EX3_0X00010000 = 0x00010000,
        EX3_RSV_EX3_0X00008000 = 0x00008000,
        EX3_RSV_EX3_0X00004000 = 0x00004000,
        EX3_RSV_EX3_0X00002000 = 0x00002000,
        EX3_RSV_EX3_0X00001000 = 0x00001000,
        EX3_RSV_EX3_0X00000800 = 0x00000800,
        EX3_RSV_EX3_0X00000400 = 0x00000400,
        EX3_RSV_EX3_0X00000200 = 0x00000200,
        EX3_RSV_EX3_0X00000100 = 0x00000100,
        EX3_CFG_BRIDGE = 0x00000080,
        EX3_INF_CARD_BRIDGE = 0x00000040,
        EX3_CFG_INDENTING = 0x00000020,
        EX3_INF_CARD_INDENTING = 0x00000010,
        EX3_INF_BRIDGE_UPDATING_FIRMWARE = 0x00000008,
        EX3_DEF_REJECT_BOX_ALMOST_FULL = 0x00000004,
        EX3_INF_CASSETTE_PRESENCE = 0x00000002,
        EX3_INF_FLASHDRIVE_COPY = 0x00000001;

    def __init__(self, c_status: _CStatus):
        self.__data = c_status
        self.config = int(c_status.config)
        self.information = int(c_status.information)
        self.warning = int(c_status.warning)
        self.error = int(c_status.error)
        self.exts = [
            int(c_status.exts[0]),
            int(c_status.exts[1]),
            int(c_status.exts[2]),
            int(c_status.exts[3]),
        ]
        self.session = int(c_status.session)

    def is_on(self, flag) -> bool:
        if type(flag) == Status.Flag:
            return Evolis.wrapper.evolis_status_is_on(self.__data, flag.value)
        if type(flag) == Status.CfgFlag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_cfg(self.__data, flag.value)
        if type(flag) == Status.InfFlag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_inf(self.__data, flag.value)
        if type(flag) == Status.WarFlag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_war(self.__data, flag.value)
        if type(flag) == Status.ErrFlag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_err(self.__data, flag.value)
        if type(flag) == Status.Ex1Flag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_ex1(self.__data, flag.value)
        if type(flag) == Status.Ex2Flag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_ex2(self.__data, flag.value)
        if type(flag) == Status.Ex3Flag:
            warn("This enum is deprecated, use Status.Flag instead", DeprecationWarning)
            return Evolis.wrapper.evolis_status_is_on_ex3(self.__data, flag.value)
        return False


    def is_session_free(self):
        return self.session == 0

    def is_session_busy(self):
        return not self.is_session_free()

    def to_string(self) -> str:
        """
        Serialize status struct as string.
        """
        outSize = 128
        out = ctypes.create_string_buffer(outSize)
        n = Evolis.wrapper.evolis_status_to_string(self.__data, out, outSize)
        return out.raw[:n].decode()

    def active_flags(self) -> list:
        l = []

        for flags in [Status.CfgFlag, Status.InfFlag, Status.WarFlag, Status.ErrFlag]:
            for e in flags:
                if self.is_on(e):
                    l.append(e)
        return l

