from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CollectableItemsUpdatedResponse")


@_attrs_define
class CollectableItemsUpdatedResponse:
    """Request to update collectible items in a collection

    Attributes:
        total_added (int): Total number of items added to the collection
        total_removed (int): Total number of items removed from the collection
    """

    total_added: int
    total_removed: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total_added = self.total_added

        total_removed = self.total_removed

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "totalAdded": total_added,
                "totalRemoved": total_removed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total_added = d.pop("totalAdded")

        total_removed = d.pop("totalRemoved")

        collectable_items_updated_response = cls(
            total_added=total_added,
            total_removed=total_removed,
        )

        collectable_items_updated_response.additional_properties = d
        return collectable_items_updated_response

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
