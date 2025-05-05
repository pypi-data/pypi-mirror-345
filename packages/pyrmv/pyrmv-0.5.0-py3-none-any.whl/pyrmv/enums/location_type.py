from enum import auto

from .auto_name import AutoName


class LocationType(AutoName):
    """Enumeration used to declare types of location filter.

    * S - Search for station/stops only
    * A - Search for addresses only
    * P - Search for POIs only
    * AP - Search for addresses and POIs
    * SA - Search for station/stops and addresses
    * SE - Search for stations/stops and entrypoints
    * SP - Search for stations/stops and POIs
    * ALL - Search in all existing location pools
    * SPE - Search for stations/stops, POIs and entrypoints

    Note that not all location types may be available for a certain methods.
    Make sure that selected type is supported by method by looking up
    its acceptable types in argument description.
    """

    S = auto()
    "Search for station/stops only"

    A = auto()
    "Search for addresses only"

    P = auto()
    "Search for POIs only"

    AP = auto()
    "Search for addresses and POIs"

    SA = auto()
    "Search for station/stops and addresses"

    SE = auto()
    "Search for stations/stops and entrypoints"

    SP = auto()
    "Search for stations/stops and POIs"

    ALL = auto()
    "Search in all existing location pools"

    SPE = auto()
    "Search for stations/stops, POIs and entrypoints"
