# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class SettingKey(Enum):

    @staticmethod
    def from_int(v: int):
        try:
            return SettingKey(v)
        except ValueError:
            return SettingKey.Unknown

    Unknown = 0

    BBlackManagement = 1
    """
    BBlackManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOBLACKPOINT, ALLBLACKPOINT, TEXTINBLACK, BMPBLACK
    """

    BColorBrightness = 2
    """
    BColorBrightness
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BColorContrast = 3
    """
    BColorContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BDualDeposite = 4
    """
    BDualDeposite
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    BHalftoning = 5
    """
    BHalftoning
    Usable in PrintSessions: true
    Type: LIST
    Possible values: THRESHOLD, FLOYD, DITHERING, CLUSTERED_DITHERING
    """

    BMonochromeContrast = 6
    """
    BMonochromeContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BOverlayContrast = 7
    """
    BOverlayContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BOverlayManagement = 8
    """
    BOverlayManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOVARNISH, FULLVARNISH, BMPVARNISH
    """

    BOverlaySecondManagement = 9
    """
    BOverlaySecondManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOVARNISH, FULLVARNISH, BMPVARNISH
    """

    BPageRotate180 = 10
    """
    BPageRotate180
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    BRwErasingSpeed = 11
    """
    BRwErasingSpeed
    Usable in PrintSessions: true
    Type: INT
    Range: 1-10
    """

    BRwErasingTemperature = 12
    """
    BRwErasingTemperature
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BRwManagement = 13
    """
    BRwManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: WRITEONLY, FULLREWRITE, BMPREWRITE
    """

    BRwPrintingSpeed = 14
    """
    BRwPrintingSpeed
    Usable in PrintSessions: true
    Type: INT
    Range: 1-10
    """

    BRwPrintingTemperature = 15
    """
    BRwPrintingTemperature
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BUvBrightness = 16
    """
    BUvBrightness
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BUvContrast = 17
    """
    BUvContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    BUvManagement = 18
    """
    BUvManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOUV, BMPUV
    """

    BUvPremium = 19
    """
    BUvPremium
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    Duplex = 20
    """
    Duplex
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NONE, HORIZONTAL
    """

    FBlackManagement = 21
    """
    FBlackManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOBLACKPOINT, ALLBLACKPOINT, TEXTINBLACK, BMPBLACK
    """

    FColorBrightness = 22
    """
    FColorBrightness
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FColorContrast = 23
    """
    FColorContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FDualDeposite = 24
    """
    FDualDeposite
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    FHalftoning = 25
    """
    FHalftoning
    Usable in PrintSessions: true
    Type: LIST
    Possible values: THRESHOLD, FLOYD, DITHERING, CLUSTERED_DITHERING
    """

    FMonochromeContrast = 26
    """
    FMonochromeContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FOverlayContrast = 27
    """
    FOverlayContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FOverlayManagement = 28
    """
    FOverlayManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOVARNISH, FULLVARNISH, BMPVARNISH
    """

    FOverlaySecondManagement = 29
    """
    FOverlaySecondManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOVARNISH, FULLVARNISH, BMPVARNISH
    """

    FPageRotate180 = 30
    """
    FPageRotate180
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    FRwErasingSpeed = 31
    """
    FRwErasingSpeed
    Usable in PrintSessions: true
    Type: INT
    Range: 1-10
    """

    FRwErasingTemperature = 32
    """
    FRwErasingTemperature
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FRwManagement = 33
    """
    FRwManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: WRITEONLY, FULLREWRITE, BMPREWRITE
    """

    FRwPrintingSpeed = 34
    """
    FRwPrintingSpeed
    Usable in PrintSessions: true
    Type: INT
    Range: 1-10
    """

    FRwPrintingTemperature = 35
    """
    FRwPrintingTemperature
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FUvBrightness = 36
    """
    FUvBrightness
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FUvContrast = 37
    """
    FUvContrast
    Usable in PrintSessions: true
    Type: INT
    Range: 1-20
    """

    FUvManagement = 38
    """
    FUvManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOUV, BMPUV
    """

    FUvPremium = 39
    """
    FUvPremium
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    GCardPreloading = 40
    """
    GCardPreloading
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    GDigitalScrambling = 41
    """
    GDigitalScrambling
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    GDuplexType = 42
    """
    GDuplexType
    Usable in PrintSessions: true
    Type: LIST
    Possible values: DUPLEX_CC, DUPLEX_CM, DUPLEX_MC, DUPLEX_MM
    """

    GFeederCfg = 43
    """
    GFeederCfg
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PRINTER, AUTO, FEEDERA, FEEDERB, FEEDERC, FEEDERD, ALTERNATE, FEEDER1, FEEDER2, FEEDER3, FEEDER4, NONE
    """

    GFeederPos = 44
    """
    GFeederPos
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PRINTER, FEEDERA, FEEDERB, FEEDERC, FEEDERD, MIDDLE, OFF
    """

    GHighQualityMode = 45
    """
    GHighQualityMode
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    GInputTray = 46
    """
    GInputTray
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PRINTER, FEEDER, AUTO, MANUAL, HOPPER, BEZEL
    """

    GMagCoercivity = 47
    """
    GMagCoercivity
    Usable in PrintSessions: true
    Type: LIST
    Possible values: OFF, LOCO, HICO
    """

    GMagT1Encoding = 48
    """
    GMagT1Encoding
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ISO1, ISO2, ISO3, SIPASS, C2, JIS2, C4, NONE
    """

    GMagT2Encoding = 49
    """
    GMagT2Encoding
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ISO1, ISO2, ISO3, SIPASS, C2, JIS2, C4, NONE
    """

    GMagT3Encoding = 50
    """
    GMagT3Encoding
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ISO1, ISO2, ISO3, SIPASS, C2, JIS2, C4, NONE
    """

    GOutputTray = 51
    """
    GOutputTray
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PRINTER, HOPPER, REAR, MANUAL, REJECT, BEZEL
    """

    GPipeDetection = 52
    """
    GPipeDetection
    Usable in PrintSessions: true
    Type: LIST
    Possible values: OFF, DEFAULT, CUSTOM
    """

    GRejectBox = 53
    """
    GRejectBox
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PRINTER, DEFAULTREJECT, HOPPER, MANUAL, REJECT, BEZEL
    """

    GRibbonType = 54
    """
    GRibbonType
    Usable in PrintSessions: true
    Type: LIST
    Possible values: RC_YMCKI, RC_YMCKKI, RC_YMCFK, RC_YMCK, RC_YMCKK, RC_YMCKO, RC_YMCKOS, RC_YMCKOS13, RC_YMCKOK, RC_YMCKOKS13, RC_YMCKOKOS, RC_YMCKOO, RM_KO, RM_KBLACK, RM_KWHITE, RM_KRED, RM_KGREEN, RM_KBLUE, RM_KSCRATCH, RM_KMETALSILVER, RM_KMETALGOLD, RM_KSIGNATURE, RM_KWAX, RM_KPREMIUM, RM_HOLO, RM_SOKO, RC_YMCK_A, RC_YMCKK_A, RC_YMCKI_A, RC_YMCKH_A, RC_YMCFK_A, RC_YMCKSI_A, RM_KBLACK_R
    """

    GRwCard = 55
    """
    GRwCard
    Usable in PrintSessions: true
    Type: LIST
    Possible values: MBLACK, MBLUE, CUSTOM_FRONT, CUSTOM_DUPLEX
    """

    GPrintingMode = 56
    """
    GPrintingMode
    Usable in PrintSessions: true
    Type: LIST
    Possible values: D2T2, RW_2IN1
    """

    GShortPanelManagement = 57
    """
    GShortPanelManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: AUTO, CUSTOM, OFF
    """

    GSmoothing = 58
    """
    GSmoothing
    Usable in PrintSessions: true
    Type: LIST
    Possible values: STDSMOOTH, ADVSMOOTH, NOSMOOTH
    """

    IBBlackCustom = 59
    """
    IBBlackCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBBlackLevelValue = 60
    """
    IBBlackLevelValue
    Usable in PrintSessions: true
    Type: INT
    Range: 1-255
    """

    IBDarkLevelValue = 61
    """
    IBDarkLevelValue
    Usable in PrintSessions: true
    Type: INT
    Range: 0-255
    """

    IBNoTransferAreas = 62
    """
    IBNoTransferAreas
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBOverlayCustom = 63
    """
    IBOverlayCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBOverlayDefaultContent = 64
    """
    IBOverlayDefaultContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IBOverlaySecondCustom = 65
    """
    IBOverlaySecondCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBOverlaySecondDefaultContent = 66
    """
    IBOverlaySecondDefaultContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IBRegionPrintingMode = 67
    """
    IBRegionPrintingMode
    Usable in PrintSessions: true
    Type: LIST
    Possible values: RESIN, BLACK_COMPOSITE
    """

    IBRwCustom = 68
    """
    IBRwCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBRwCustomBitmap = 69
    """
    IBRwCustomBitmap
    Usable in PrintSessions: false
    Type: BLOB
    """

    IBTextRegion = 70
    """
    IBTextRegion
    Usable in PrintSessions: true
    Type: TEXT
    """

    IBThresholdValue = 71
    """
    IBThresholdValue
    Usable in PrintSessions: true
    Type: INT
    Range: 1-255
    """

    IBUvContent = 72
    """
    IBUvContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IBUvCustom = 73
    """
    IBUvCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFBlackCustom = 74
    """
    IFBlackCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFBlackLevelValue = 75
    """
    IFBlackLevelValue
    Usable in PrintSessions: true
    Type: INT
    Range: 1-255
    """

    IFDarkLevelValue = 76
    """
    IFDarkLevelValue
    Usable in PrintSessions: true
    Type: INT
    Range: 0-255
    """

    IFNoTransferAreas = 77
    """
    IFNoTransferAreas
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFOverlayCustom = 78
    """
    IFOverlayCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFOverlayDefaultContent = 79
    """
    IFOverlayDefaultContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IFOverlaySecondCustom = 80
    """
    IFOverlaySecondCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFOverlaySecondDefaultContent = 81
    """
    IFOverlaySecondDefaultContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IFRegionPrintingMode = 82
    """
    IFRegionPrintingMode
    Usable in PrintSessions: true
    Type: LIST
    Possible values: RESIN, BLACK_COMPOSITE
    """

    IFRwCustom = 83
    """
    IFRwCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFRwCustomBitmap = 84
    """
    IFRwCustomBitmap
    Usable in PrintSessions: false
    Type: BLOB
    """

    IFTextRegion = 85
    """
    IFTextRegion
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFUvContent = 86
    """
    IFUvContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    IFUvCustom = 87
    """
    IFUvCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IFThresholdValue = 88
    """
    IFThresholdValue
    Usable in PrintSessions: true
    Type: INT
    Range: 1-255
    """

    IGBlackSub = 89
    """
    IGBlackSub
    Usable in PrintSessions: true
    Type: TEXT
    """

    IGDuplexPreset = 90
    """
    IGDuplexPreset
    Usable in PrintSessions: false
    Type: INT
    Range: 0-99
    """

    IGIQLABC = 91
    """
    IGIQLABC
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGIQLABM = 92
    """
    IGIQLABM
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGIQLABY = 93
    """
    IGIQLABY
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGIQLACC = 94
    """
    IGIQLACC
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGIQLACM = 95
    """
    IGIQLACM
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGIQLACY = 96
    """
    IGIQLACY
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IGMonoReaderType = 97
    """
    IGMonoReaderType
    Usable in PrintSessions: false
    Type: LIST
    Possible values: REG, FILE
    """

    IGMonochromeSpeed = 98
    """
    IGMonochromeSpeed
    Usable in PrintSessions: true
    Type: INT
    Range: 1-10
    """

    IGRegionOrientation = 99
    """
    IGRegionOrientation
    Usable in PrintSessions: true
    Type: LIST
    Possible values: LANDSCAPE, PORTRAIT
    """

    IGRibbonOptimization = 100
    """
    IGRibbonOptimization
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    IGSendIQLA = 101
    """
    IGSendIQLA
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    IGSendSpoolerSession = 102
    """
    IGSendSpoolerSession
    Usable in PrintSessions: false
    Type: LIST
    Possible values: ON, OFF
    """

    IGDisableAutoEject = 103
    """
    IGDisableAutoEject
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    IGStrictPageSetup = 104
    """
    IGStrictPageSetup
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    IGTextRectErr = 105
    """
    IGTextRectErr
    Usable in PrintSessions: true
    Type: INT
    Range: 0-20
    """

    IOverlayCustomContentAfnor = 106
    """
    IOverlayCustomContentAfnor
    Usable in PrintSessions: false
    Type: BLOB
    """

    IOverlayCustomContentIso = 107
    """
    IOverlayCustomContentIso
    Usable in PrintSessions: false
    Type: BLOB
    """

    IOverlayCustomContentMag = 108
    """
    IOverlayCustomContentMag
    Usable in PrintSessions: false
    Type: BLOB
    """

    IPipeDefinition = 109
    """
    IPipeDefinition
    Usable in PrintSessions: false
    Type: TEXT
    """

    IPostSmoothing = 110
    """
    IPostSmoothing
    Usable in PrintSessions: true
    Type: LIST
    Possible values: STDSMOOTH, ADVSMOOTH, NOSMOOTH
    """

    ISendBlankPanel = 111
    """
    ISendBlankPanel
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    IShortPanelShift = 112
    """
    IShortPanelShift
    Usable in PrintSessions: true
    Type: INT
    Range: 0-9999
    """

    Orientation = 113
    """
    Orientation
    Usable in PrintSessions: true
    Type: LIST
    Possible values: LANDSCAPE_CC90, PORTRAIT
    """

    RawData = 114
    """
    RawData
    Usable in PrintSessions: false
    Type: TEXT
    """

    Resolution = 115
    """
    Resolution
    Usable in PrintSessions: true
    Type: LIST
    Possible values: DPI300260, DPI300, DPI600300, DPI600, DPI1200300
    """

    Track1Data = 116
    """
    Track1Data
    Usable in PrintSessions: false
    Type: TEXT
    """

    Track2Data = 117
    """
    Track2Data
    Usable in PrintSessions: false
    Type: TEXT
    """

    Track3Data = 118
    """
    Track3Data
    Usable in PrintSessions: false
    Type: TEXT
    """

    PrinterIsManaged = 119
    """
    PrinterIsManaged
    Usable in PrintSessions: false
    Type: INT
    Range: 0-1
    """

    srvAddress = 120
    """
    srvAddress
    Usable in PrintSessions: false
    Type: TEXT
    """

    UIMagTrackSettingMode = 121
    """
    UIMagTrackSettingMode
    Usable in PrintSessions: false
    Type: INT
    Range: 0-1
    """

    UIRibbonMode = 122
    """
    UIRibbonMode
    Usable in PrintSessions: false
    Type: INT
    Range: 0-1
    """

    UpdatedByDrv = 123
    """
    UpdatedByDrv
    Usable in PrintSessions: false
    Type: INT
    Range: 0-1
    """

    UpdatedBySrv = 124
    """
    UpdatedBySrv
    Usable in PrintSessions: false
    Type: INT
    Range: 0-1
    """

    GColorProfileMode = 125
    """
    GColorProfileMode
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOPROFILE, DRIVERPROFILE, CUSTOM
    """

    GColorProfile = 126
    """
    GColorProfile
    Usable in PrintSessions: true
    Type: LIST
    Possible values: STDPROFILE
    """

    GColorProfileRendering = 127
    """
    GColorProfileRendering
    Usable in PrintSessions: true
    Type: LIST
    Possible values: PERCEPTUAL, SATURATION
    """

    IGColorProfileCustom = 128
    """
    IGColorProfileCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    IGColorProfileContent = 129
    """
    IGColorProfileContent
    Usable in PrintSessions: false
    Type: BLOB
    """

    UIColorProfileName = 130
    """
    UIColorProfileName
    Usable in PrintSessions: false
    Type: TEXT
    """

    WIScanImageDepth = 131
    """
    WIScanImageDepth
    Usable in PrintSessions: false
    Type: LIST
    Possible values: BPP8, BPP16, BPP24, BPP32
    """

    WIScanImageResolution = 132
    """
    WIScanImageResolution
    Usable in PrintSessions: false
    Type: LIST
    Possible values: DPI300, DPI600
    """

    WIScanImageFileFormat = 133
    """
    WIScanImageFileFormat
    Usable in PrintSessions: false
    Type: LIST
    Possible values: JPG, BMP, PNG
    """

    WIScanSpeed = 134
    """
    WIScanSpeed
    Usable in PrintSessions: false
    Type: INT
    Range: 0-40
    """

    WIScanOffset = 135
    """
    WIScanOffset
    Usable in PrintSessions: false
    Type: INT
    Range: 0-40
    """

    WIScanCardSides = 136
    """
    WIScanCardSides
    Usable in PrintSessions: false
    Type: LIST
    Possible values: FRONT_BACK, FRONT_ONLY, BACK_ONLY
    """

    passthrough = 137
    """
    passthrough
    Usable in PrintSessions: false
    Type: TEXT
    """

    PaperSize = 138
    """
    PaperSize
    Usable in PrintSessions: true
    Type: LIST
    Possible values: CR80, ISOCR80, CR120X50, CR150X50, AVANSIACR80
    """

    FGamma = 139
    """
    FGamma
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    FGammaFactor = 140
    """
    FGammaFactor
    Usable in PrintSessions: true
    Type: INT
    Range: 0-100
    """

    BGamma = 141
    """
    BGamma
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    BGammaFactor = 142
    """
    BGammaFactor
    Usable in PrintSessions: true
    Type: INT
    Range: 0-100
    """

    FBlackPrinting = 143
    """
    FBlackPrinting
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    BBlackPrinting = 144
    """
    BBlackPrinting
    Usable in PrintSessions: true
    Type: LIST
    Possible values: ON, OFF
    """

    FSilverManagement = 145
    """
    FSilverManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOSILVER
    """

    IFSilverCustom = 146
    """
    IFSilverCustom
    Usable in PrintSessions: true
    Type: TEXT
    """

    BSilverManagement = 147
    """
    BSilverManagement
    Usable in PrintSessions: true
    Type: LIST
    Possible values: NOSILVER
    """

    IBSilverCustom = 148
    """
    IBSilverCustom
    Usable in PrintSessions: true
    Type: TEXT
    """


