from enum import auto

from .auto_name import AutoName


class AffectedJourneyStopMode(AutoName):
    """Enumeration used to declare types of affected journey stops return modes."""

    ALL = auto()
    "Return all affected stops of affected journeys."

    IMP = auto()
    "Return important stops of affected journeys."

    OFF = auto()
    "Do not return stops of affected journeys."
