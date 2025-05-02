from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.remove_collection_response_params import RemoveCollectionResponseParams
    from ..models.remove_collection_response_task import RemoveCollectionResponseTask


T = TypeVar("T", bound="RemoveCollectionResponse")


@_attrs_define
class RemoveCollectionResponse:
    """Remove collection response

    Attributes:
        params (RemoveCollectionResponseParams):
        task (RemoveCollectionResponseTask): Deletion task details
    """

    params: "RemoveCollectionResponseParams"
    task: "RemoveCollectionResponseTask"

    def to_dict(self) -> Dict[str, Any]:
        params = self.params.to_dict()

        task = self.task.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "params": params,
                "task": task,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.remove_collection_response_params import RemoveCollectionResponseParams
        from ..models.remove_collection_response_task import RemoveCollectionResponseTask

        d = src_dict.copy()
        params = RemoveCollectionResponseParams.from_dict(d.pop("params"))

        task = RemoveCollectionResponseTask.from_dict(d.pop("task"))

        remove_collection_response = cls(
            params=params,
            task=task,
        )

        return remove_collection_response
