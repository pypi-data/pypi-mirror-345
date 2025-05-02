from enum import Enum
from typing import Literal


class MediaSourceType(str, Enum):
    NEWSPAPER = "newspaper"

    def __str__(self) -> str:
        return str(self.value)


MediaSourceTypeLiteral = Literal["newspaper",]
