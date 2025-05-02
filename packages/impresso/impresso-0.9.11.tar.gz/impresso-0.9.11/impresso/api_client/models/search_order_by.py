from enum import Enum
from typing import Literal


class SearchOrderBy(str, Enum):
    DATE = "date"
    ID = "id"
    RELEVANCE = "relevance"
    VALUE_0 = "-date"  # Descending date
    VALUE_2 = "-relevance"  # Descending relevance (default search behavior)
    VALUE_5 = "-id"  # Descending ID

    def __str__(self) -> str:
        return str(self.value)


SearchOrderByLiteral = Literal[
    "date",
    "id",
    "relevance",
    "-date",
    "-relevance",
    "-id",
]
"""
Specifies the sorting order for search results using string literals.

This type defines the valid string values that can be used to specify the
field by which search results should be ordered, and whether the order
should be ascending or descending.

Ascending order is the default (e.g., `"date"` sorts from oldest to newest).
Descending order is indicated by a preceding hyphen (e.g., `"-date"`
sorts from newest to oldest).

Usage Example:
    ```python
    # Example: Search for articles and sort by relevance (descending)
    # Note: "-relevance" is often the default sorting for search APIs
    results = client.search(query="example query", order_by="-relevance")

    # Example: Search and sort by date (ascending)
    results_by_date = client.search(query="another query", order_by="date")

    # Example: Search and sort by date (descending)
    results_by_date_desc = client.search(query="yet another query", order_by="-date")
    ```

See Also:
    `SearchOrderBy`: An enum representation of these literal values.
"""
