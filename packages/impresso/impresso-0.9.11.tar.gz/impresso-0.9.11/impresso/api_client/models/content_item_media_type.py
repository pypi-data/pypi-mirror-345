from enum import Enum
from typing import Literal


class ContentItemMediaType(str, Enum):
    NEWSPAPER = "newspaper"

    def __str__(self) -> str:
        return str(self.value)


ContentItemMediaTypeLiteral = Literal["newspaper",]
