from enum import Enum
from typing import Literal


class FilterOp(str, Enum):
    AND = "AND"
    OR = "OR"

    def __str__(self) -> str:
        return str(self.value)


FilterOpLiteral = Literal[
    "AND",
    "OR",
]
