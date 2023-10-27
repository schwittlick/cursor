from enum import Enum, auto


class ColorCode(Enum):
    B110 = auto()  # actually without B, but cant use enum without char
    B000 = auto()  # actually doesnt axist, this is white

    R17 = auto()
    R29 = auto()
    R20 = auto()

    Y06 = auto()
    Y13 = auto()
    Y17 = auto()

    YG01 = auto()
    YG21 = auto()
    YG67 = auto()

    YR07 = auto()
    YR24 = auto()

    BG15 = auto()
    BG18 = auto()

    B12 = auto()
    B14 = auto()
    B23 = auto()
    B24 = auto()
    B39 = auto()

    G02 = auto()
    G07 = auto()
    G14 = auto()
    G17 = auto()
    G29 = auto()
    G85 = auto()

    RV09 = auto()
    RV13 = auto()

    E37 = auto()

    V12 = auto()
    V17 = auto()
