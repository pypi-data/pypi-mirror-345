import datetime
from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

T = TypeVar("T", bound="TextReuseClusterTimeCoverage")


@_attrs_define
class TextReuseClusterTimeCoverage:
    """Time coverage of the cluster.

    Attributes:
        start_date (datetime.date): Publication date of the earliest content item in the cluster.
        end_date (datetime.date): Publication date of the latest content item in the cluster.
    """

    start_date: datetime.date
    end_date: datetime.date

    def to_dict(self) -> Dict[str, Any]:
        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "startDate": start_date,
                "endDate": end_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start_date = isoparse(d.pop("startDate")).date()

        end_date = isoparse(d.pop("endDate")).date()

        text_reuse_cluster_time_coverage = cls(
            start_date=start_date,
            end_date=end_date,
        )

        return text_reuse_cluster_time_coverage
