from enum import Enum
from typing import Literal


class RemoveCollectionResponseParamsStatus(str, Enum):
    DEL = "DEL"

    def __str__(self) -> str:
        return str(self.value)


RemoveCollectionResponseParamsStatusLiteral = Literal["DEL",]
