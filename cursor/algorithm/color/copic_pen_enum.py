from enum import Enum, auto


class CopicColorCode(Enum):
    _110 = auto()
    _000 = auto()  # actually doesnt exist, this is white

    # Blue-Violet
    BV0000 = auto()
    BV04 = auto()
    BV11 = auto()
    BV20 = auto()
    BV31 = auto()
    BV34 = auto()

    # Violet
    V09 = auto()
    V12 = auto()
    V17 = auto()
    V15 = auto()
    V20 = auto()
    V91 = auto()
    V99 = auto()

    # Red-Violet
    RV06 = auto()
    RV09 = auto()
    RV11 = auto()
    RV13 = auto()
    RV19 = auto()
    RV29 = auto()
    RV63 = auto()
    RV93 = auto()

    # Red
    R00 = auto()
    R01 = auto()
    R02 = auto()
    R05 = auto()
    R08 = auto()
    R11 = auto()
    R12 = auto()
    R14 = auto()
    R17 = auto()
    R20 = auto()
    R21 = auto()
    R22 = auto()
    R24 = auto()
    R27 = auto()
    R29 = auto()
    R30 = auto()
    R32 = auto()
    R35 = auto()
    R37 = auto()
    R39 = auto()
    R43 = auto()
    R46 = auto()
    R56 = auto()
    R59 = auto()
    R81 = auto()
    R83 = auto()
    R85 = auto()
    R89 = auto()
    FRV1 = auto()

    # Yellow-Red
    YR01 = auto()
    YR02 = auto()
    YR04 = auto()
    YR07 = auto()
    YR12 = auto()
    YR18 = auto()
    YR23 = auto()
    YR24 = auto()
    YR68 = auto()

    # Yellow
    Y00 = auto()
    Y02 = auto()
    Y04 = auto()
    Y06 = auto()
    Y08 = auto()
    Y11 = auto()
    Y13 = auto()
    Y15 = auto()
    Y17 = auto()
    Y18 = auto()
    Y19 = auto()
    Y21 = auto()
    Y23 = auto()
    Y26 = auto()
    Y28 = auto()
    Y32 = auto()
    Y35 = auto()
    Y38 = auto()

    # Yellow-Green
    YG01 = auto()
    YG05 = auto()
    YG11 = auto()
    YG21 = auto()
    YG25 = auto()
    YG45 = auto()
    YG67 = auto()
    YG91 = auto()
    FYG2 = auto()

    # Green
    G00 = auto()
    G02 = auto()
    G03 = auto()
    G05 = auto()
    G07 = auto()
    G09 = auto()
    G12 = auto()
    G14 = auto()
    G16 = auto()
    G17 = auto()
    G19 = auto()
    G20 = auto()
    G21 = auto()
    G24 = auto()
    G28 = auto()
    G29 = auto()
    G40 = auto()
    G43 = auto()
    G46 = auto()
    G82 = auto()
    G85 = auto()
    G94 = auto()
    G99 = auto()
    FG = auto()

    # Blue-Green
    BG01 = auto()
    BG02 = auto()
    BG07 = auto()
    BG09 = auto()
    BG10 = auto()
    BG13 = auto()
    BG15 = auto()
    BG18 = auto()
    BG57 = auto()
    BG72 = auto()

    # Blue
    B00 = auto()
    B000 = auto()
    B0000 = auto()
    B01 = auto()
    B02 = auto()
    B04 = auto()
    B05 = auto()
    B06 = auto()
    B12 = auto()
    B14 = auto()
    B16 = auto()
    B18 = auto()
    B21 = auto()
    B23 = auto()
    B24 = auto()
    B26 = auto()
    B28 = auto()
    B29 = auto()
    B32 = auto()
    B34 = auto()
    B37 = auto()
    B39 = auto()
    B41 = auto()
    B45 = auto()
    B52 = auto()
    B60 = auto()
    B63 = auto()
    B66 = auto()
    B69 = auto()
    B79 = auto()
    B91 = auto()
    B93 = auto()
    B95 = auto()
    B97 = auto()
    B99 = auto()
    FB2 = auto()

    # Earth
    E01 = auto()
    E04 = auto()
    E11 = auto()
    E17 = auto()
    E23 = auto()
    E37 = auto()
    E39 = auto()
    E53 = auto()
    E87 = auto()
    E97 = auto()

    # Flourescent
    FBG2 = auto()
    FY1 = auto()
    FYR1 = auto()
    FYG1 = auto()
    FV2 = auto()

    # Grays (C T N W)
    N3 = auto()
    W9 = auto()
    T9 = auto()
