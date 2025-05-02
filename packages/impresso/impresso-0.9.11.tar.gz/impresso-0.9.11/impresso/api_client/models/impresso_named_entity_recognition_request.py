from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.impresso_named_entity_recognition_request_method import ImpressoNamedEntityRecognitionRequestMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImpressoNamedEntityRecognitionRequest")


@_attrs_define
class ImpressoNamedEntityRecognitionRequest:
    """Request body for the Impresso NER endpoint

    Attributes:
        text (str): Text to be processed for named entity recognition
        method (Union[Unset, ImpressoNamedEntityRecognitionRequestMethod]): NER method to be used: `ner` (default),
            `ner-nel` (named entity recognition with named entity linking) and `nel` (linking only - enclose entities in
            [START] [END] tags). Default: ImpressoNamedEntityRecognitionRequestMethod.NER.
    """

    text: str
    method: Union[Unset, ImpressoNamedEntityRecognitionRequestMethod] = ImpressoNamedEntityRecognitionRequestMethod.NER

    def to_dict(self) -> Dict[str, Any]:
        text = self.text

        method: Union[Unset, str] = UNSET
        if not isinstance(self.method, Unset):
            method = self.method.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "text": text,
            }
        )
        if method is not UNSET:
            field_dict["method"] = method

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        text = d.pop("text")

        _method = d.pop("method", UNSET)
        method: Union[Unset, ImpressoNamedEntityRecognitionRequestMethod]
        if isinstance(_method, Unset):
            method = UNSET
        else:
            method = ImpressoNamedEntityRecognitionRequestMethod(_method)

        impresso_named_entity_recognition_request = cls(
            text=text,
            method=method,
        )

        return impresso_named_entity_recognition_request
