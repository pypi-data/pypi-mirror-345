from datetime import datetime
from typing import Any, List, Mapping, Union

from ..classes.journey import Journey
from ..classes.message import Message
from ..classes.stop import Stop
from ..utility import ref_upgrade


class LineArrival:
    def __init__(
        self,
        data: Mapping[str, Any],
        retrieve_stops: bool = False,
        retrieve_journey: bool = False,
        client: Union["pyrmv.Client", None] = None,
    ):
        if (retrieve_stops or retrieve_journey) and client is None:
            raise KeyError(
                "Stops/journey retrieval requested but client argument was not provided."
            )

        # Upgrade is temporarily used due to RMV API mismatch
        # self.journey = client.journey_detail(data["JourneyDetailRef"]["ref"])
        self.journey: Union[Journey, None] = (
            client.journey_detail(ref_upgrade(data["JourneyDetailRef"]["ref"]))
            if retrieve_journey
            else None
        )

        self.status: str = data["JourneyStatus"]
        self.messages: List[Message] = []
        self.name: str = data["name"]
        self.type: str = data["type"]
        self.stop_name: str = data["stop"]
        self.stop_id: str = data["stopid"]
        self.stop_id_ext: Union[str, None] = data.get("stopExtId")
        self.stop: Union[Stop, None] = (
            client.stop_by_id(self.stop_id) if retrieve_stops else None
        )
        self.time: datetime = datetime.strptime(
            f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M:%S"
        )
        self.time_real: datetime = (
            datetime.strptime(f"{data['rtDate']} {data['rtTime']}", "%Y-%m-%d %H:%M:%S")
            if data.get("rtTime") and data.get("rtDate")
            else None
        )
        self.reachable: bool = data["reachable"]
        self.origin: Union[str, None] = data.get("origin")

        if "Messages" in data:
            self.messages.extend(Message(message) for message in data["Messages"]["Message"])

    def __str__(self) -> str:
        return (
            f"{self.name} coming from {self.origin} at {self.time.time()} {self.date.date()}"
        )


class LineDeparture:
    def __init__(
        self,
        data: Mapping[str, Any],
        retrieve_stops: bool = False,
        retrieve_journey: bool = False,
        client: Union["pyrmv.Client", None] = None,
    ):
        if (retrieve_stops or retrieve_journey) and client is None:
            raise KeyError(
                "Stops/journey retrieval requested but client argument was not provided."
            )

        # Upgrade is temporarily used due to RMV API mismatch
        # self.journey = client.journey_detail(data["JourneyDetailRef"]["ref"])
        self.journey: Union[Journey, None] = (
            client.journey_detail(ref_upgrade(data["JourneyDetailRef"]["ref"]))
            if retrieve_journey
            else None
        )

        self.status: str = data["JourneyStatus"]
        self.messages: List[Message] = []
        self.name: str = data["name"]
        self.type: str = data["type"]
        self.stop_name: str = data["stop"]
        self.stop_id: str = data["stopid"]
        self.stop_id_ext: Union[str, None] = data.get("stopExtId")
        self.stop: Union[Stop, None] = (
            client.stop_by_id(self.stop_id) if retrieve_stops else None
        )
        self.time: datetime = datetime.strptime(
            f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M:%S"
        )
        self.time_real: datetime = (
            datetime.strptime(f"{data['rtDate']} {data['rtTime']}", "%Y-%m-%d %H:%M:%S")
            if data.get("rtTime") and data.get("rtDate")
            else None
        )
        self.reachable: bool = data["reachable"]
        self.direction: Union[str, None] = data.get("direction")
        self.direction_flag: Union[str, None] = data.get("directionFlag")

        if "Messages" in data:
            self.messages.extend(Message(message) for message in data["Messages"]["Message"])

    def __str__(self) -> str:
        return (
            f"{self.name} heading {self.direction} at {self.time.time()} {self.date.date()}"
        )


class BoardArrival(list):
    def __init__(
        self,
        data: Mapping[str, Any],
        retrieve_stops: bool = False,
        retrieve_journey: bool = False,
        client: Union["pyrmv.Client", None] = None,
    ):
        """Arrival board representation

        ### Args:
            * data (`Mapping[str, Any]`): Dictionary from RMV to be parsed.
            * retrieve_stops (`bool`, *optional*): Retrieve `Stop` objects for each line of the board. Defaults to `False`.
            * retrieve_journey (`bool`, *optional*): Retrieve `Journey` object for each line of the board. Defaults to `False`.
            * client (`Union[Client, None]`, *optional*): Client to be used if `retrieve_stops` or `retrieve_journey` are set to `True`. Defaults to `None`.
        """
        super().__init__([])

        if "Arrival" not in data:
            return

        for line in data["Arrival"]:
            self.append(
                LineArrival(
                    line,
                    retrieve_stops=retrieve_stops,
                    retrieve_journey=retrieve_journey,
                    client=client,
                )
            )

    def __str__(self) -> str:
        return "Arrival board\n" + "\n".join([str(line) for line in self])


class BoardDeparture(list):
    def __init__(
        self,
        data: Mapping[str, Any],
        retrieve_stops: bool = False,
        retrieve_journey: bool = False,
        client: Union["pyrmv.Client", None] = None,
    ):
        """Departure board representation

        ### Args:
            * data (`Mapping[str, Any]`): Dictionary from RMV to be parsed.
            * retrieve_stops (`bool`, *optional*): Retrieve `Stop` objects for each line of the board. Defaults to `False`.
            * retrieve_journey (`bool`, *optional*): Retrieve `Journey` object for each line of the board. Defaults to `False`.
            * client (`Union[Client, None]`, *optional*): Client to be used if `retrieve_stops` or `retrieve_journey` are set to `True`. Defaults to `None`.
        """
        super().__init__([])

        if "Departure" not in data:
            return

        for line in data["Departure"]:
            self.append(
                LineDeparture(
                    line,
                    retrieve_stops=retrieve_stops,
                    retrieve_journey=retrieve_journey,
                    client=client,
                )
            )

    def __str__(self) -> str:
        return "Departure board\n" + "\n".join([str(line) for line in self])
