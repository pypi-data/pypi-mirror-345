from enum import auto

from .auto_name import AutoName


class SelectionMode(AutoName):
    """Enumeration used to declare location selection modes.

    * SLCT_A - Selectable
    * SLCT_N - Not selectable
    """

    SLCT_A = auto()
    "Selectable"

    SLCT_N = auto()
    "Not selectable"
