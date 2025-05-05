# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class Model(Enum):
    """
    References the model of the printer.
    """

    def from_int(v:int):
        try:
            return Model(v)
        except ValueError:
            return Model.INVALID

    INVALID = 0
    Evolis_KC100 = 1
    Evolis_KC100B = 2
    Evolis_KC200 = 3
    Evolis_KC200B = 4
    Evolis_KM500B = 5
    Evolis_KM2000B = 6
    Evolis_Primacy = 7
    Evolis_Altess = 8
    Evolis_Altess_Elite = 9
    BadgePass_Connect = 10
    BadgePass_NXT5000 = 11
    ID_Maker_Primacy = 12
    Evolis_Elypso = 13
    ID_Maker_Elypso = 14
    Evolis_Zenius = 15
    ID_Maker_Zenius = 16
    ATC_ATC300 = 17
    Evolis_Apteo = 18
    BadgePass_Connect_Lite = 19
    Durable_Duracard_ID_300 = 20
    Edikio_Access = 21
    Edikio_Flex = 22
    Edikio_Duplex = 23
    Evolis_Badgy100 = 24
    Evolis_Badgy200 = 25
    Bodno_Badgy100X = 26
    Bodno_Badgy200X = 27
    Evolis_Lamination_Module = 28
    Evolis_KC_Essential = 29
    Evolis_KC_Prime = 30
    ATC_ATC310 = 31
    Evolis_KC_Max = 32
    Evolis_Primacy_2 = 33
    Evolis_Asmi = 34
    BadgePass_NXTElite = 35
    BadgePass_CONNECTplus = 36
    ID_Maker_Primacy_Infinity = 37
    Plasco_Primacy_2_LE = 38
    Identisys_Primacy_2_SE = 39
    BRAVO_DC_3300 = 40
    Evolis_EPX300 = 41
    Evolis_Avansia = 42
    Evolis_Agilia = 43
    ATC_ATC600 = 44
    Evolis_Quantum2 = 45
