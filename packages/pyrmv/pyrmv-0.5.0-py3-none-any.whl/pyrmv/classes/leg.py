from datetime import timedelta
from typing import Any, List, Mapping, Union

from isodate import Duration, parse_duration

from ..classes.gis import Gis
from ..classes.message import Message
from ..classes.stop import StopTrip


class Leg:
    """Trip leg object."""

    def __init__(self, data: Mapping[str, Any]):
        self.origin: StopTrip = StopTrip(data["Origin"])
        self.destination: StopTrip = StopTrip(data["Destination"])
        self.gis = (
            None if "GisRef" not in data else Gis(data["GisRef"]["ref"], data["GisRoute"])
        )
        self.messages: List[Message] = []
        self.index: Union[int, None] = data.get("idx")
        self.name: str = data["name"]
        self.type: Union[str, None] = data.get("type")
        self.direction: Union[str, None] = data.get("direction")
        self.number: Union[str, None] = data.get("number")
        self.duration: Union[Duration, timedelta] = parse_duration(data["duration"])
        self.distance: Union[int, None] = data.get("dist")

        if "Messages" in data:
            self.messages.extend(Message(message) for message in data["Messages"]["Message"])
