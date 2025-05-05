from datetime import datetime, timedelta
from typing import Union

from requests import get
from xmltodict import parse as xmlparse

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# 2.24. Departure Board (departureBoard)
def board_departure(
    accessId: str,
    json: bool = True,
    id: Union[str, None] = None,
    extId: Union[str, None] = None,
    direction: Union[str, None] = None,
    date: Union[str, datetime, None] = None,
    time: Union[str, datetime, None] = None,
    duration: Union[int, timedelta] = 60,
    maxJourneys: int = -1,
    products: Union[int, None] = None,
    operators: Union[str, list, None] = None,
    lines: Union[str, list, None] = None,
    filterEquiv: bool = True,
    attributes: Union[str, list, None] = None,
    platforms: Union[str, list, None] = None,
    passlist: bool = False,
    boardType: Literal["DEP", "DEP_EQUIVS", "DEP_MAST", "DEP_STATION"] = "DEP",
) -> dict:
    """The separture board can be retrieved by a call to the departureBoard service. This method will return the
    next departures (or less if not existing) from a given point in time within a duration covered time span. The
    default duration size is 60 minutes.

    Note: The result list always contains all departures running the the last minute found even if the requested
    maximum was overrun.

    Read more about this in section 2.24. "Departure Board (departureBoard)" of HAFAS ReST Documentation.

    ### Args:
        * accessId (str): Access ID for identifying the requesting client. Get your key on [RMV website](https://opendata.rmv.de/site/start.html).
        * json (bool, *optional*): Whether response should be retrieved as JSON. XML is returned if False. Only matters if raw_response is True. Defaults to True.
        * id (str, *optional*): Access ID for identifying the requesting client. Defaults to None.
        * extId (str, *optional*): Deprecated. Please use id as it supports external IDs. Specifies the external station/stop ID for which the arrivals shall be retrieved. Required if id is not present. Such ID can be retrieved from the `stop_by_name` or `stop_by_coords`. Defaults to None.
        * direction (str, *optional*): If only vehicles departing or arriving from a certain direction shall be returned, specify the direction by giving the station/stop ID of the last stop on the journey. Defaults to None.
        * date (Union[str, datetime], *optional*): Sets the start date for which the departures shall be retrieved. Represented in the format YYYY-MM-DD. By default the current server date is used. Defaults to None.
        * time (Union[str, datetime], *optional*): Sets the start time for which the departures shall be retrieved. Represented in the format hh:mm[:ss] in 24h nomenclature. Seconds will be ignored for requests. By default the current server time is used. Defaults to None.
        * duration (int, *optional*): Set the interval size in minutes. Defaults to 60.
        * maxJourneys (int, *optional*): Maximum number of journeys to be returned. If no value is defined or -1, all departing/arriving services within the duration sized period are returned. Defaults to -1.
        * products (int, *optional*): Decimal value defining the product classes to be included in the search. It represents a bitmask combining bit number of a product as defined in the HAFAS raw data. Defaults to None.
        * operators (Union[str, list], *optional*): Only journeys provided by the given operators are part of the result. To filter multiple operators, separate the codes by comma. If the operator should not be part of the be trip, negate it by putting ! in front of it. Example: Filter for operator A and B: `operators=[A,B]`. Defaults to None.
        * lines (Union[str, list], *optional*): Only journeys running the given line are part of the result. To filter multiple lines, provide a list or separate the codes by comma. If the line should not be part of the be trip, negate it by putting ! in front of it. Defaults to None.
        * filterEquiv (bool, *optional*): Use `boardType` instead. Enables/disables the filtering of equivalent marked stops. Defaults to True.
        * attributes (Union[str, list], *optional*): Filter boards by one or more attribute codes of a journey. Multiple attribute as a list or as a string separated by comma. If the attribute should not be part of the result, negate it by putting ! in front of it. Defaults to None.
        * platforms (Union[str, list], *optional*): Filter boards by platform. Multiple platforms provided as a list or as a string separated by comma. Defaults to None.
        * passlist (bool, *optional*): Include a list of all passed waystops. Defaults to False.
        * boardType (Literal["DEP", "DEP_EQUIVS", "DEP_MAST", "DEP_STATION"], *optional*): Set the station departure board type to be used. DEP: Departure board as configured in HAFAS; DEP_EQUIVS: Departure board with all journeys at any masts and equivalent stops; DEP_MAST: Departure board at mast; DEP_STATION: Departure board with all journeys at any masts of the requested station. Defaults to "DEP".

    ### Returns:
        * dict: Output from RMV. Dict will contain "errorCode" and "errorText" if exception occurs.
    """

    payload = {}
    headers = {"Accept": "application/json"} if json else {"Accept": "application/xml"}

    for var, val in locals().copy().items():
        if str(var) == "date":
            if val != None:
                if isinstance(val, datetime):
                    payload[str(var)] = val.strftime("%Y-%m-%d")
                else:
                    payload[str(var)] = val
        elif str(var) == "time":
            if val != None:
                payload[str(var)] = (
                    val.strftime("%H:%M") if isinstance(val, datetime) else val
                )
        elif str(var) == "duration":
            if val != None:
                payload[str(var)] = val.minutes if isinstance(val, timedelta) else val
        elif str(var) == "boardType":
            if val != None:
                payload["type"] = val.upper()
        elif str(var) not in ["json", "headers", "payload"]:
            if val != None:
                payload[str(var)] = val

    output = get("https://www.rmv.de/hapi/departureBoard", params=payload, headers=headers)

    return output.json() if json else xmlparse(output.content)
