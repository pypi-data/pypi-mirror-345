from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Error")


@_attrs_define
class Error:
    """Error response that follows https://datatracker.ietf.org/doc/html/rfc7807#section-3.1

    Attributes:
        type (str): A URI reference [RFC3986] that identifies the problem type.
        title (str): A short, human-readable summary of the problem type.
        status (int): The HTTP status code ([RFC7231], Section 6)
        detail (Union[Unset, str]): A human-readable explanation specific to this occurrence of the problem.
    """

    type: str
    title: str
    status: int
    detail: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type

        title = self.title

        status = self.status

        detail = self.detail

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "title": title,
                "status": status,
            }
        )
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type")

        title = d.pop("title")

        status = d.pop("status")

        detail = d.pop("detail", UNSET)

        error = cls(
            type=type,
            title=title,
            status=status,
            detail=detail,
        )

        error.additional_properties = d
        return error

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
