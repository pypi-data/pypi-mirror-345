from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.remove_collection_response_params_status import RemoveCollectionResponseParamsStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoveCollectionResponseParams")


@_attrs_define
class RemoveCollectionResponseParams:
    """
    Attributes:
        id (Union[Unset, str]): The collection id
        status (Union[Unset, RemoveCollectionResponseParamsStatus]): The status of the operation
    """

    id: Union[Unset, str] = UNSET
    status: Union[Unset, RemoveCollectionResponseParamsStatus] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, RemoveCollectionResponseParamsStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = RemoveCollectionResponseParamsStatus(_status)

        remove_collection_response_params = cls(
            id=id,
            status=status,
        )

        return remove_collection_response_params
