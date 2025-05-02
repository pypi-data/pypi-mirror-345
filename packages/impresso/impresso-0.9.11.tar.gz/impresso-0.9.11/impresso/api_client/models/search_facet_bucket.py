from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchFacetBucket")


@_attrs_define
class SearchFacetBucket:
    """Facet bucket

    Attributes:
        count (int): Number of items in the bucket
        value (Union[float, int, str]): Value that represents the bucket.
        label (Union[Unset, str]): Label of the value, if relevant.
    """

    count: int
    value: Union[float, int, str]
    label: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        count = self.count

        value: Union[float, int, str]
        value = self.value

        label = self.label

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "count": count,
                "value": value,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        count = d.pop("count")

        def _parse_value(data: object) -> Union[float, int, str]:
            return cast(Union[float, int, str], data)

        value = _parse_value(d.pop("value"))

        label = d.pop("label", UNSET)

        search_facet_bucket = cls(
            count=count,
            value=value,
            label=label,
        )

        return search_facet_bucket
