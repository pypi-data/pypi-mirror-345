from enum import Enum
from typing import Literal


class CollectionAccessLevel(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)


CollectionAccessLevelLiteral = Literal[
    "private",
    "public",
]
