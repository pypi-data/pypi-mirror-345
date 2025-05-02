from enum import Enum
from typing import Literal


class FindCollectionsOrderBy(str, Enum):
    DATE = "date"
    SIZE = "size"
    VALUE_0 = "-date"
    VALUE_2 = "-size"

    def __str__(self) -> str:
        return str(self.value)


FindCollectionsOrderByLiteral = Literal[
    "date",
    "size",
    "-date",
    "-size",
]
