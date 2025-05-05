from datetime import datetime, timedelta
from typing import Any, List, Mapping, Union

from isodate import Duration, parse_duration

from ..classes.stop import Stop


class Url:
    """Traffic message channel url object."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.name: str = data["name"]
        self.url: str = data["url"]

    def __str__(self) -> str:
        return f"{self.name}: {self.url}"


class Channel:
    """Traffic message channel object."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.name: str = data["name"]
        url = []
        url.extend(Url(link) for link in url)
        self.url: List[Url] = url
        self.time_start: Union[datetime, None] = (
            None
            if "validFromDate" not in data
            else datetime.strptime(
                f"{data['validFromDate']} {data['validFromTime']}", "%Y-%m-%d %H:%M:%S"
            )
        )
        self.time_end: Union[datetime, None] = (
            None
            if "validToDate" not in data
            else datetime.strptime(
                f"{data['validToDate']} {data['validToTime']}", "%Y-%m-%d %H:%M:%S"
            )
        )

    def __str__(self) -> str:
        return f"{self.name}: from {self.time_start} until {self.time_end}"


class Message:
    """Traffic message object."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.affected_stops: List[Stop] = []
        self.valid_from_stop: Union[Stop, None] = (
            None if "validFromStop" not in data else Stop(data["validFromStop"])
        )
        self.valid_to_stop: Union[Stop, None] = (
            None if "validToStop" not in data else Stop(data["validToStop"])
        )
        self.channels: Union[Channel, None] = []
        self.channels.extend(Channel(channel) for channel in data["channel"])
        self.id: str = data["id"]
        self.active: bool = data["act"]
        self.head: str = "" if "head" not in data else data["head"]
        self.lead: str = "" if "lead" not in data else data["lead"]
        self.text: str = "" if "text" not in data else data["text"]
        self.company: Union[str, None] = data.get("company")
        self.category: Union[str, None] = data.get("category")
        self.priority: Union[int, None] = data.get("priority")
        self.products: int = data["products"]
        self.icon: Mapping[str, Any] = data["icon"]
        self.time_start: Union[datetime, None] = (
            None
            if "validFromDate" not in data or "validFromTime" not in data
            else datetime.strptime(
                f"{data['validFromDate']} {data['validFromTime']}", "%Y-%m-%d %H:%M:%S"
            )
        )
        self.time_end: Union[datetime, None] = (
            None
            if "validToDate" not in data or "validToTime" not in data
            else datetime.strptime(
                f"{data['validToDate']} {data['validToTime']}", "%Y-%m-%d %H:%M:%S"
            )
        )
        self.date_start_alt: Union[str, None] = (
            None if "altStart" not in data else data["altStart"]
        )
        self.date_end_alt: Union[str, None] = None if "altEnd" not in data else data["altEnd"]
        self.time_modified: Union[datetime, None] = (
            None
            if "modDate" not in data or "modTime" not in data
            else datetime.strptime(
                f"{data['modDate']} {data['modTime']}", "%Y-%m-%d %H:%M:%S"
            )
        )
        self.daily_start: Union[datetime, None] = (
            None
            if "dailyStartingAt" not in data
            else datetime.strptime(data["dailyStartingAt"], "%H:%M:%S")
        )
        self.daily_duration: Union[Duration, timedelta] = parse_duration(
            data["dailyDuration"]
        )
        self.base_type: Union[str, None] = data.get("baseType")

        if "affectedStops" in data:
            self.affected_stops.extend(
                Stop(stop) for stop in data["affectedStops"]["StopLocation"]
            )

    def __str__(self) -> str:
        return f"{self.base_type} message with priority {self.products} valid from {self.time_start} until {self.time_end}: {self.head} - {self.lead}"
