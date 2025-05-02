from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.content_item import ContentItem
    from ..models.search_base_find_response_pagination import SearchBaseFindResponsePagination


T = TypeVar("T", bound="SearchBaseFindResponse")


@_attrs_define
class SearchBaseFindResponse:
    """
    Attributes:
        data (List['ContentItem']):
        pagination (SearchBaseFindResponsePagination):
    """

    data: List["ContentItem"]
    pagination: "SearchBaseFindResponsePagination"

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
        from ..models.content_item import ContentItem
        from ..models.search_base_find_response_pagination import SearchBaseFindResponsePagination

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ContentItem.from_dict(data_item_data)

            data.append(data_item)

        pagination = SearchBaseFindResponsePagination.from_dict(d.pop("pagination"))

        search_base_find_response = cls(
            data=data,
            pagination=pagination,
        )

        return search_base_find_response
