from enum import Enum
from typing import Literal


class NewCollectionRequestAccessLevel(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)


NewCollectionRequestAccessLevelLiteral = Literal[
    "private",
    "public",
]
