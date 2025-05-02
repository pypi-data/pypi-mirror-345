from enum import Enum
from typing import Literal


class FindMediaSourcesOrderBy(str, Enum):
    COUNTISSUES = "countIssues"
    FIRSTISSUE = "firstIssue"
    LASTISSUE = "lastIssue"
    NAME = "name"
    VALUE_1 = "-name"
    VALUE_3 = "-firstIssue"
    VALUE_5 = "-lastIssue"
    VALUE_7 = "-countIssues"

    def __str__(self) -> str:
        return str(self.value)


FindMediaSourcesOrderByLiteral = Literal[
    "countIssues",
    "firstIssue",
    "lastIssue",
    "name",
    "-name",
    "-firstIssue",
    "-lastIssue",
    "-countIssues",
]
"""Specifies the sorting order for media source results using string literals.

This type defines the valid string values that can be used to specify the
field by which media source results should be ordered, and whether the order
should be ascending or descending.

Possible ordering fields:
- `countIssues`: Order by the total number of issues available for the media source.
- `firstIssue`: Order by the publication date of the earliest available issue.
- `lastIssue`: Order by the publication date of the latest available issue.
- `name`: Order alphabetically by the media source's name.

Ascending order is the default (e.g., `"name"` sorts A-Z, `"firstIssue"` sorts oldest to newest).
Descending order is indicated by a preceding hyphen (e.g., `"-countIssues"`
sorts from the highest count to the lowest, `"-lastIssue"` sorts newest to oldest).

Usage Example:
    ```python
    # Assume 'client' is an initialized API client instance
    # Example: Find media sources and sort by the number of issues (descending)
    sources_by_issue_count = client.find_media_sources(order_by="-countIssues")

    # Example: Find media sources and sort alphabetically by name (ascending)
    sources_by_name = client.find_media_sources(order_by="name")

    # Example: Find media sources and sort by the date of the last issue (newest first)
    sources_by_last_issue = client.find_media_sources(order_by="-lastIssue")
    ```

See Also:
    `FindMediaSourcesOrderBy`: An enum representation of these literal values.
"""
