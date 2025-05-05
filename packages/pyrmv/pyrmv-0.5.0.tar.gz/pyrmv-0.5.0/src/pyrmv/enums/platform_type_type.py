from enum import Enum, auto


class PlatformTypeType(Enum):
    """Enumeration used to declare types of platform type.

    * U - Undefined
    * PL - Platform/track at train station
    * ST - Stop at bus or tram station
    * GA - Terminal/Gate at airport
    * PI - Pier if ship or ferry
    * SL - Slot/parking space if bike or car
    * FL - Floor in buildings or at footpath
    * CI - Check-in/entrance
    * CO - Check-out/exit
    * X - No explicit type
    * H - Hide platform information
    """

    U = auto()
    "Undefined"

    PL = auto()
    "Platform/track at train station"

    ST = auto()
    "Stop at bus or tram station"

    GA = auto()
    "Terminal/Gate at airport"

    PI = auto()
    "Pier if ship or ferry"

    SL = auto()
    "Slot/parking space if bike or car"

    FL = auto()
    "Floor in buildings or at footpath"

    CI = auto()
    "Check-in/entrance"

    CO = auto()
    "Check-out/exit"

    X = auto()
    "No explicit type"

    H = auto()
    "Hide platform information"
