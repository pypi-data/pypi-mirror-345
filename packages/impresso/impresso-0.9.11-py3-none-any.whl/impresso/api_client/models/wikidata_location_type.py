from enum import Enum
from typing import Literal


class WikidataLocationType(str, Enum):
    LOCATION = "location"

    def __str__(self) -> str:
        return str(self.value)


WikidataLocationTypeLiteral = Literal["location",]
