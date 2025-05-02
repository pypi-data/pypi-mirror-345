from enum import Enum
from typing import Literal


class WikidataPersonType(str, Enum):
    HUMAN = "human"

    def __str__(self) -> str:
        return str(self.value)


WikidataPersonTypeLiteral = Literal["human",]
