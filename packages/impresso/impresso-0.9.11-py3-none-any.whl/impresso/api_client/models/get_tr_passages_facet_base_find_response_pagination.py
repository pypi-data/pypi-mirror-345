from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetTrPassagesFacetBaseFindResponsePagination")


@_attrs_define
class GetTrPassagesFacetBaseFindResponsePagination:
    """
    Attributes:
        total (int): The total number of items matching the query
        limit (int): The number of items returned in this response
        offset (int): Starting index of the items subset returned in this response
    """

    total: int
    limit: int
    offset: int

    def to_dict(self) -> Dict[str, Any]:
        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_tr_passages_facet_base_find_response_pagination = cls(
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_tr_passages_facet_base_find_response_pagination
