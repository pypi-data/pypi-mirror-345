from enum import auto

from .auto_name import AutoName


class SearchMode(AutoName):
    """Enumeration used to declare types of HIM search modes."""

    MATCH = auto()
    "Iterate over all trips to find HIM messages."

    NOMATCH = auto()
    "Iterate over all HIM messages available."

    TFMATCH = auto()
    "Uses filters defined `metas` parameter."
