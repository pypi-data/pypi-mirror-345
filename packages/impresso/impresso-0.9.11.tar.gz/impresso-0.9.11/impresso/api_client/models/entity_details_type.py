from enum import Enum
from typing import Literal


class EntityDetailsType(str, Enum):
    LOCATION = "location"
    PERSON = "person"

    def __str__(self) -> str:
        return str(self.value)


EntityDetailsTypeLiteral = Literal[
    "location",
    "person",
]
