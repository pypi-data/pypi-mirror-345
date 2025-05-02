from enum import Enum
from typing import Literal


class FilterPrecision(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    PARTIAL = "partial"
    SOFT = "soft"

    def __str__(self) -> str:
        return str(self.value)


FilterPrecisionLiteral = Literal[
    "exact",
    "fuzzy",
    "partial",
    "soft",
]
