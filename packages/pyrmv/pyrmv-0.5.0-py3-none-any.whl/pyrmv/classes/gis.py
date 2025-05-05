from datetime import timedelta
from typing import Any, Mapping, Union

from isodate import Duration, parse_duration


class Gis:
    """Gis object."""

    def __init__(self, ref: str, route: Mapping[str, Any]):
        self.ref: str = ref
        self.dist: Union[int, None] = route.get("dist")
        self.duration: Union[Duration, timedelta] = parse_duration(route["durS"])
        self.geo: Union[int, None] = route.get("dirGeo")
