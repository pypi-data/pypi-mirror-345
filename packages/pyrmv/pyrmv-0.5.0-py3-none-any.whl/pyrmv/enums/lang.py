from enum import auto

from .auto_name import AutoName


class Language(AutoName):
    """Enumeration used to declare locales as ISO-3166 codes (but only available in HAFAS ones)."""

    AR = auto()
    "Arabic"

    CA = auto()
    "Catalan, Valencian"

    DA = auto()
    "Danish"

    DE = auto()
    "German"

    EL = auto()
    "Greek"

    EN = auto()
    "English"

    ES = auto()
    "Spanish"

    FI = auto()
    "Finnish"

    FR = auto()
    "French"

    HI = auto()
    "Hindi"

    HR = auto()
    "Croatian"

    HU = auto()
    "Hungarian"

    IT = auto()
    "Italian"

    NL = auto()
    "Dutch"

    NO = auto()
    "Norwegian"

    PL = auto()
    "Polish"

    RU = auto()
    "Russian"

    SK = auto()
    "Slovak"

    SL = auto()
    "Slovenian"

    SV = auto()
    "Swedish"

    TL = auto()
    "Tagalog"

    TR = auto()
    "Turkish"

    UR = auto()
    "Urdu"

    ZH = auto()
    "Chinese"
