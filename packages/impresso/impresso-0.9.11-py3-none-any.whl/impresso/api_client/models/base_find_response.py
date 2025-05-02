from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.base_find_response_pagination import BaseFindResponsePagination


T = TypeVar("T", bound="BaseFindResponse")


@_attrs_define
class BaseFindResponse:
    """
    Attributes:
        data (List[Any]):
        pagination (BaseFindResponsePagination):
    """

    data: List[Any]
    pagination: "BaseFindResponsePagination"

    def to_dict(self) -> Dict[str, Any]:
        data = self.data

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
        from ..models.base_find_response_pagination import BaseFindResponsePagination

        d = src_dict.copy()
        data = cast(List[Any], d.pop("data"))

        pagination = BaseFindResponsePagination.from_dict(d.pop("pagination"))

        base_find_response = cls(
            data=data,
            pagination=pagination,
        )

        return base_find_response
