from typing import Union

from requests import get
from xmltodict import parse as xmlparse

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# 2.4. Location Search by Coordinate (location.nearbystops)
def stop_by_coords(
    accessId: str,
    originCoordLat: Union[str, float],
    originCoordLong: Union[str, float],
    lang: Literal[
        "de", "da", "en", "es", "fr", "hu", "it", "nl", "no", "pl", "sv", "tr"
    ] = "en",
    json: bool = True,
    radius: Union[int, float] = 1000,
    maxNo: int = 10,
    stopType: Literal["S", "P", "SP", "SE", "SPE"] = "S",
    locationSelectionMode: Union[Literal["SLCT_N", "SLCT_A"], None] = None,
    products: Union[int, None] = None,
    meta: Union[str, None] = None,
    sattributes: Union[str, list, None] = None,
    sinfotexts: Union[str, list, None] = None,
) -> dict:
    """The location.nearbystops service returns a list of stops around a given center coordinate (within a
    radius of 1000m). The returned results are ordered by their distance to the center coordinate.

    Read more about this in section 2.4. "Location Search by Coordinate (location.nearbystops)" of HAFAS ReST Documentation.

    ### Args:
        * accessId (str): Access ID for identifying the requesting client. Get your key on [RMV website](https://opendata.rmv.de/site/start.html).
        * originCoordLat (Union[str, float]): Latitude of centre coordinate.
        * originCoordLong (Union[str, float]): Longitude of centre coordinate.
        * lang (Literal["de","da","en","es","fr","hu","it","nl","no","pl","sv","tr"], *optional*): The language of response. Defaults to "en".
        * json (bool, *optional*): Whether response should be retrieved as JSON. XML is returned if False. Only matters if raw_response is True. Defaults to True.
        * radius (Union[int, float], *optional*): Search radius in meter around the given coordinate if any. Defaults to 1000.
        * maxNo (int, *optional*): Maximum number of returned stops. Defaults to 10.
        * stopType (Literal["S", "P", "SP", "SE", "SPE"], *optional*): Type filter for location types. Defaults to "S".
        * locationSelectionMode (Literal["SLCT_N", "SLCT_A"], *optional*): Selection mode for locations. Defaults to None.
        * products (int, *optional*): Decimal value defining the product classes to be included in the search. It represents a bitmask combining bit number of a product as defined in the HAFAS raw data. Defaults to None.
        * meta (str, *optional*): Filter by a predefined meta filter. If the rules of the predefined filter should not be negated, put ! in front of it. Defaults to None.
        * sattributes (Union[str, list], *optional*): Filter locations by one or more attribute codes. Multiple attribute codes are separated by comma. If the attribute should not be part of the be location data, negate it by putting ! in front of it. Defaults to None.
        * sinfotexts (Union[str, list], *optional*): Filter locations by one or more station infotext codes and values. Multiple attribute codes are separated by comma the value by pipe |. Defaults to None.

    ### Returns:
        * dict: Output from RMV. Dict will contain "errorCode" and "errorText" if exception occurs.
    """

    payload = {}
    headers = {"Accept": "application/json"} if json else {"Accept": "application/xml"}

    for var, val in locals().copy().items():
        if str(var) == "stopType":
            if val != None:
                payload["type"] = val.upper()
        elif str(var) == "locationSelectionMode":
            if val != None:
                payload["locationSelectionMode"] = val.upper()
        elif str(var) not in ["json", "headers", "payload", "raw_response"]:
            if val != None:
                payload[str(var)] = val

    output = get(
        "https://www.rmv.de/hapi/location.nearbystops", params=payload, headers=headers
    )

    return output.json() if json else xmlparse(output.content)
