from enum import Enum
from typing import Literal


class GetTrPassagesFacetId(str, Enum):
    COLLECTION = "collection"
    CONNECTEDCLUSTERS = "connectedClusters"
    COUNTRY = "country"
    DATERANGE = "daterange"
    LANGUAGE = "language"
    LOCATION = "location"
    NAG = "nag"
    NEWSPAPER = "newspaper"
    PERSON = "person"
    TEXTREUSECLUSTER = "textReuseCluster"
    TEXTREUSECLUSTERDAYDELTA = "textReuseClusterDayDelta"
    TEXTREUSECLUSTERLEXICALOVERLAP = "textReuseClusterLexicalOverlap"
    TEXTREUSECLUSTERSIZE = "textReuseClusterSize"
    TOPIC = "topic"
    TYPE = "type"
    YEAR = "year"
    YEARMONTH = "yearmonth"

    def __str__(self) -> str:
        return str(self.value)


GetTrPassagesFacetIdLiteral = Literal[
    "collection",
    "connectedClusters",
    "country",
    "daterange",
    "language",
    "location",
    "nag",
    "newspaper",
    "person",
    "textReuseCluster",
    "textReuseClusterDayDelta",
    "textReuseClusterLexicalOverlap",
    "textReuseClusterSize",
    "topic",
    "type",
    "year",
    "yearmonth",
]
