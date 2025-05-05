from enum import auto

from .auto_name import AutoName


class BoardArrivalType(AutoName):
    """Enumeration used to declare types of arrival board.

    * ARR - Arrival board as configured in HAFAS
    * ARR_EQUIVS - Arrival board with all journeys at any masts and equivalent stops
    * ARR_MAST - Arrival board at mast
    * ARR_STATION - Arrival board with all journeys at any masts of the requested station
    """

    ARR = auto()
    "Arrival board as configured in HAFAS"

    ARR_EQUIVS = auto()
    "Arrival board with all journeys at any masts and equivalent stops"

    ARR_MAST = auto()
    "Arrival board at mast"

    ARR_STATION = auto()
    "Arrival board with all journeys at any masts of the requested station"


class BoardDepartureType(AutoName):
    """Enumeration used to declare types of departure board.

    * DEP - Departure board as configured in HAFAS
    * DEP_EQUIVS - Departure board with all journeys at any masts and equivalent stops
    * DEP_MAST - Departure board at mast
    * DEP_STATION - Departure board with all journeys at any masts of the requested station
    """

    DEP = auto()
    "Departure board as configured in HAFAS"

    DEP_EQUIVS = auto()
    "Departure board with all journeys at any masts and equivalent stops"

    DEP_MAST = auto()
    "Departure board at mast"

    DEP_STATION = auto()
    "Departure board with all journeys at any masts of the requested station"
