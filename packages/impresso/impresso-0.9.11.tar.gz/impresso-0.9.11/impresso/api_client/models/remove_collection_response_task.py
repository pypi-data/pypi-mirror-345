from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoveCollectionResponseTask")


@_attrs_define
class RemoveCollectionResponseTask:
    """Deletion task details

    Attributes:
        task_id (Union[Unset, str]): The ID of the task
        creation_date (Union[Unset, str]): When task was created
    """

    task_id: Union[Unset, str] = UNSET
    creation_date: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        task_id = self.task_id

        creation_date = self.creation_date

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if task_id is not UNSET:
            field_dict["task_id"] = task_id
        if creation_date is not UNSET:
            field_dict["creationDate"] = creation_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        task_id = d.pop("task_id", UNSET)

        creation_date = d.pop("creationDate", UNSET)

        remove_collection_response_task = cls(
            task_id=task_id,
            creation_date=creation_date,
        )

        return remove_collection_response_task
