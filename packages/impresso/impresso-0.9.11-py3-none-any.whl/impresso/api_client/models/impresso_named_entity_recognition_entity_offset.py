from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ImpressoNamedEntityRecognitionEntityOffset")


@_attrs_define
class ImpressoNamedEntityRecognitionEntityOffset:
    """
    Attributes:
        start (int): Start offset of the entity in the text
        end (int): End offset of the entity in the text
    """

    start: int
    end: int

    def to_dict(self) -> Dict[str, Any]:
        start = self.start

        end = self.end

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "start": start,
                "end": end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start = d.pop("start")

        end = d.pop("end")

        impresso_named_entity_recognition_entity_offset = cls(
            start=start,
            end=end,
        )

        return impresso_named_entity_recognition_entity_offset
