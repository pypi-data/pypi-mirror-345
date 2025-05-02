from enum import Enum
from typing import Literal


class FilterContext(str, Enum):
    EXCLUDE = "exclude"
    INCLUDE = "include"

    def __str__(self) -> str:
        return str(self.value)


FilterContextLiteral = Literal[
    "exclude",
    "include",
]
