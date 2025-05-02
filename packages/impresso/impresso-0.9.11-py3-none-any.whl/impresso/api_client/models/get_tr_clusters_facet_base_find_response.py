from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_tr_clusters_facet_base_find_response_pagination import (
        GetTrClustersFacetBaseFindResponsePagination,
    )
    from ..models.search_facet_bucket import SearchFacetBucket


T = TypeVar("T", bound="GetTrClustersFacetBaseFindResponse")


@_attrs_define
class GetTrClustersFacetBaseFindResponse:
    """
    Attributes:
        data (List['SearchFacetBucket']):
        pagination (GetTrClustersFacetBaseFindResponsePagination):
    """

    data: List["SearchFacetBucket"]
    pagination: "GetTrClustersFacetBaseFindResponsePagination"

    def to_dict(self) -> Dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_tr_clusters_facet_base_find_response_pagination import (
            GetTrClustersFacetBaseFindResponsePagination,
        )
        from ..models.search_facet_bucket import SearchFacetBucket

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = SearchFacetBucket.from_dict(data_item_data)

            data.append(data_item)

        pagination = GetTrClustersFacetBaseFindResponsePagination.from_dict(d.pop("pagination"))

        get_tr_clusters_facet_base_find_response = cls(
            data=data,
            pagination=pagination,
        )

        return get_tr_clusters_facet_base_find_response
