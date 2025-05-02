from enum import Enum
from typing import Literal


class ImpressoNamedEntityRecognitionRequestMethod(str, Enum):
    NEL = "nel"
    NER = "ner"
    NER_NEL = "ner-nel"

    def __str__(self) -> str:
        return str(self.value)


ImpressoNamedEntityRecognitionRequestMethodLiteral = Literal[
    "nel",
    "ner",
    "ner-nel",
]
