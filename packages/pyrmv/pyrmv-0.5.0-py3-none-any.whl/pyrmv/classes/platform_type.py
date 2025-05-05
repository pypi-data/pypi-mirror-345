from typing import Any, Mapping, Union

from ..enums.platform_type_type import PlatformTypeType


class PlatformType:
    """Platform information."""

    def __init__(self, data: Mapping[str, Any]):
        self.type: PlatformTypeType = (
            PlatformTypeType.U if "type" not in data else PlatformTypeType(data.get("type"))
        )
        self.text: Union[str, None] = data.get("text")
        self.hidden: bool = bool(data.get("hidden"))
        self.lon: float = data["lon"]
        self.lat: float = data["lat"]
        self.alt: int = data["alt"]
