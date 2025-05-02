from enum import Enum
from typing import Literal


class GetTrClustersFacetOrderBy(str, Enum):
    COUNT = "count"
    VALUE = "value"
    VALUE_0 = "-count"
    VALUE_2 = "-value"

    def __str__(self) -> str:
        return str(self.value)


GetTrClustersFacetOrderByLiteral = Literal[
    "count",
    "value",
    "-count",
    "-value",
]
