from datetime import datetime
from typing import Union

from requests import get
from xmltodict import parse as xmlparse

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# 2.26. Journey Detail (journeyDetail)
def journey_detail(
    accessId: str,
    id: str,
    json: bool = True,
    date: Union[str, datetime, None] = None,
    poly: bool = False,
    polyEnc: Literal["DLT", "GPA", "N"] = "N",
    showPassingPoints: bool = False,
    rtMode: Union[Literal["FULL", "INFOS", "OFF", "REALTIME", "SERVER_DEFAULT"], None] = None,
    fromId: Union[str, None] = None,
    fromIdx: Union[int, None] = None,
    toId: Union[str, None] = None,
    toIdx: Union[int, None] = None,
    baim: bool = False,
) -> dict:
    """The journey_detail method will deliver information about the complete route of a vehicle. The journey
    identifier is part of a trip or departureBoard response. It contains a list of all stops/stations of this journey
    including all departure and arrival times (with real-time data if available) and additional information like
    specific attributes about facilities and other texts.

    Read more about this in section 2.26. "Journey Detail (journeyDetail)" of HAFAS ReST Documentation.

    ### Args:
        * accessId (str): Access ID for identifying the requesting client. Get your key on [RMV website](https://opendata.rmv.de/site/start.html).
        * id (str): Specifies the internal journey id of the journey shall be retrieved. Maximum length 512.
        * json (bool, *optional*): Whether response should be retrieved as JSON. XML is returned if False. Defaults to True.
        * date (Union[str, datetime], *optional*): Day of operation. Represented in the format `YYYY-MM-DD`. By default the current server date is used. Defaults to None.
        * poly (bool, *optional*): Enables/disables the calculation of the polyline for each leg of the trip except any GIS route. Defaults to False.
        * polyEnc (Literal["DLT", "GPA", "N"], *optional*): Defines encoding of the returned polyline. Possible values are "N" (no encoding / compression), "DLT" (delta to the previous coordinate), "GPA" (Google encoded polyline format). Defaults to "N".
        * showPassingPoints (bool, *optional*): Enables/disables the return of stops having no alighting and no boarding in its passlist for each leg of the trip. Defaults to False.
        * rtMode (Literal["FULL", "INFOS", "OFF", "REALTIME", "SERVER_DEFAULT"], *optional*): Set the realtime mode to be used. Read more about this in HAFAS ReST Documentation. Defaults to None.
        * fromId (str, *optional*): Specifies the station/stop ID the partial itinerary shall start from. Defaults to None.
        * fromIdx (str, *optional*): Specifies the station/stop index the partial itinerary shall start from. Defaults to None.
        * toId (str, *optional*): Specifies the station/stop ID the partial itinerary shall end at. Defaults to None.
        * toIdx (str, *optional*): Specifies the station/stop index the partial itinerary shall end at. Defaults to None.
        * baim (bool, *optional*): Enables/disables BAIM search and response. Defaults to False.

    ### Returns:
        * dict: Output from RMV. Dict will contain "errorCode" and "errorText" if exception occurs.
    """

    payload = {}
    headers = {"Accept": "application/json"} if json else {"Accept": "application/xml"}

    for var, val in locals().copy().items():
        if str(var) == "rtMode":
            if val != None:
                payload["rtMode"] = val.upper()
        elif str(var) not in ["json", "headers", "payload"]:
            if val != None:
                payload[str(var)] = val

    output = get("https://www.rmv.de/hapi/journeyDetail", params=payload, headers=headers)

    return output.json() if json else xmlparse(output.content)
