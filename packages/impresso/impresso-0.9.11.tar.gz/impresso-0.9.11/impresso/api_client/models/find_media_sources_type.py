from enum import Enum
from typing import Literal


class FindMediaSourcesType(str, Enum):
    NEWSPAPER = "newspaper"

    def __str__(self) -> str:
        return str(self.value)


FindMediaSourcesTypeLiteral = Literal["newspaper",]
