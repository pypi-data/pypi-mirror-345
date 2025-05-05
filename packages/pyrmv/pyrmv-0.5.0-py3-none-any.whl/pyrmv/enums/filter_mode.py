from enum import auto

from .auto_name import AutoName


class FilterMode(AutoName):
    """Enumeration used to declare filters for nearby searches.

    * DIST_PERI - Accentuate matches. Matches in the radius are first
    * EXCL_PERI - Returns matches inside the radius only
    * SLCT_PERI - Matches in the radius are excluded. Returns matches outside the radius only
    """

    DIST_PERI = auto()
    "Accentuate matches. Matches in the radius are first."

    EXCL_PERI = auto()
    "Returns matches inside the radius only."

    SLCT_PERI = auto()
    "Matches in the radius are excluded. Returns matches outside the radius only."
