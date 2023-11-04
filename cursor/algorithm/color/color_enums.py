from enum import Enum, auto


class ColorCode(Enum):
    B110 = auto()  # actually without B, but cant use enum without char
    B000 = auto()  # actually doesnt axist, this is white

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
