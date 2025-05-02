from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.find_media_sources_base_find_response_pagination import FindMediaSourcesBaseFindResponsePagination
    from ..models.media_source import MediaSource


T = TypeVar("T", bound="FindMediaSourcesBaseFindResponse")


@_attrs_define
class FindMediaSourcesBaseFindResponse:
    """
    Attributes:
        data (List['MediaSource']):
        pagination (FindMediaSourcesBaseFindResponsePagination):
    """

    data: List["MediaSource"]
    pagination: "FindMediaSourcesBaseFindResponsePagination"

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
        from ..models.find_media_sources_base_find_response_pagination import FindMediaSourcesBaseFindResponsePagination
        from ..models.media_source import MediaSource

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = MediaSource.from_dict(data_item_data)

            data.append(data_item)

        pagination = FindMediaSourcesBaseFindResponsePagination.from_dict(d.pop("pagination"))

        find_media_sources_base_find_response = cls(
            data=data,
            pagination=pagination,
        )

        return find_media_sources_base_find_response
