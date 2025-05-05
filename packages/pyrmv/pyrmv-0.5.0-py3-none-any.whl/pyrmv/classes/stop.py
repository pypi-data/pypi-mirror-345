from datetime import datetime
from typing import Union


class Stop:
    """Stop object."""

    def __init__(self, data: dict):
        self.name: str = data["name"]
        self.id: str = data["id"]
        self.ext_id: Union[str, None] = data.get("extId")
        self.description: Union[str, None] = data.get("description")
        self.lon: float = data["lon"]
        self.lat: float = data["lat"]
        self.route_index: Union[int, None] = data.get("routeIdx")
        self.track_arrival: Union[str, None] = data.get("arrTrack")
        self.track_departure: Union[str, None] = data.get("depTrack")

    def __str__(self) -> str:
        return f"Stop {self.name} at {self.lon}, {self.lat}"


class StopTrip(Stop):
    """Trip stop object. It's like a Stop object, but with a date and time."""

    def __init__(self, data: dict):
        self.type: str = data["type"]
        self.time: datetime = datetime.strptime(
            f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M:%S"
        )
        super().__init__(data)

    def __str__(self) -> str:
        return f"Stop {self.name} at {self.lon}, {self.lat} at {self.time.time()}"
