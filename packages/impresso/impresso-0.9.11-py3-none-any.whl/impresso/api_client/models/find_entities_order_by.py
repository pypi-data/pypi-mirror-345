from enum import Enum
from typing import Literal


class FindEntitiesOrderBy(str, Enum):
    COUNT = "count"
    COUNT_MENTIONS = "count-mentions"
    NAME = "name"
    RELEVANCE = "relevance"
    VALUE_1 = "-relevance"
    VALUE_3 = "-name"
    VALUE_5 = "-count"
    VALUE_7 = "-count-mentions"

    def __str__(self) -> str:
        return str(self.value)


FindEntitiesOrderByLiteral = Literal[
    "count",
    "count-mentions",
    "name",
    "relevance",
    "-relevance",
    "-name",
    "-count",
    "-count-mentions",
]
"""Specifies the sorting order for entity results using string literals.

This type defines the valid string values that can be used to specify the
field by which entity results should be ordered, and whether the order
should be ascending or descending.

Possible ordering fields:
- `count`: Order by the total number of documents the entity appears in.
- `count-mentions`: Order by the total number of times the entity is mentioned across all documents.
- `name`: Order alphabetically by entity name.
- `relevance`: Order by relevance score (specific to the query context, often the default).

Ascending order is the default (e.g., `"name"` sorts A-Z).
Descending order is indicated by a preceding hyphen (e.g., `"-count"`
sorts from the highest count to the lowest).

Usage Example:
    ```python
    # Assume 'client' is an initialized API client instance
    # Example: Find entities and sort by the number of mentions (descending)
    entities_by_mentions = client.find_entities(query="some query", order_by="-count-mentions")

    # Example: Find entities and sort alphabetically by name (ascending)
    entities_by_name = client.find_entities(query="another query", order_by="name")
    ```

See Also:
    `FindEntitiesOrderBy`: An enum representation of these literal values.
"""
