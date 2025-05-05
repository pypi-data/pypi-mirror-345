import contextlib

import requests

from .board_arrival import board_arrival
from .board_departure import board_departure
from .him_search import him_search
from .journey_detail import journey_detail
from .stop_by_coords import stop_by_coords
from .stop_by_name import stop_by_name
from .trip_find import trip_find
from .trip_recon import trip_recon

with contextlib.suppress(ImportError):
    import ujson

    requests.models.complexjson = ujson
