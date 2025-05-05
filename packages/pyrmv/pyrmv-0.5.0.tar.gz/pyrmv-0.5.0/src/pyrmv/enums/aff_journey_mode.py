from enum import auto

from .auto_name import AutoName


class AffectedJourneyMode(AutoName):
    """Enumeration used to declare types of HIM search modes."""

    ALL = auto()
    "Return affected journeys."

    OFF = auto()
    "Do not return affected journeys."
