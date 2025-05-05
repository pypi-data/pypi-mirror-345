# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class RibbonType(Enum):
    """
    List of ribbons accepted by Evolis printers.
    """

    def from_int(n:int):
        try:
            return RibbonType(n)
        except ValueError:
            return RibbonType.UNKNOWN

    UNKNOWN = -1
    YMCKO = 0
    YMCKOS = 3
    YMCKOS13 = 5
    YMCKOK = 4
    YMCKOKS13 = 9
    YMCKOKOS = 10
    YMCKOO = 13
    KO = 1
    KBLACK = 100
    KWHITE = 105
    KRED = 103
    KGREEN = 102
    KBLUE = 101
    KSCRATCH = 108
    KMETALSILVER = 107
    KMETALGOLD = 106
    KSIGNATURE = 114
    KWAX = 112
    KPREMIUM = 115
    KRMS = 116
    HOLO = 91
    SOKO = 12
    YMCFK = 1002
    YMCK = 1000
    YMCKS = 1050
    YMCKH = 1003
    YMCKI = 1004
    YMCKK = 1001
    YMCKKS = 1051
    YMCKKI = 1005
    KBLACK_R = 1100
    CLEAR = 2000
