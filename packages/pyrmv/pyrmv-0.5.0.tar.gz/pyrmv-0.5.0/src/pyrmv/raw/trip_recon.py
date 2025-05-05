from datetime import datetime
from typing import Union

from requests import get
from xmltodict import parse as xmlparse

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


def trip_recon(
    accessId: str,
    ctx: str,
    json: bool = True,
    poly: bool = False,
    polyEnc: Literal["DLT", "GPA", "N"] = "N",
    date: Union[str, datetime, None] = None,
    useCombinedComparison: Union[bool, None] = None,
    acceptGaps: Union[bool, None] = None,
    allowDummySections: Union[bool, None] = None,
    flagAllNonReachable: Union[bool, None] = None,
    matchCatStrict: Union[bool, None] = None,
    matchIdNonBlank: Union[bool, None] = None,
    matchIdStrict: Union[bool, None] = None,
    matchNumStrict: Union[bool, None] = None,
    matchRtType: Union[bool, None] = None,
    enableRtFullSearch: Union[bool, None] = None,
    enableReplacements: Union[bool, None] = None,
    arrL: Union[int, None] = None,
    arrU: Union[int, None] = None,
    depL: Union[int, None] = None,
    depU: Union[int, None] = None,
    passlist: bool = False,
    showPassingPoints: bool = False,
    rtMode: Union[Literal["FULL", "INFOS", "OFF", "REALTIME", "SERVER_DEFAULT"], None] = None,
    eco: bool = False,
    ecoCmp: bool = False,
    ecoParams: Union[str, None] = None,
    tariff: Union[bool, None] = None,
    trafficMessages: Union[bool, None] = None,
    travellerProfileData: Union[str, None] = None,
) -> dict:
    """Reconstructing a trip can be achieved using the reconstruction context provided by any trip result in the
    ctxRecon attribute of Trip element. The result will be a true copy of the original trip search result given
    that the underlying data did not change.

    Read more about this in section 2.17. "Reconstruction (recon)" of HAFAS ReST Documentation.

    ### Args:
        * accessId (str): Access ID for identifying the requesting client. Get your key on [RMV website](https://opendata.rmv.de/site/start.html).
        * ctx (str): Specifies the reconstruction context.
        * json (bool, *optional*): Whether response should be retrieved as JSON. XML is returned if False. Defaults to True.
        * poly (bool, *optional*): Enables/disables the calculation of the polyline for each leg of the trip except any GIS route. Defaults to False.
        * polyEnc (Literal["DLT", "GPA", "N"], *optional*): Defines encoding of the returned polyline. Possible values are "N" (no encoding / compression), "DLT" (delta to the previous coordinate), "GPA" (Google encoded polyline format). Defaults to "N".
        * date (Union[str, datetime], *optional*): Sets the start date for which the departures shall be retrieved. Represented in the format `YYYY-MM-DD`. This parameter will force the ser-vice to reconstruct the trip on that specific date. If the trip is not available on that date, because it does not operate, the error code SVC_NO_RESULT will be returned. Defaults to None.
        * useCombinedComparison (bool, *optional*): Compare based on combined output name - `False`: Compare parameters (category, line, train number) individually. Defaults to None.
        * acceptGaps (bool, *optional*): Accept an incomplete description of the connection (with gaps) i.e. missing walks/transfers. Defaults to None.
        * allowDummySections (bool, *optional*): Allow a partial reconstruction that will not lead to a reconstruction failure if sections are not reconstructable. Instead, for theses inconstructable sections, dummy sections will be created in the result. Defaults to None.
        * flagAllNonReachable (bool, *optional*): Should all non-reachable journeys be flagged (`True`), or only the first one encountered? Defaults to None.
        * matchCatStrict (bool, *optional*): Should the category (Gattung) match exactly? Only applicable if `useCombinedComparison` is `False`. Defaults to None.
        * matchIdNonBlank (bool, *optional*): Should the train identifier (Zugbezeichner) without whitespace match? Defaults to None.
        * matchIdStrict (bool, *optional*): Should the train identifier (Zugbezeichner) match exactly? Defaults to None.
        * matchNumStrict (bool, *optional*): Should the train number (Zugnummer) match exactly? Only applicable if `useCombinedComparison` is `False`. Defaults to None.
        * matchRtType (bool, *optional*): Should the realtime type that journeys are based on (e.g. SOLL, IST, additional, deviation, …) be considered? Defaults to None.
        * enableRtFullSearch (bool, *optional*): By default, the reconstruction request makes one attempt for each journey within the scheduled data. However, the scheduled data may not necessarily reflect basic realtime properties of the journeys therein. In such a case, one may enable a two-step approach which we call "full search", i.e. search for matching journeys in the scheduled data in a first step. If this fails, then search for matching journeys in the realtime data. Defaults to None.
        * enableReplacements (bool, *optional*): If set to true replaces cancelled journeys with their replacement journeys if possible. Defaults to None.
        * arrL (int, *optional*): Lower deviation in minutes within interval [0, 720] indicating "how much earlier than original arrival". Defaults to None.
        * arrU (int, *optional*): Upper deviation in minutes within interval [0, 720] indicating "how much later than original arrival". Defaults to None.
        * depL (int, *optional*): Lower deviation in minutes within interval [0, 720] indicating "how much earlier than original departure". Defaults to None.
        * depU (int, *optional*): Upper deviation in minutes within interval [0, 720] indicating "how much later than original departure". Defaults to None.
        * passlist (bool, *optional*): Enables/disables the return of the passlist for each leg of the trip. Defaults to False.
        * showPassingPoints (bool, *optional*): Enables/disables the return of stops having no alighting and boarding in its passlist for each leg of the trip. Needs passlist parameter enabled. Defaults to False.
        * rtMode (Literal["FULL", "INFOS", "OFF", "REALTIME", "SERVER_DEFAULT"], *optional*): Set the realtime mode to be used. Read more about this in HAFAS ReST Documentation. Defaults to None.
        * eco (bool, *optional*): Enables/disables eco value calculation. Defaults to False.
        * ecoCmp (bool, *optional*): Enables/disables eco comparison. Defaults to False.
        * ecoParams (str, *optional*): Provide additional eco parameters. Values vary. Defaults to None.
        * tariff (bool, *optional*): Enables/disables the output of tariff data. The default is configurable via provisioning. Defaults to None.
        * trafficMessages (bool, *optional*): Enables/disables the output of traffic messages. The default is configurable via provisioning. Defaults to None.
        * travellerProfileData (str, *optional*): Traveller profile data. Structure depends on set up. Defaults to None.

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
        elif str(var) not in ["json", "headers", "payload"]:
            if val != None:
                payload[str(var)] = val

    output = get("https://www.rmv.de/hapi/recon", params=payload, headers=headers)

    return output.json() if json else xmlparse(output.content)
