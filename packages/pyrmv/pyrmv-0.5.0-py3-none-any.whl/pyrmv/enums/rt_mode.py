from enum import auto

from .auto_name import AutoName


class RealTimeMode(AutoName):
    """Enumeration used to declare types of real-time traffic."""

    FULL = auto()
    "Combined search on planned and real-time data This search consists of two steps: i. Search on scheduled data ii. If the result of step (i) contains a non-feasible connection, a search on real-time data is performed and all results are combined"

    INFOS = auto()
    "Search on planned data, use real-time information for display only: Connections are computed on the basis of planned data. Delays and feasibility of the connections are integrated into the result. Note that additional trains (supplied via realtime feed) will not be part of the resulting connections."

    OFF = auto()
    "Search on planned data, ignore real-time information completely: Connections are computed on the basis of planned data. No real-time information is shown."

    REALTIME = auto()
    "Search on real-time data: Connections are computed on the basis of real-time data, using planned schedule only whenever no real-time data is available. All connections computed are feasible with respect to the currently known real-time situation. Additional trains (supplied via real-time feed) will be found if these are part of a fast, comfortable, or direct connection (or economic connection, if economic search is activated)."

    SERVER_DEFAULT = auto()
    "One of the other real-times modes used by default for RMV."
