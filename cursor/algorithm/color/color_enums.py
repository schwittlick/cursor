from enum import Enum, auto


class ColorCode(Enum):
    _110 = auto()  # actually without B, but cant use enum without char
    _000 = auto()  # actually doesnt axist, this is white

    # ordered
    # b
    B00 = auto()
    B000 = auto()
    B0000 = auto()
    B01 = auto()
    B02 = auto()
    B04 = auto()
    B05 = auto()
    B06 = auto()
    B16 = auto()
    B18 = auto()
    B21 = auto()
    B26 = auto()
    B28 = auto()
    B34 = auto()
    B37 = auto()
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

    # bg
    BG01 = auto()
    BG02 = auto()
    BG07 = auto()
    BG57 = auto()
    BG72 = auto()

    # g
    G12 = auto()
    G24 = auto()
    G43 = auto()
    G46 = auto()
    G99 = auto()

    # YG
    YG05 = auto()
    YG11 = auto()
    YG25 = auto()
    YG45 = auto()
    YG91 = auto()

    # y
    Y02 = auto()
    Y11 = auto()
    Y18 = auto()
    Y35 = auto()
    Y38 = auto()

    # yr
    YR01 = auto()
    YR12 = auto()
    YR18 = auto()
    YR23 = auto()
    YR68 = auto()

    # e (earth)
    E01 = auto()
    E11 = auto()
    E17 = auto()
    E23 = auto()
    E53 = auto()
    E87 = auto()

    # r
    R08 = auto()
    R12 = auto()
    R35 = auto()
    R39 = auto()
    R83 = auto()

    # rv
    RV06 = auto()
    RV11 = auto()
    RV19 = auto()
    RV29 = auto()
    RV63 = auto()

    # v
    V09 = auto()
    V15 = auto()
    V20 = auto()
    V91 = auto()
    V99 = auto()

    # bv
    BV04 = auto()
    BV11 = auto()
    BV20 = auto()
    BV31 = auto()
    BV34 = auto()

    # flourescent
    FBG2 = auto()
    FY1 = auto()
    FYR1 = auto()
    FYG1 = auto()
    FV2 = auto()



    # blues
    B12 = auto()
    B14 = auto()
    B23 = auto()
    B24 = auto()
    B29 = auto()
    B39 = auto()

    # blue-green
    BG09 = auto()
    BG10 = auto()
    BG13 = auto()
    BG15 = auto()
    BG18 = auto()

    # blue-violet
    BV0000 = auto()

    # sepia-brown
    E04 = auto()
    E37 = auto()
    E39 = auto()
    E97 = auto()

    # green
    G02 = auto()
    G03 = auto()
    G07 = auto()
    G14 = auto()
    G17 = auto()
    G20 = auto()
    G29 = auto()
    G40 = auto()
    G85 = auto()

    # red
    R00 = auto()
    R01 = auto()
    R02 = auto()
    R17 = auto()
    R29 = auto()
    R20 = auto()

    # red-violet
    RV09 = auto()
    RV13 = auto()
    RV93 = auto()

    # violet
    V12 = auto()
    V17 = auto()

    # yellow
    Y06 = auto()
    Y13 = auto()
    Y17 = auto()

    # yellow-green
    YG01 = auto()
    YG21 = auto()
    YG67 = auto()

    # yellow-red
    YR02 = auto()
    YR04 = auto()
    YR07 = auto()
    YR24 = auto()

    # grays
    N3 = auto()
    W9 = auto()
    T9 = auto()
