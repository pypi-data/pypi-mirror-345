from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="MediaSourcePropertiesItem")


@_attrs_define
class MediaSourcePropertiesItem:
    """
    Attributes:
        id (str): The unique identifier of the property.
        label (str): The name of the property.
        value (str): The value of the property.
    """

    id: str
    label: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        label = self.label

        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "label": label,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        label = d.pop("label")

        value = d.pop("value")

        media_source_properties_item = cls(
            id=id,
            label=label,
            value=value,
        )

        return media_source_properties_item
