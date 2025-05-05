from datetime import datetime
from typing import OrderedDict, Union

from requests import get
from xmltodict import parse as xmlparse

from ..utility import weekdays_bitmask

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# 2.37. HIM Search (himsearch)
def him_search(
    accessId: str,
    json: bool = True,
    dateB: Union[str, datetime, None] = None,
    dateE: Union[str, datetime, None] = None,
    timeB: Union[str, datetime, None] = None,
    timeE: Union[str, datetime, None] = None,
    weekdays: Union[str, OrderedDict[str, bool], None] = None,
    himIds: Union[str, list, None] = None,
    hierarchicalView: bool = False,
    operators: Union[str, list, None] = None,
    categories: Union[str, list, None] = None,
    channels: Union[str, list, None] = None,
    companies: Union[str, list, None] = None,
    lines: Union[str, list, None] = None,
    lineids: Union[str, list, None] = None,
    stations: Union[str, list, None] = None,
    fromstation: Union[str, None] = None,
    tostation: Union[str, None] = None,
    bothways: Union[bool, None] = None,
    trainnames: Union[str, list, None] = None,
    metas: Union[str, list, None] = None,
    himcategory: Union[str, None] = None,
    himtags: Union[str, list, None] = None,
    regions: Union[str, list, None] = None,
    himtext: Union[str, list, None] = None,
    himtexttags: Union[str, list, None] = None,
    additionalfields: Union[str, list, dict, None] = None,
    poly: bool = False,
    searchmode: Union[Literal["MATCH", "NOMATCH", "TFMATCH"], None] = None,
    affectedJourneyMode: Union[Literal["ALL", "OFF"], None] = None,
    affectedJourneyStopMode: Union[Literal["ALL", "IMP", "OFF"], None] = None,
    orderBy: Union[str, list, None] = None,
    minprio: Union[str, int, None] = None,
    maxprio: Union[str, int, None] = None,
) -> dict:
    """The himSearch will return a list of HIM messages if matched by the given criteria as well as affected
    products if any.

    Read more about this in section 2.37. "HIM Search (himsearch)" of HAFAS ReST Documentation.

    ### Args:
        * accessId (str): Access ID for identifying the requesting client. Get your key on [RMV website](https://opendata.rmv.de/site/start.html).
        * json (bool, *optional*): Whether response should be retrieved as JSON. XML is returned if False. Defaults to True.
        * dateB (Union[str, datetime], *optional*): Sets the event period start date. Represented in the format `YYYY-MM-DD`. By default the current server date is used. Defaults to None.
        * dateE (Union[str, datetime], *optional*): Sets the event period end date. Represented in the format `YYYY-MM-DD`. By default the current server date is used. Defaults to None.
        * timeB (Union[str, datetime], *optional*): Sets the event period start time. Represented in the format `hh:mm[:ss]` in 24h nomenclature. Seconds will be ignored for requests. By default the current server time is used. Defaults to None.
        * timeE (Union[str, datetime], *optional*): Sets the event period end time. Represented in the format `hh:mm[:ss]` in 24h nomenclature. Seconds will be ignored for requests. By default the current server time is used. Defaults to None.
        * weekdays (Union[str, OrderedDict[str, bool]], *optional*): Bitmask or an OrderedDict for validity of HIM messages based on weekdays. OrderedDict must be formatted as follows: `OrderedDict(Monday=bool, Tuesday=bool, Wednesday=bool, Thursday=bool, Friday=bool, Saturday=bool, Sunday=bool)`. Each character of a bitmask represents a weekday starting on monday. Example: Only find HIM Messages valid from monday to friday: `1111100`. Defaults to None.
        * himIds (Union[str, list], *optional*): List of HIM message IDs as a list or as a string separated by comma. Defaults to None.
        * hierarchicalView (bool, *optional*): Return parent messages with childs. Defaults to False.
        * operators (Union[str, list], *optional*): List of operators as a list or as a string separated by comma. Defaults to None.
        * categories (Union[str, list], *optional*): List of train categories as a list or as a string separated by comma. Defaults to None.
        * channels (Union[str, list], *optional*): List of channels as a list or as a string separated by comma. Defaults to None.
        * companies (Union[str, list], *optional*): List of companies as a list or as a string separated by comma. Defaults to None.
        * lines (Union[str, list], *optional*): Only HIM messages for the given line are part of the result. To filter multiple lines, separate the codes by comma. Defaults to None.
        * lineids (Union[str, list], *optional*): Only HIM messages for the given line (identified by its line ID) are part of the result. To filter multiple lines, separate the line IDs by comma. Defaults to None.
        * stations (Union[str, list], *optional*): List of (external) station ids to be filtered for as a list or as a string separated by comma. Defaults to None.
        * fromstation (str, *optional*): Filter messages by line segment starting at this station given as (external) station id. Defaults to None.
        * tostation (str, *optional*): Filter messages by line segment travelling in direction of this station given as (external) station id. Defaults to None.
        * bothways (bool, *optional*): If enabled, messages in both directions - from 'fromstation' to 'tostation' as well as from 'tostation' to 'fromstation' are returned. Defaults to None.
        * trainnames (Union[str, list], *optional*): List of train name to be filtered for as a list or as a string separated by comma. Defaults to None.
        * metas (Union[str, list], *optional*): List of predefined filters as a list or as a string separated by comma. Defaults to None.
        * himcategory (str, *optional*): HIM category, e.g. Works and/or Disturbance. Value depends on your HAFAS server data. Defaults to None.
        * himtags (Union[str, list], *optional*): HIM Tags. Value depends on your HAFAS server data. Return HIM messages having these tag(s) only. Multiple values are separated by comma. Note: HIM tags differ from HIM text tags. Defaults to None.
        * regions (Union[str, list], *optional*): Filter for HIM messages based on regions defined in HAFAS raw data. As a list or as a string separated by comma. Available regions can be retrieved by /datainfo service. Defaults to None.
        * himtext (Union[str, list], *optional*): Filter for HIM messages containing the given free text message as a list or as a string separated by comma. Defaults to None.
        * himtexttags (Union[str, list], *optional*): Return HIM texts having this text tag(s) only. Multiple values are separated by comma. Note: HIM text tags differ from HIM tags. Defaults to None.
        * additionalfields (Union[str, list, dict], *optional*): List of additional fields and values to be filtered for. Two filter options are available: Filter by key only: `additionalfields=key` or filter by key and value: `additionalfields={key:value}`. Multiple filters are separated by comma like `additionalfields=[keyA,keyB]` or `additionalfields={key:value}`. Defaults to None.
        * poly (bool, *optional*): Enables/disables returning of geo information for affected edges and regions if available and enabled in the backend. Defaults to False.
        * searchmode (Literal["MATCH", "NOMATCH", "TFMATCH"], *optional*): HIM search mode. `"NOMATCH"` iterate over all HIM messages available. `"MATCH"` iterate over all trips to find HIM messages. `"TFMATCH"` uses filters defined `metas` parameter. Defaults to None.
        * affectedJourneyMode (Literal["ALL", "OFF"], *optional*): Define how to return affected journeys `"OFF"`: do not return affected journeys. `"ALL"`: return affected journeys. Defaults to None.
        * affectedJourneyStopMode (Literal["ALL", "IMP", "OFF"], *optional*): Define how to return stops of affected journeys. `"IMP"`: return important stops of affected journeys. `"OFF"`: do not return stops of affected journeys. `"ALL"`: return all affected stops of affected journeys. Defaults to None.
        * orderBy (Union[str, list], *optional*): Define the Order the returned messages by fields and directions. Multiple, string comma separated or list entries are supported. Read more about this in HAFAS ReST Documentation. Defaults to None.
        * minprio (Union[str, int], *optional*): Filter for HIM messages having at least this priority. Defaults to None.
        * maxprio (Union[str, int], *optional*): Filter for HIM messages having this priority as maximum. Defaults to None.

    ### Returns:
        * dict: Output from RMV. Dict will contain "errorCode" and "errorText" if exception occurs.
    """

    payload = {}
    headers = {"Accept": "application/json"} if json else {"Accept": "application/xml"}

    for var, val in locals().copy().items():
        if str(var) in {"dateB", "dateE"}:
            if val != None:
                if isinstance(val, datetime):
                    payload[str(var)] = val.strftime("%Y-%m-%d")
                else:
                    payload[str(var)] = val
        elif str(var) in {"timeB", "timeE"}:
            if val != None:
                payload[str(var)] = (
                    val.strftime("%H:%M") if isinstance(val, datetime) else val
                )
        elif str(var) == "weekdays":
            if val != None:
                if isinstance(val, OrderedDict):
                    payload[str(var)] = weekdays_bitmask(val)
                else:
                    payload[str(var)] = val
        elif str(var) == "searchmode":
            if val != None:
                payload["searchmode"] = val.upper()
        elif str(var) == "affectedJourneyMode":
            if val != None:
                payload["affectedJourneyMode"] = val.upper()
        elif str(var) == "affectedJourneyStopMode":
            if val != None:
                payload["affectedJourneyStopMode"] = val.upper()
        elif str(var) not in ["json", "headers", "payload"]:
            if val != None:
                payload[str(var)] = val

    output = get("https://www.rmv.de/hapi/himsearch", params=payload, headers=headers)

    return output.json() if json else xmlparse(output.content)
