from enum import Enum
from typing import Literal


class FindTextReuseClustersOrderBy(str, Enum):
    PASSAGES_COUNT = "passages-count"
    VALUE_1 = "-passages-count"

    def __str__(self) -> str:
        return str(self.value)


FindTextReuseClustersOrderByLiteral = Literal[
    "passages-count",
    "-passages-count",
]
