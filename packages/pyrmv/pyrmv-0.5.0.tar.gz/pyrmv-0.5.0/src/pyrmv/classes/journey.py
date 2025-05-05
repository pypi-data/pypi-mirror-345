from typing import Any, List, Mapping, Union

from ..classes.message import Message
from ..classes.stop import Stop
from ..utility import ref_upgrade


class Journey:
    """Journey object."""

    def __init__(self, data: Mapping[str, Any]):
        self.stops: List[Stop] = []

        # Upgrade is temporarily used due to RMV API mismatch
        # self.ref = data["ref"]
        self.ref: str = ref_upgrade(data["ref"])

        self.direction: Union[str, None] = (
            data["Directions"]["Direction"][0].get("value")
            if data["Directions"]["Direction"]
            else None
        )
        self.direction_flag: Union[str, None] = (
            data["Directions"]["Direction"][0].get("flag")
            if data["Directions"]["Direction"]
            else None
        )
        self.stops.extend(Stop(stop) for stop in data["Stops"]["Stop"])
        self.messages: List[Message] = []

        if "Messages" in data:
            self.messages.extend(Message(message) for message in data["Messages"]["Message"])

    def __str__(self) -> str:
        return f"Journey with total of {len(self.stops)} stops and {len(self.messages)} messages heading {self.direction} ({self.direction_flag})"
