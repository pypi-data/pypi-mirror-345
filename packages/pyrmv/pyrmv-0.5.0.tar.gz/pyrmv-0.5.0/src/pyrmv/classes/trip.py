from datetime import timedelta
from typing import List, Union

from isodate import Duration, parse_duration

from ..classes.leg import Leg
from ..classes.stop import StopTrip


class Trip:
    """Trip object."""

    def __init__(self, data: dict):
        self.origin: StopTrip = StopTrip(data["Origin"])
        self.destination: StopTrip = StopTrip(data["Destination"])
        self.legs: List[Leg] = []
        self.legs.extend(Leg(leg) for leg in data["LegList"]["Leg"])
        self.calculation: str = data["calculation"]
        self.index: int = data["idx"]
        self.id: str = data["tripId"]
        self.ctx_recon: str = data["ctxRecon"]
        self.duration: Union[Duration, timedelta, None] = (
            None if "duration" not in data else parse_duration(data["duration"])
        )
        self.real_time_duration: Union[Duration, timedelta, None] = (
            None if "rtDuration" not in data else parse_duration(data["rtDuration"])
        )
        self.checksum: str = data["checksum"]
        self.transfer_count: int = data.get("transferCount", 0)

    def __str__(self) -> str:
        return f"Trip from {self.origin.name} to {self.destination.name} lasting {self.duration} ({self.real_time_duration}) with {len(self.legs)} legs and {self.transfer_count} transfers"
