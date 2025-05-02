from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImpressoNamedEntityRecognitionEntityConfidence")


@_attrs_define
class ImpressoNamedEntityRecognitionEntityConfidence:
    """
    Attributes:
        ner (Union[Unset, float]): Confidence score for the named entity recognition
        nel (Union[Unset, float]): Confidence score for the named entity linking
    """

    ner: Union[Unset, float] = UNSET
    nel: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        ner = self.ner

        nel = self.nel

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if ner is not UNSET:
            field_dict["ner"] = ner
        if nel is not UNSET:
            field_dict["nel"] = nel

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ner = d.pop("ner", UNSET)

        nel = d.pop("nel", UNSET)

        impresso_named_entity_recognition_entity_confidence = cls(
            ner=ner,
            nel=nel,
        )

        return impresso_named_entity_recognition_entity_confidence
